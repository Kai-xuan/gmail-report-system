"""
report_sender.py - HTML 郵件報告發送模組
產生美觀的 HTML 摘要報告，並透過 SMTP 或 Gmail API 發送。
"""

import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config_loader import load_config


def generate_html_report(emails: list, days: int, config: dict) -> str:
    """產生 HTML 格式的郵件摘要報告。"""
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M')

    total = len(emails)
    spam_list = [m for m in emails if m.get('is_spam')]
    high_list = [m for m in emails if not m.get('is_spam') and m.get('importance') == 'high']
    medium_list = [m for m in emails if not m.get('is_spam') and m.get('importance') == 'medium']
    low_list = [m for m in emails if not m.get('is_spam') and m.get('importance') == 'low']

    def email_rows(mail_list, badge_color='#6b7280', badge_text='一般'):
        if not mail_list:
            return '<tr><td colspan="3" style="padding:12px;color:#9ca3af;text-align:center;">（無郵件）</td></tr>'
        rows = ''
        for m in mail_list[:20]:  # 最多顯示 20 封
            rows += f"""
            <tr style="border-bottom:1px solid #f3f4f6;">
              <td style="padding:10px 12px;font-size:13px;color:#374151;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                {m.get('subject','（無標題）')}
              </td>
              <td style="padding:10px 12px;font-size:12px;color:#6b7280;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                {m.get('from','').split('<')[0].strip()}
              </td>
              <td style="padding:10px 12px;font-size:12px;color:#374151;">
                {m.get('ai_summary','') or m.get('snippet','')[:60]}
              </td>
            </tr>"""
        return rows

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>郵件週報</title>
</head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:680px;margin:0 auto;padding:24px 16px;">

  <!-- 標頭 -->
  <div style="background:#1e40af;border-radius:12px;padding:28px 32px;margin-bottom:20px;color:#fff;">
    <h1 style="margin:0 0 6px;font-size:22px;font-weight:600;">📬 郵件摘要報告</h1>
    <p style="margin:0;font-size:14px;opacity:.8;">過去 {days} 天 · 產生時間：{now}</p>
  </div>

  <!-- 統計卡片 -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
    <div style="background:#fff;border-radius:10px;padding:18px 16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06);">
      <div style="font-size:26px;font-weight:700;color:#1e40af;">{total}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">總郵件</div>
    </div>
    <div style="background:#fff;border-radius:10px;padding:18px 16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06);">
      <div style="font-size:26px;font-weight:700;color:#dc2626;">{len(high_list)}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">重要郵件</div>
    </div>
    <div style="background:#fff;border-radius:10px;padding:18px 16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06);">
      <div style="font-size:26px;font-weight:700;color:#d97706;">{len(medium_list)}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">一般郵件</div>
    </div>
    <div style="background:#fff;border-radius:10px;padding:18px 16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06);">
      <div style="font-size:26px;font-weight:700;color:#6b7280;">{len(spam_list)}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">垃圾過濾</div>
    </div>
  </div>

  <!-- 重要郵件 -->
  <div style="background:#fff;border-radius:10px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);overflow:hidden;">
    <div style="padding:16px 20px;border-bottom:1px solid #f3f4f6;display:flex;align-items:center;gap:8px;">
      <span style="background:#fee2e2;color:#dc2626;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;">🔴 重要</span>
      <span style="font-size:14px;font-weight:600;color:#111827;">{len(high_list)} 封需要關注</span>
    </div>
    <table style="width:100%;border-collapse:collapse;">
      <thead>
        <tr style="background:#f9fafb;">
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;font-weight:500;">標題</th>
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;font-weight:500;">寄件人</th>
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;font-weight:500;">AI 摘要</th>
        </tr>
      </thead>
      <tbody>
        {email_rows(high_list, '#fee2e2', '重要')}
      </tbody>
    </table>
  </div>

  <!-- 一般郵件 -->
  <div style="background:#fff;border-radius:10px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);overflow:hidden;">
    <div style="padding:16px 20px;border-bottom:1px solid #f3f4f6;display:flex;align-items:center;gap:8px;">
      <span style="background:#fef3c7;color:#d97706;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;">🟡 一般</span>
      <span style="font-size:14px;font-weight:600;color:#111827;">{len(medium_list)} 封一般郵件</span>
    </div>
    <table style="width:100%;border-collapse:collapse;">
      <thead>
        <tr style="background:#f9fafb;">
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;font-weight:500;">標題</th>
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;font-weight:500;">寄件人</th>
          <th style="padding:10px 12px;text-align:left;font-size:12px;color:#6b7280;font-weight:500;">AI 摘要</th>
        </tr>
      </thead>
      <tbody>
        {email_rows(medium_list)}
      </tbody>
    </table>
  </div>

  <!-- 頁尾 -->
  <div style="text-align:center;padding:16px;color:#9ca3af;font-size:12px;">
    此報告由 Gmail Report System 自動產生 · 垃圾郵件已過濾（共 {len(spam_list)} 封）
  </div>
</div>
</body>
</html>"""
    return html


def send_report(emails: list, days: int, config: dict):
    """發送 HTML 郵件報告。"""
    report_config = config.get('report', {})
    recipients = report_config.get('recipients', [])

    if not recipients:
        print("⚠️ 沒有設定收件人，跳過發送。")
        return

    html_content = generate_html_report(emails, days, config)
    now_str = datetime.now().strftime('%Y/%m/%d')
    subject = f"📬 郵件週報 {now_str}｜{len([m for m in emails if m.get('importance')=='high'])} 封重要郵件"

    smtp_host = report_config.get('smtp_host', 'smtp.gmail.com')
    smtp_port = report_config.get('smtp_port', 587)
    smtp_user = report_config.get('smtp_user', '')
    smtp_pass = report_config.get('smtp_password', '')

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = ', '.join(recipients)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipients, msg.as_string())

        print(f"✅ 報告已發送至：{', '.join(recipients)}")

    except Exception as e:
        print(f"❌ 發送失敗：{e}")
        # 備案：儲存 HTML 到本地
        with open('latest_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("📄 已將報告儲存至 latest_report.html")
        raise
