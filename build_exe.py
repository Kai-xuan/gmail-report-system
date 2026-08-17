"""
build_exe.py - 打包成 Windows .exe 安裝包
在客戶電腦安裝完 Python 後，執行此腳本即可打包。

使用方式：
  pip install pyinstaller
  python build_exe.py
"""

import subprocess
import sys
import os

def build():
    print("📦 開始打包 Gmail 報告系統...")

    # PyInstaller 指令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=Gmail報告系統',
        '--onefile',                    # 打包成單一 .exe
        '--noconsole',                  # 不顯示黑色命令提示字元視窗
        '--add-data=templates;templates',  # 包含 HTML 模板
        '--add-data=config.example.yaml;.',
        '--hidden-import=flask',
        '--hidden-import=flask_socketio',
        '--hidden-import=google.auth',
        '--hidden-import=google.auth.transport.requests',
        '--hidden-import=google_auth_oauthlib.flow',
        '--hidden-import=googleapiclient.discovery',
        '--hidden-import=anthropic',
        '--hidden-import=apscheduler',
        '--hidden-import=yaml',
        'app.py'
    ]

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n✅ 打包成功！")
        print("   檔案位置：dist/Gmail報告系統.exe")
        print("\n交付給客戶時，請確認以下檔案一起給：")
        print("  ├── Gmail報告系統.exe   （主程式）")
        print("  ├── credentials.json    （需由你設定好再交付）")
        print("  ├── config.yaml         （需填好設定再交付）")
        print("  └── 使用說明.txt")
    else:
        print("\n❌ 打包失敗，請確認 PyInstaller 已安裝：")
        print("   pip install pyinstaller")

if __name__ == '__main__':
    build()
