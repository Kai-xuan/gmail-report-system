"""
app.py - Flask Web UI 後端
啟動後在瀏覽器開啟 http://localhost:5000 即可使用。
"""

import threading
import queue
import json
import os
import yaml
from flask import Flask, render_template, request, jsonify, Response
from config_loader import load_config

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 用於即時串流 log 給前端
log_queue = queue.Queue()
is_running = False
auth_status = {'state': 'idle', 'message': ''}  # idle / waiting / done / error


def stream_print(msg: str):
    """取代 print()，同時輸出到終端機和前端串流。"""
    print(msg)
    log_queue.put(msg)


# ── 路由 ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """取得當前設定。密碼欄位只回傳是否已設定，不回傳明文。"""
    try:
        config = load_config()
        # 密碼不傳到前端，只告知是否已設定
        smtp_pass = config.get('report', {}).get('smtp_password', '')
        config['report']['smtp_password_set'] = bool(smtp_pass)
        config['report']['smtp_password'] = ''  # 清空，不傳明文
        return jsonify({'success': True, 'config': config})
    except FileNotFoundError:
        return jsonify({'success': False, 'error': '找不到 config.yaml，請先建立設定檔。'})


@app.route('/api/config', methods=['POST'])
def save_config():
    """儲存設定。若密碼欄位為空，保留原本已存的密碼。"""
    try:
        data = request.json

        # 若使用者沒有填密碼，保留原本存的
        new_password = data.get('smtp_password', '').strip()
        if not new_password:
            try:
                old_config = load_config()
                new_password = old_config.get('report', {}).get('smtp_password', '')
            except Exception:
                new_password = ''

        config = {
            'schedule': {
                'interval': data.get('interval', 'weekly'),
                'cron': data.get('cron', '0 9 * * 1'),
                'query_days': int(data.get('query_days', 7)),
            },
            'report': {
                'recipients': [r.strip() for r in data.get('recipients', '').split('\n') if r.strip()],
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'smtp_user': data.get('smtp_user', ''),
                'smtp_password': new_password,
            },
            'spam_keywords': [k.strip() for k in data.get('spam_keywords', '').split('\n') if k.strip()],
            'anthropic': {
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': 200,
            }
        }

        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/status')
def get_status():
    """取得 Gmail 連線狀態。"""
    try:
        from gmail_auth import get_gmail_service
        service = get_gmail_service()
        profile = service.users().getProfile(userId='me').execute()
        return jsonify({
            'success': True,
            'email': profile['emailAddress'],
            'total': profile['messagesTotal'],
        })
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'credentials.json 不存在，請先設定 Google 憑證。'})
    except Exception as e:
        error_msg = str(e)
        # token 失效，需要重新授權
        if 'invalid_grant' in error_msg or 'Token has been expired' in error_msg:
            # 自動刪除失效的 token
            if os.path.exists('token.json'):
                os.remove('token.json')
            return jsonify({'success': False, 'error': 'token_expired'})
        return jsonify({'success': False, 'error': error_msg})


@app.route('/api/auth/start', methods=['POST'])
def auth_start():
    """在背景執行 Gmail OAuth2 授權流程，不需要命令提示字元。"""
    global auth_status

    if auth_status['state'] == 'waiting':
        return jsonify({'success': False, 'error': '授權流程進行中，請在瀏覽器完成授權。'})

    def _do_auth():
        global auth_status
        auth_status = {'state': 'waiting', 'message': '等待瀏覽器授權...'}
        try:
            # 刪除舊 token
            if os.path.exists('token.json'):
                os.remove('token.json')

            from gmail_auth import get_gmail_service
            service = get_gmail_service()
            profile = service.users().getProfile(userId='me').execute()
            auth_status = {
                'state': 'done',
                'message': f'授權成功！已連線到 {profile["emailAddress"]}'
            }
        except Exception as e:
            auth_status = {'state': 'error', 'message': f'授權失敗：{str(e)}'}

    thread = threading.Thread(target=_do_auth, daemon=True)
    thread.start()
    return jsonify({'success': True})


@app.route('/api/auth/status')
def auth_check():
    """前端輪詢，確認授權是否完成。"""
    return jsonify(auth_status)


@app.route('/api/run', methods=['POST'])
def run_report():
    """立即執行一次報告。"""
    global is_running

    if is_running:
        return jsonify({'success': False, 'error': '報告正在執行中，請稍候。'})

    def _run():
        global is_running
        is_running = True

        while not log_queue.empty():
            log_queue.get()

        try:
            import builtins
            original_print = builtins.print
            builtins.print = lambda *a, **k: stream_print(' '.join(str(x) for x in a))

            from email_fetcher import fetch_emails
            from email_analyzer import analyze_batch
            from gmail_actions import apply_labels
            from report_sender import send_report

            config = load_config()
            days = config.get('schedule', {}).get('query_days', 7)

            emails = fetch_emails(days=days)
            if emails:
                analyzed = analyze_batch(emails, config)
                apply_labels(analyzed)
                send_report(analyzed, days, config)
            else:
                stream_print('📭 這段時間沒有郵件。')

            builtins.print = original_print
            stream_print('__DONE__')

        except Exception as e:
            import traceback
            stream_print(f'❌ 執行失敗：{e}')
            stream_print(traceback.format_exc())
            stream_print('__DONE__')
        finally:
            is_running = False

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return jsonify({'success': True})


@app.route('/api/stream')
def stream():
    """SSE 串流，把執行 log 即時推送給前端。"""
    def generate():
        while True:
            try:
                msg = log_queue.get(timeout=30)
                yield f"data: {json.dumps({'log': msg})}\n\n"
                if msg == '__DONE__':
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'ping': True})}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


if __name__ == '__main__':
    print('\n🚀 Gmail 報告系統啟動中...')
    print('📌 請在瀏覽器開啟：http://localhost:5000\n')
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
