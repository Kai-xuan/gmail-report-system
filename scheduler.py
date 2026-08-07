"""
scheduler.py - 排程管理模組
支援每日、每週、自訂 cron 三種模式。
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from config_loader import load_config
from email_fetcher import fetch_emails
from email_analyzer import analyze_batch
from gmail_actions import apply_labels
from report_sender import send_report


def run_report():
    """執行一次完整的郵件分析＋標籤＋報告流程。"""
    print(f"\n{'='*50}")
    print(f"🚀 開始執行報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    try:
        config = load_config()
        days = config.get('schedule', {}).get('query_days', 7)

        # 1. 抓取郵件
        emails = fetch_emails(days=days)
        if not emails:
            print("📭 這段時間沒有郵件，跳過分析。")
            return

        # 2. AI 分析
        analyzed = analyze_batch(emails, config)

        # 3. ⭐ 套用 Gmail 標籤（加星星 / 移垃圾桶）
        apply_labels(analyzed)

        # 4. 發送報告
        send_report(analyzed, days, config)

        print(f"\n✅ 報告執行完成！")

    except Exception as e:
        print(f"\n❌ 報告執行失敗：{e}")
        import traceback
        traceback.print_exc()


def start_scheduler():
    """啟動排程器。"""
    config = load_config()
    schedule_config = config.get('schedule', {})
    mode = schedule_config.get('interval', 'weekly')
    cron_expr = schedule_config.get('cron', '0 9 * * 1')

    scheduler = BlockingScheduler(timezone='Asia/Taipei')

    if mode == 'daily':
        scheduler.add_job(run_report, CronTrigger(hour=9, minute=0))
        print("⏰ 排程：每天早上 9:00 執行")
    elif mode == 'weekly':
        scheduler.add_job(run_report, CronTrigger(day_of_week='mon', hour=9, minute=0))
        print("⏰ 排程：每週一早上 9:00 執行")
    elif mode == 'custom':
        parts = cron_expr.split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
            scheduler.add_job(run_report, CronTrigger(
                minute=minute, hour=hour,
                day=day, month=month,
                day_of_week=day_of_week
            ))
            print(f"⏰ 排程（自訂 cron）：{cron_expr}")
        else:
            scheduler.add_job(run_report, CronTrigger(day_of_week='mon', hour=9, minute=0))

    print("\n✅ 排程器已啟動，按 Ctrl+C 停止。")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n⏹ 排程器已停止。")


if __name__ == '__main__':
    start_scheduler()
