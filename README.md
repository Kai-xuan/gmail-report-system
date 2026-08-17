# 📬 Gmail 智慧郵件報告系統

> 自動分析 Gmail 收件夾，AI 判斷重要性、過濾垃圾郵件，並定期發送 HTML 摘要報告。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Gmail API](https://img.shields.io/badge/Gmail_API-v1-red?logo=gmail&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude-Haiku-orange?logo=anthropic&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌿 版本說明

| 分支 | 版本 | 適合對象 | 使用方式 |
|------|------|----------|----------|
| `main` | v1 命令列版 | 開發者 | 命令提示字元 |
| `v2` | v2 Web UI 版 ⭐ | 一般使用者／企業 | 瀏覽器操作，雙擊啟動 |

> **建議使用 v2 分支**，使用者無需碰任何命令提示字元。

---

## ✨ 功能特色

| 功能 | v1 | v2 |
|------|:--:|:--:|
| ⭐ 重要郵件自動加星星 | ✅ | ✅ |
| 📂 垃圾郵件自動分類 | ✅ | ✅ |
| 📊 HTML 摘要報告寄送 | ✅ | ✅ |
| ⏰ 彈性排程（每日／每週／自訂）| ✅ | ✅ |
| 🖥️ Web UI 瀏覽器介面 | ❌ | ✅ |
| 🔄 瀏覽器一鍵重新授權 | ❌ | ✅ |
| 💾 密碼設定後不需重填 | ❌ | ✅ |
| 📦 雙擊 .bat 即可啟動 | ❌ | ✅ |

---

## 🖥️ v2 介面預覽

```
┌─────────────────────────────────────────────────┐
│  📬 Gmail 報告系統                               │
│  ─────────────────                              │
│  🏠 總覽      → Gmail 連線狀態、設定摘要         │
│  ▶️ 立即執行  → 一鍵執行，即時顯示執行記錄       │
│  ⚙️ 設定      → 所有設定用表單填寫，存檔生效     │
└─────────────────────────────────────────────────┘
```

執行後，Gmail 收件夾自動整理為：

```
收件夾
├── ⭐ 重要合約更新通知        ← AI 判斷高重要性，自動加星
├── ⭐ 客戶回覆：專案確認      ← AI 判斷高重要性，自動加星
├──    每週工作報告             ← 一般郵件，不動
├──    會議通知：週五下午       ← 一般郵件，不動
└──    （廣告促銷已自動移走）  ← 移至垃圾郵件資料夾
```

---

## 🏗️ 系統架構

```
gmail-report-system/
├── app.py               # Flask Web UI 後端（v2 新增）
├── templates/
│   └── index.html       # Web UI 前端（v2 新增）
├── 啟動系統.bat          # 雙擊啟動，自動開瀏覽器（v2 新增）
├── build_exe.py         # 打包成 .exe 安裝包（v2 新增）
├── main.py              # 命令列入口（v1）
├── gmail_auth.py        # Gmail OAuth2 認證
├── email_fetcher.py     # 郵件抓取與解析
├── email_analyzer.py    # Claude AI 分析引擎
├── gmail_actions.py     # Gmail 標籤操作（⭐ 加星星 / 📂 垃圾郵件）
├── report_sender.py     # HTML 報告產生與發送
├── scheduler.py         # APScheduler 排程管理
├── config_loader.py     # 設定檔載入
├── config.example.yaml  # 設定檔範本
└── requirements.txt     # 套件清單
```

**執行流程：**
```
Gmail API 抓取郵件
      ↓
本地關鍵字預過濾（免費）
      ↓
Claude Haiku AI 深度分析
      ↓
套用 Gmail 標籤（⭐ 星星 / 📂 垃圾郵件）
      ↓
發送 HTML 摘要報告
```

---

## 🚀 快速開始（v2 Web UI 版）

### 前置需求

- Python 3.8 以上
- 一個 Gmail 帳號
- [Google Cloud Console](https://console.cloud.google.com/) 帳號（免費）
- [Anthropic API Key](https://console.anthropic.com/)

### 1. 切換到 v2 分支並複製專案

```bash
git clone -b v2 https://github.com/Kai-xuan/gmail-report-system.git
cd gmail-report-system
```

### 2. 安裝套件

```bash
pip install -r requirements.txt
```

### 3. 取得 Gmail API 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)，建立新專案
2. 啟用 **Gmail API**
3. 建立「OAuth 同意畫面」（選外部，填入應用程式名稱）
4. 在「測試使用者」中加入你的 Gmail 帳號
5. 建立「OAuth 用戶端 ID」（類型選桌面應用程式）
6. 下載憑證，**改名為 `credentials.json`**，放入專案根目錄

### 4. 建立設定檔

```bash
cp config.example.yaml config.yaml
```

### 5. 設定環境變數

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-api03-你的Key

# Mac / Linux
export ANTHROPIC_API_KEY=sk-ant-api03-你的Key
```

### 6. 啟動系統

**Windows（推薦）：** 雙擊 `啟動系統.bat`，瀏覽器自動開啟

**或命令列：**
```bash
python app.py
```

開啟瀏覽器前往 `http://localhost:5000`，在介面完成以下設定：
- **設定頁** → 填入收件人、Gmail 帳號、應用程式密碼
- **總覽頁** → 點擊「重新授權 Gmail」完成 OAuth 授權
- **立即執行** → 點擊按鈕，即時查看執行記錄

---

## 📖 使用方式

### v2（Web UI）
雙擊 `啟動系統.bat` → 瀏覽器自動開啟 → 點擊「▶ 開始分析」

### v1（命令列）
```bash
python main.py test    # 測試 Gmail 連線
python main.py run     # 立即執行一次報告
python main.py start   # 啟動自動排程器
```

---

## ⚙️ 設定說明

### 排程設定

```yaml
schedule:
  interval: weekly        # daily（每天）/ weekly（每週）/ custom（自訂）
  cron: "0 9 * * 1"       # 僅 custom 模式有效（分 時 日 月 星期）
  query_days: 7           # 每次分析幾天內的郵件
```

### AI 重要性判斷標準

| 等級 | 判斷條件 | Gmail 動作 |
|------|----------|------------|
| `high` | 需當天回覆、客戶投訴、重要合約、緊急事項 | ⭐ 加星星 |
| `medium` | 一般業務聯繫、會議通知、不緊急事項 | 無動作 |
| `low` | 系統通知、收據、無需回覆 | 無動作 |
| `spam` | 廣告、促銷、退訂信 | 📂 移至垃圾郵件資料夾（30天後自動刪除）|

---

## 💰 成本估算

| 郵件量 | Claude Haiku 費用 | Gmail API | 合計 |
|--------|-------------------|-----------|------|
| 200 封/月 | 約 NT$5 | 免費 | **NT$5/月** |
| 1,000 封/月 | 約 NT$30-50 | 免費 | **NT$30-50/月** |
| 5,000 封/月 | 約 NT$150-200 | 免費 | **NT$150-200/月** |

> 使用 Claude Haiku（最低成本模型），每封郵件約 150 tokens。

---

## 🔒 安全性說明

- `credentials.json`、`token.json`、`config.yaml` 已加入 `.gitignore`，不會上傳到 GitHub
- Web UI 密碼欄位儲存後不回傳明文，重新開啟頁面無需重填
- 系統僅申請 `gmail.readonly`、`gmail.modify`、`gmail.send` 三項最小必要權限

---

## 🛠️ 常見問題

**Q：出現「已封鎖存取權：未完成 Google 驗證程序」**
A：前往 Google Cloud Console → OAuth 同意畫面 → 測試使用者，加入你的 Gmail 帳號。

**Q：Token 失效（invalid_grant）**
A：v2 會自動偵測並在頁面顯示警告，點擊「重新授權 Gmail」即可，無需碰命令提示字元。

**Q：SMTP 發信失敗**
A：確認 Gmail 兩步驟驗證已開啟，且填的是應用程式密碼（16位），不是 Gmail 登入密碼。

**Q：誤判為垃圾郵件怎麼辦？**
A：垃圾郵件只移至「垃圾郵件」資料夾，30 天內可在 Gmail 手動「移回收件夾」。

---

## 📄 License

MIT License — 歡迎自由使用與修改。
