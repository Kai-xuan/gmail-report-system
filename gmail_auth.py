"""
gmail_auth.py - Gmail OAuth2 認證模組
第一次執行需在瀏覽器登入授權，之後自動使用 token.json 續期。
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ⚠️ 新增 gmail.modify 權限（用於加星星、移垃圾桶）
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_gmail_service():
    """取得 Gmail API 服務物件，自動處理 OAuth2 認證流程。"""
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 正在更新 token...")
            creds.refresh(Request())
        else:
            print("🌐 開啟瀏覽器進行 Google 授權...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("✅ 授權成功，token 已儲存。")

    service = build('gmail', 'v1', credentials=creds)
    return service


if __name__ == '__main__':
    service = get_gmail_service()
    profile = service.users().getProfile(userId='me').execute()
    print(f"✅ 已連線到 Gmail：{profile['emailAddress']}")
    print(f"   信箱總郵件數：{profile['messagesTotal']}")
