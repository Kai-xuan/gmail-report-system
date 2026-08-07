"""
email_analyzer.py - AI 郵件分析模組
使用 Claude API 對每封郵件進行：
  1. 垃圾郵件過濾
  2. 重要程度評分（high / medium / low）
  3. 一句話摘要
"""

import json
import time
import anthropic
from config_loader import load_config


def analyze_batch(emails: list, config: dict) -> list:
    """
    批次分析郵件清單。
    為了節省 API 費用，先做本地規則過濾，再送給 AI 分析。

    Args:
        emails: 郵件清單（來自 email_fetcher）
        config: config.yaml 設定

    Returns:
        加入 AI 分析結果的郵件清單
    """
    client = anthropic.Anthropic()
    spam_keywords = config.get('spam_keywords', [])
    results = []

    print(f"\n🤖 開始 AI 分析，共 {len(emails)} 封郵件...")

    for i, mail in enumerate(emails):
        # ── 第一關：本地關鍵字過濾（免費，速度快）─────────────────
        subject_lower = mail['subject'].lower()
        sender_lower = mail['from'].lower()
        snippet_lower = mail['snippet'].lower()
        combined = f"{subject_lower} {sender_lower} {snippet_lower}"

        is_local_spam = any(kw.lower() in combined for kw in spam_keywords)

        if is_local_spam:
            mail['is_spam'] = True
            mail['importance'] = 'low'
            mail['ai_summary'] = '（本地規則判定為垃圾郵件）'
            results.append(mail)
            continue

        # ── 第二關：Claude AI 深度分析 ────────────────────────────
        try:
            prompt = f"""你是一個企業郵件助理。請分析以下郵件，回傳 JSON 格式（不要加任何說明文字）：

寄件人：{mail['from']}
標題：{mail['subject']}
內容：{mail['snippet']}

請回傳以下格式，不要加 markdown backtick：
{{
  "is_spam": true 或 false,
  "importance": "high" 或 "medium" 或 "low",
  "ai_summary": "一句話中文摘要（20字以內）",
  "reason": "判斷理由（10字以內）"
}}

判斷標準：
- is_spam: 廣告、退訂、促銷 → true；真人寄送的業務/工作信 → false
- high: 需要當天回覆、客戶投訴、重要合約、緊急事項
- medium: 一般業務聯繫、會議通知、有需要但不緊急
- low: 系統通知、收據、已讀無需回覆"""

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",  # 用最便宜的 Haiku 做分類
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            raw = response.content[0].text.strip()
            # 移除可能的 markdown backtick
            raw = raw.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(raw)

            mail['is_spam'] = analysis.get('is_spam', False)
            mail['importance'] = analysis.get('importance', 'low')
            mail['ai_summary'] = analysis.get('ai_summary', '')
            mail['ai_reason'] = analysis.get('reason', '')

        except json.JSONDecodeError:
            # AI 回傳格式異常，保守處理
            mail['is_spam'] = False
            mail['importance'] = 'medium'
            mail['ai_summary'] = mail['snippet'][:50]
            mail['ai_reason'] = '解析失敗'

        except Exception as e:
            print(f"   ⚠️ 分析郵件失敗（{mail['subject'][:30]}）：{e}")
            mail['is_spam'] = False
            mail['importance'] = 'low'
            mail['ai_summary'] = '（分析失敗）'
            mail['ai_reason'] = str(e)

        results.append(mail)

        # 每 10 封顯示進度
        if (i + 1) % 10 == 0:
            print(f"   已分析 {i + 1}/{len(emails)} 封...")

        # 避免觸發 API rate limit
        time.sleep(0.1)

    # ── 統計結果 ──────────────────────────────────────────────────
    total = len(results)
    spam_count = sum(1 for m in results if m.get('is_spam'))
    high_count = sum(1 for m in results if not m.get('is_spam') and m.get('importance') == 'high')
    medium_count = sum(1 for m in results if not m.get('is_spam') and m.get('importance') == 'medium')
    low_count = sum(1 for m in results if not m.get('is_spam') and m.get('importance') == 'low')

    print(f"\n✅ 分析完成！")
    print(f"   總計：{total} 封 | 垃圾：{spam_count} | 重要：{high_count} | 一般：{medium_count} | 低優先：{low_count}")

    return results
