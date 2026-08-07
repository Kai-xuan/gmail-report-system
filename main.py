"""
main.py - 系統入口
使用方式：
  python main.py run      # 立即執行一次報告
  python main.py start    # 啟動排程器（長期運行）
  python main.py test     # 測試 Gmail 連線
"""

import sys
from config_loader import load_config


def cmd_test():
    """測試 Gmail 連線是否正常。"""
    print("🔍 測試 Gmail 連線...")
    from gmail_auth import get_gmail_service
    service = get_gmail_service()
    profile = service.users().getProfile(userId='me').execute()
    print(f"✅ 連線成功！")
    print(f"   帳號：{profile['emailAddress']}")
    print(f"   信箱郵件總數：{profile['messagesTotal']}")


def cmd_run():
    """立即執行一次報告（不需要等排程）。"""
    from scheduler import run_report
    run_report()


def cmd_start():
    """啟動排程器，依設定自動定期執行。"""
    from scheduler import start_scheduler
    start_scheduler()


def show_help():
    print("""
Gmail 郵件報告系統

用法：
  python main.py test     測試 Gmail 連線
  python main.py run      立即執行一次報告
  python main.py start    啟動自動排程器

設定：請編輯 config.yaml
    """)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == 'test':
        cmd_test()
    elif command == 'run':
        cmd_run()
    elif command == 'start':
        cmd_start()
    else:
        print(f"❌ 未知指令：{command}")
        show_help()
        sys.exit(1)
