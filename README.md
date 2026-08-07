# 📬 Gmail 智慧郵件報告系統

> 自動分析 Gmail 收件夾，AI 判斷重要性、過濾垃圾郵件，並定期發送 HTML 摘要報告。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Gmail API](https://img.shields.io/badge/Gmail_API-v1-red?logo=gmail&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude-Haiku-orange?logo=anthropic&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| ⭐ **重要郵件加星星** | AI 判斷為高重要性的郵件自動加上星星標記 |
| 📂 **垃圾郵件分類** | 自動移至垃圾郵件資料夾，30 天後由 Gmail 自動清除 |
| 📊 **HTML 摘要報告** | 定期寄送美觀的 HTML 報告，包含郵件統計與 AI 摘要 |
| ⏰ **彈性排程** | 支援每日、每週、或自訂 cron 時間觸發 |
| 💰 **極低成本** | 使用 Claude Haiku，1,000 封郵件分析費用約 NT$30-50/月 |

---

## 🖥️ 系統效果預覽

執行後，Gmail 收件夾會自動整理為：

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
├── main.py              # 主入口（run / start / test）
├── gmail_auth.py        # Gmail OAuth2 認證
├── email_fetcher.py     # 郵件抓取與解析
├── email_analyzer.py    # Claude AI 分析引擎
├── gmail_actions.py     # Gmail 標籤操作（加星星/移垃圾郵件）
├── report_sender.py     # HTML 報告產生與發送
├── scheduler.py         # APScheduler 排程管理
├── config_loader.py     # 設定檔載入
├── config.yaml          # 所有設定集中管理
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

## 🚀 快速開始

### 前置需求

- Python 3.8 以上
- 一個 Gmail 帳號
- [Google Cloud Console](https://console.cloud.google.com/) 帳號（免費）
- [Anthropic API Key](https://console.anthropic.com/)

### 1. 複製專案

```bash
git clone https://github.com/your-username/gmail-report-system.git
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

### 4. 設定 Gmail 應用程式密碼（用於發送報告）

1. 前往 [Google 帳號安全性設定](https://myaccount.google.com/security)
2. 確認「兩步驟驗證」已開啟
3. 搜尋「應用程式密碼」，產生一組 16 位密碼並複製

### 5. 設定環境變數

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-api03-你的Key

# Mac / Linux
export ANTHROPIC_API_KEY=sk-ant-api03-你的Key
```

### 6. 填寫 config.yaml

```yaml
schedule:
  interval: weekly       # daily / weekly / custom
  query_days: 7

report:
  recipients:
    - your@email.com     # 收報告的信箱
  smtp_user: your_gmail@gmail.com
  smtp_password: "你的16位應用程式密碼"

spam_keywords:
  - unsubscribe
  - 退訂
  - promotional
```

### 7. 測試連線

```bash
python main.py test
```

瀏覽器會開啟 Google 授權頁面，點擊允許後看到 ✅ 即代表成功。

---

## 📖 使用方式

```bash
# 立即執行一次報告
python main.py run

# 啟動自動排程器（依 config.yaml 設定定期執行）
python main.py start

# 測試 Gmail 連線
python main.py test
```

---

## ⚙️ 設定說明

### 排程設定

```yaml
schedule:
  interval: weekly        # daily（每天）/ weekly（每週）/ custom（自訂）
  cron: "0 9 * * 1"       # 僅 interval=custom 時有效（分 時 日 月 星期）
  query_days: 7           # 每次分析幾天內的郵件
```

### 垃圾郵件關鍵字

在 `spam_keywords` 加入任何想過濾的關鍵字，含有這些關鍵字的郵件會在送 AI 分析前先過濾，節省 API 費用：

```yaml
spam_keywords:
  - unsubscribe
  - 退訂
  - 優惠
  - 限時特賣
  - 你的自訂關鍵字
```

### AI 重要性判斷標準

| 等級 | 判斷條件 | Gmail 動作 |
|------|----------|------------|
| `high` | 需當天回覆、客戶投訴、重要合約、緊急事項 | ⭐ 加星星 |
| `medium` | 一般業務聯繫、會議通知、不緊急事項 | 無動作 |
| `low` | 系統通知、收據、無需回覆 | 無動作 |
| `spam` | 廣告、促銷、退訂信 | 📂 移至垃圾郵件 |

---

## 💰 成本估算

| 郵件量 | Claude Haiku 費用 | Gmail API | 合計 |
|--------|-------------------|-----------|------|
| 200 封/月 | 約 NT$5 | 免費 | **NT$5/月** |
| 1,000 封/月 | 約 NT$30-50 | 免費 | **NT$30-50/月** |
| 5,000 封/月 | 約 NT$150-200 | 免費 | **NT$150-200/月** |

> 使用 Claude Haiku 模型（最低成本），每封郵件約 150 tokens。

---

## 🔒 安全性說明

- `credentials.json` 和 `token.json` 已加入 `.gitignore`，**絕對不會上傳到 GitHub**
- `config.yaml` 中的 SMTP 密碼建議改用環境變數管理
- 系統僅申請 `gmail.readonly`、`gmail.modify`、`gmail.send` 三項最小必要權限

---

## 🛠️ 常見問題

**Q：出現「已封鎖存取權：未完成 Google 驗證程序」**
A：前往 Google Cloud Console → OAuth 同意畫面 → 測試使用者，加入你的 Gmail 帳號。

**Q：SMTP 發信失敗**
A：確認 Gmail 兩步驟驗證已開啟，且 `smtp_password` 填的是應用程式密碼（16位），不是 Gmail 登入密碼。

**Q：AI 分析顯示「分析失敗」**
A：確認 `ANTHROPIC_API_KEY` 環境變數已正確設定，重新開啟命令提示字元後再執行。

**Q：誤判為垃圾郵件怎麼辦？**
A：垃圾郵件只是移至「垃圾郵件」資料夾，30 天內可在 Gmail 中手動選取「移回收件夾」。

---

## 📄 License

MIT License — 歡迎自由使用與修改。
