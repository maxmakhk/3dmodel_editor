# GLB Texture Editor - Session Management Edition 

## 🎨 專業 GLB 編輯工具 + 多 Session 管理

這是一個功能強大的 3D GLB 紋理編輯器，已升級支持多個 session 記錄、伺服器 API、手動配置編輯。

---

## 🚀 快速開始（30 秒）

### Windows
```bash
start-server.bat
# 自動打開 http://localhost:3000
```

### macOS / Linux
```bash
./start-server.sh
# 或 python server.py
```

然後打開瀏覽器：**http://localhost:3000**

---

## 📚 文檔導航

| 文檔 | 用途 | 長度 |
|------|------|------|
| **[QUICK_START.md](QUICK_START.md)** | 5分鐘上手指南 | 快速 |
| **[SESSION_MANAGEMENT_README.md](SESSION_MANAGEMENT_README.md)** | 完整功能文檔 | 詳細 |
| **[TEST_GUIDE.md](TEST_GUIDE.md)** | 10步驟測試流程 | 實踐 |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | 技術實現詳情 | 技術 |

---

## ✨ 核心功能

### 🎬 編輯功能
- ✅ **紋理管理** - 下載、替換、還原紋理
- ✅ **骨骼編輯** - 選擇骨骼、附加配件
- ✅ **變換編輯** - 位置、旋轉、縮放精確控制
- ✅ **即時預覽** - 3D 軌道控制、實時渲染
- ✅ **動畫預覽** - 播放、暫停、調整速度

### 💾 Session 管理
- ✅ **多記錄保存** - 無限 session 記錄
- ✅ **新建/覆寫** - 靈活保存選項
- ✅ **快速切換** - 載入歷史配置
- ✅ **手動編輯** - 直接編輯 JSON 檔案
- ✅ **版本控制** - Git 友善

### 🔧 技術支持
- ✅ **Node.js 伺服器** - 輕量級部署
- ✅ **Python Flask** - 靈活選擇
- ✅ **REST API** - 完整端點
- ✅ **CORS 支持** - 跨域安全
- ✅ **啟動腳本** - 一鍵開啟

---

## 📁 檔案結構

```
3dmodel_editor/
├── 🎨 編輯器
│   └── editor.html          (現代化 WebGL 編輯器)
│
├── 🖥️ 伺服器 (二選一)
│   ├── server.js                          (Node.js 版)
│   └── server.py                          (Python 版)
│
├── ⚡ 啟動腳本 (選一個用)
│   ├── start-server.bat                   (Windows .bat)
│   ├── start-server.ps1                   (PowerShell)
│   └── start-server.sh                    (Bash)
│
├── 📦 資料
│   ├── glb-save.json                      (自動建立)
│   └── data/sprite.json                   (VFX 配置)
│
└── 📖 文檔
    ├── README.md                          (本檔案)
    ├── QUICK_START.md                     (快速上手)
    ├── SESSION_MANAGEMENT_README.md       (完整文檔)
    ├── TEST_GUIDE.md                      (測試步驟)
    └── IMPLEMENTATION_SUMMARY.md          (技術細節)
```

---

## 🛠️ 使用方法

### 方案 A: Node.js（推薦，最簡單）

```bash
# 只需一行！
node server.js

# 自訂埠
node server.js 8080
```

### 方案 B: Python Flask

```bash
# 首次安裝依賴
pip install flask flask-cors

# 執行伺服器
python server.py
```

### 方案 C: 啟動腳本（自動檢查環境）

```bash
# Windows
start-server.bat

# Linux/macOS
chmod +x start-server.sh
./start-server.sh
```

---

## 🎯 主要工作流程

```
1. 啟動伺服器
   ↓
2. 打開 http://localhost:3000
   ↓
3. 拖放或選擇 GLB 檔案
   ↓
4. 編輯紋理、附加配件、調整位置
   ↓
5. 點擊 "💾 Save Session" 保存
   ↓
6. 下次打開自動顯示可載入的 session
   ↓
7. 點擊 "Export GLB" 下載最終檔案
```

---

## 💡 主要特性

### 🆕 多 Session 管理（新功能）

**前：** 只能一個自動儲存  
**後：** 無限個 session，手動管理

```json
{
  "sessions": [
    { "name": "Character v1", ... },
    { "name": "Character v2", ... },
    { "name": "Accessory Set A", ... }
  ]
}
```

### 🆕 Save as / Overwrite

```
💾 Save Session
├─ 新建 → 自動命名或自訂
└─ 覆寫 → 選擇要更新的 session
```

### 🆕 JSON 手動編輯

可用任何文字編輯器修改 `glb-save.json`:
- 改名稱
- 刪除舊記錄
- 調整 transform 數值
- 重新載入頁面自動生效

### 🔄 API 端點

```
GET  /api/sessions           - 列表
POST /api/session/save       - 保存
GET  /api/session/load?id=0  - 載入
DEL  /api/session/delete?id=0 - 刪除
GET  /api/raw-save           - 原始 JSON
```

---

## 📊 效能

| 操作 | 時間 |
|------|------|
| 啟動伺服器 | < 1s |
| 載入 GLB | 2-5s |
| 保存 session | < 1s |
| 載入 session | 2-5s |

---

## 🔐 本地安全

- ✅ 所有資料存在本地 `glb-save.json`
- ✅ 無網路上傳
- ✅ 支持離線使用（啟動後）
- ✅ 可用 Git 管理版本

---

## 📈 進階用途

### 1. 遠端訪問

```bash
# SSH Tunneling
ssh -L 3000:localhost:3000 user@server

# 然後本地打開 http://localhost:3000
```

### 2. Nginx 反向代理

```nginx
server {
    listen 80;
    location / {
        proxy_pass http://localhost:3000;
    }
}
```

### 3. Docker 容器化

```dockerfile
FROM node:18
WORKDIR /app
COPY server.js editor.html ./
CMD ["node", "server.js", "0.0.0.0"]
```

### 4. CI/CD 集成

在 GitHub Actions 中自動備份 `glb-save.json`

---

## 🐛 常見問題

**Q: 第一次用，應該看什麼文檔？**  
A: [QUICK_START.md](QUICK_START.md) (5分鐘上手)

**Q: 完整功能說明在哪？**  
A: [SESSION_MANAGEMENT_README.md](SESSION_MANAGEMENT_README.md) (詳細指南)

**Q: 想驗證系統是否正常運作？**  
A: [TEST_GUIDE.md](TEST_GUIDE.md) (10步測試流程)

**Q: 想了解技術實現？**  
A: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) (架構詳情)

**Q: 為什麼改用伺服器而不是 IndexedDB？**  
A: 容量無限、易備份、支持手動編輯、版本控制

**Q: 能否本地離線使用？**  
A: 可以。啟動伺服器後無需網路連線

**Q: 數據會上傳到雲端嗎？**  
A: 不會。所有數據存在本地 `glb-save.json`

---

## 📞 技術支持

### 快速自檢

```bash
# 1. 檢查 Node.js
node --version

# 2. 檢查埠
netstat -ano | findstr :3000  # Windows
lsof -i :3000                  # macOS/Linux

# 3. 測試伺服器
curl http://localhost:3000/api/sessions

# 4. 查看日誌
# 終端中檢查伺服器輸出
```

### 開發者工具

```javascript
// 瀏覽器 DevTools (F12)
// Network 標籤 - 監控 API 呼叫
// Console - 查看錯誤訊息
// Application - 檢查 localStorage
```

---

## 🎓 學習資源

### 編輯技巧

1. **紋理替換** - 下載原始、編輯、重新上傳
2. **配件附加** - 選骨骼、指定位置和旋轉
3. **精確定位** - 使用數字輸入框調整毫米級變化
4. **批量操作** - 複製所有記錄、共享配置

### 最佳實踐

- 💾 每個重要修改後立即 Save Session
- 📝 使用有意義的 session 名稱（e.g. "v1.0", "eyes_red", "armor_gold"）
- 🔄 定期備份 `glb-save.json`
- 📊 用 Git 追蹤版本歷程

---

## 🎉 版本歷程

### v2.0 (Current)
- ✅ 伺服器 API 儲存
- ✅ 多 session 支持
- ✅ Save as / Overwrite UI
- ✅ 手動 JSON 編輯
- ✅ Node.js + Python 伺服器
- ✅ 完整文檔和測試指南

### v1.0 (Previous)
- IndexedDB 自動儲存
- 單個 session

---

## 📋 檢查清單

準備就緒？
- [ ] 閱讀 QUICK_START.md
- [ ] 伺服器成功啟動
- [ ] 編輯器在 http://localhost:3000 載入
- [ ] 能夠載入 GLB 檔案
- [ ] 能夠保存 session
- [ ] glb-save.json 有內容
- [ ] 能夠載入已保存的 session

---

## 🚀 開始編輯

**立即開始：** 執行啟動腳本或 `node server.js`

**需要幫助？** 參考文檔或 F12 DevTools 診斷

**發現問題？** 檢查日誌或查閱故障排除章節

---

## 📄 附件清單

```
README.md (📍 本檔案)
├── QUICK_START.md           (🟢 新手必看)
├── SESSION_MANAGEMENT_README.md (🔵 完整文檔)
├── TEST_GUIDE.md            (🟡 測試驗證)
└── IMPLEMENTATION_SUMMARY.md (🔴 技術深度)
```

---

## ⚡ 一鍵啟動

```bash
# 複製下列命令到終端並執行
cd e:/CyberpunkRealm/doc/3dmodel_editor && node server.js
```

然後打開瀏覽器：`http://localhost:3000`

---

## 🙏 感謝使用

**祝編輯愉快！** 🎨✨

如有任何問題，先查閱文檔，通常能解決 95% 的問題。

---

**最後更新：** 2026-05-14  
**狀態：** ✅ 完全就緒  
**版本：** 2.0 - Session Management Edition
