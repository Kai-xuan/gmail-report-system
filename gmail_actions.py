"""
gmail_actions.py - Gmail 標籤操作模組
根據 AI 分析結果，對郵件執行：
  - 重要（high）  → 加星星 ⭐
  - 一般（medium/low）→ 不動
  - 垃圾（is_spam）→ 移至垃圾桶 🗑️
"""

from gmail_auth import get_gmail_service


def apply_labels(emails: list) -> dict:
    """
    批次對郵件套用 Gmail 標籤動作。

    Args:
        emails: 已含 AI 分析結果的郵件清單

    Returns:
        統計結果 dict {starred, trashed, skipped}
    """
    service = get_gmail_service()
    stats = {'starred': 0, 'trashed': 0, 'skipped': 0}

    print(f"\n📌 開始套用 Gmail 標籤，共 {len(emails)} 封...")

    for mail in emails:
        mail_id = mail['id']
        subject_preview = mail.get('subject', '')[:35]

        try:
            if mail.get('is_spam'):
                # ── 垃圾郵件：移至垃圾桶 ──────────────────────────
                # 加上 TRASH label，同時移除 INBOX
                service.users().messages().modify(
                    userId='me',
                    id=mail_id,
                    body={
                        'addLabelIds': ['TRASH'],
                        'removeLabelIds': ['INBOX', 'UNREAD']
                    }
                ).execute()
                print(f"   🗑️  垃圾 → {subject_preview}")
                stats['trashed'] += 1

            elif mail.get('importance') == 'high':
                # ── 重要郵件：加星星 ───────────────────────────────
                service.users().messages().modify(
                    userId='me',
                    id=mail_id,
                    body={
                        'addLabelIds': ['STARRED']
                    }
                ).execute()
                print(f"   ⭐ 星星 → {subject_preview}")
                stats['starred'] += 1

            else:
                # ── 一般郵件：不動 ─────────────────────────────────
                stats['skipped'] += 1

        except Exception as e:
            print(f"   ⚠️ 操作失敗（{subject_preview}）：{e}")
            stats['skipped'] += 1

    print(f"\n✅ 標籤套用完成！")
    print(f"   ⭐ 加星星：{stats['starred']} 封")
    print(f"   🗑️  移垃圾：{stats['trashed']} 封")
    print(f"   ➖ 不動：  {stats['skipped']} 封")
    return stats