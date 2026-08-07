"""
email_fetcher.py - 郵件抓取模組
根據設定的回報週期，從 Gmail 拉取郵件並解析基本資訊。
"""

import base64
import email
from datetime import datetime, timedelta
from gmail_auth import get_gmail_service


def get_date_query(days: int) -> str:
    """產生 Gmail 搜尋日期條件，例如抓取過去 7 天。"""
    since_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
    return f'after:{since_date}'


def decode_body(payload) -> str:
    """解析郵件內文（支援 plain text 和 multipart）。"""
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body[:2000]  # 只取前 2000 字元送給 AI 分析，節省 token


def parse_headers(headers: list) -> dict:
    """從郵件 headers 提取寄件人、標題、日期。"""
    result = {'from': '', 'subject': '', 'date': ''}
    for h in headers:
        name = h['name'].lower()
        if name == 'from':
            result['from'] = h['value']
        elif name == 'subject':
            result['subject'] = h['value']
        elif name == 'date':
            result['date'] = h['value']
    return result


def fetch_emails(days: int = 7, max_results: int = 100) -> list:
    """
    抓取指定天數內的郵件。
    
    Args:
        days: 回報週期（幾天內）
        max_results: 最多抓幾封郵件
    
    Returns:
        郵件清單，每封包含 id, from, subject, date, snippet, body, labels
    """
    print(f"\n📬 正在抓取過去 {days} 天的郵件...")
    service = get_gmail_service()

    query = get_date_query(days)
    emails = []

    try:
        # 第一頁
        response = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = response.get('messages', [])

        if not messages:
            print("   📭 這段時間內沒有郵件。")
            return []

        print(f"   找到 {len(messages)} 封郵件，正在解析...")

        for i, msg in enumerate(messages):
            try:
                # 取得郵件詳細內容
                detail = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                headers = parse_headers(detail['payload'].get('headers', []))
                body = decode_body(detail['payload'])
                labels = detail.get('labelIds', [])

                emails.append({
                    'id': msg['id'],
                    'from': headers['from'],
                    'subject': headers['subject'] or '（無標題）',
                    'date': headers['date'],
                    'snippet': detail.get('snippet', ''),
                    'body': body,
                    'labels': labels,
                    'is_read': 'UNREAD' not in labels,
                    'is_inbox': 'INBOX' in labels,
                })

                if (i + 1) % 10 == 0:
                    print(f"   已解析 {i + 1}/{len(messages)} 封...")

            except Exception as e:
                print(f"   ⚠️ 無法解析郵件 {msg['id']}: {e}")
                continue

    except Exception as e:
        print(f"❌ 抓取郵件失敗：{e}")
        raise

    print(f"✅ 成功解析 {len(emails)} 封郵件。")
    return emails


if __name__ == '__main__':
    emails = fetch_emails(days=7, max_results=20)
    for e in emails[:3]:
        print(f"\n寄件人：{e['from']}")
        print(f"標題：{e['subject']}")
        print(f"日期：{e['date']}")
        print(f"摘要：{e['snippet'][:80]}...")
