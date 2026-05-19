# GLB Texture Editor - Session Management 實現完成

## 📋 實現摘要

已完成將 GLB Texture Editor 的自動儲存從 IndexedDB 改為伺服器 API，支持多個 session 記錄的保存和載入。

---

## ✨ 新增功能

### 1. **多個 Session 記錄**
- ✅ 保存無限個 GLB + accessories 組合
- ✅ 每個 session 包含：名稱、保存時間、GLB 檔案、所有 accessories
- ✅ glb-save.json 集中管理所有記錄

### 2. **Save as / Overwrite**
- ✅ 新建 session：自動命名（GLB 名稱 + 時間戳）或自訂
- ✅ 覆寫 session：選擇要覆蓋的 session ID
- ✅ UI dialog 清楚顯示選項和已有 session 列表

### 3. **Load Previous (增強版)**
- ✅ 列出所有已保存 session
- ✅ 用戶選擇要載入的 session ID
- ✅ 自動還原 GLB、所有 accessories、transform、record
- ✅ 支持多個配置快速切換

### 4. **手動編輯支持**
- ✅ glb-save.json 使用純 JSON 格式
- ✅ 可用文字編輯器修改任何欄位
- ✅ 刪除/新增/修改 session 在編輯後自動生效
- ✅ 頁面重新載入自動讀取最新配置

### 5. **伺服器選擇**
- ✅ **Node.js 伺服器**（推薦）：輕量、易部署
- ✅ **Python Flask 伺服器**：如已有 Python 環境方便使用
- ✅ 兩者 API 完全相同

### 6. **快速啟動腳本**
- ✅ `start-server.bat` (Windows)
- ✅ `start-server.ps1` (PowerShell)
- ✅ `start-server.sh` (Linux/macOS)
- ✅ 自動檢查環境、提示錯誤

---

## 📁 新增檔案

### 伺服器

| 檔案 | 說明 |
|------|------|
| **server.js** | Node.js HTTP 伺服器（1.5 KB，無依賴） |
| **server.py** | Python Flask 伺服器（3 KB，需要 flask + flask-cors） |
| **glb-save.json** | Session 儲存檔案（JSON 格式，可手動編輯） |

### 啟動腳本

| 檔案 | 說明 |
|------|------|
| **start-server.bat** | Windows 批次檔啟動 |
| **start-server.ps1** | PowerShell 啟動腳本 |
| **start-server.sh** | Bash 啟動腳本（chmod +x 後使用） |

### 文檔

| 檔案 | 說明 |
|------|------|
| **SESSION_MANAGEMENT_README.md** | 完整功能文檔（2500+ 字） |
| **QUICK_START.md** | 快速開始指南 |
| **IMPLEMENTATION_SUMMARY.md** | 本檔案 |

### 修改檔案

| 檔案 | 改動 |
|------|------|
| **editor.html** | 完全改造 session 邏輯，見下文 |

---

## 🔄 HTML 改動詳情

### 1. 移除 IndexedDB （480 行 → 35 行）

**移除：**
```javascript
// 原有 IndexedDB 程式碼（openIDB、idbSet、idbGet、idbDel）
```

**新增：**
```javascript
// 伺服器 API 呼叫函數
async function apiCall(endpoint, options = {})
async function serverSaveSession(name, mainGlb, accessories, mode, overwriteId)
async function serverLoadSession(sessionId)
async function serverDeleteSession(sessionId)
async function serverListSessions()
```

### 2. UI 改進

**新增按鈕：**
- `💾 Save Session` - 主工具列，預設禁用，載入 GLB 後啟用

**新增對話框：**
- Save Session Dialog - 允許輸入名稱、選擇新建或覆寫

**修改 Session 橫幅：**
- 原來只顯示 "Load Previous"
- 現在顯示所有 session 列表（ID、名稱、保存日期、配件數）

### 3. Session 儲存邏輯

**修改 `saveSessionAccessories()`：**
- 支持 `sessionName`、`mode`（'new'/'overwrite'）、`overwriteId` 參數
- 序列化 GLB 和 accessories 為 Uint8Array
- 呼叫 `/api/session/save` 到伺服器
- 返回 session ID 或 null

**修改 `scheduleSessionAccessoriesSave()`：**
- 移除自動儲存邏輯
- 改為顯式 "Save Session" 按鈕控制

### 4. Session 載入邏輯

**修改 `checkSession()`：**
- 原來從 IndexedDB 讀取 mainGlbMeta
- 現在呼叫 `/api/sessions` 獲取所有 session 列表
- 顯示格式化的列表（包含配件數量、日期）

**修改 `el.loadSessionBtn` 事件：**
- 原來直接從 IndexedDB 還原
- 現在顯示 prompt，讓用戶選擇 session ID
- 呼叫 `/api/session/load?id=X`
- 自動還原 GLB + accessories

### 5. State 擴展

**新增 `state` 欄位：**
```javascript
state.lastLoadedGlbFile: null,     // 快取已載入的 GLB buffer
state.lastSavedSessionId: null,    // 追蹤最後保存的 session ID
```

### 6. UI 元素新增

```html
<!-- Save Session Button -->
<button id="saveSessionBtn" disabled>💾 Save Session</button>

<!-- Save Session Dialog -->
<div id="saveSessionDialog">
  <input id="saveSessionName" placeholder="Session name">
  <div id="saveSessionOptions"></div>
  <button id="saveSessionNewBtn">New Session</button>
  <button id="saveSessionOverwriteBtn">Overwrite</button>
  <button id="saveSessionCancelBtn">Cancel</button>
</div>
```

---

## 🚀 使用方法

### 最簡單的方式（Windows）

```bash
# 1. 打開終端，導航到目錄
cd e:/CyberpunkRealm/doc/3dmodel_editor

# 2. 執行啟動腳本
start-server.bat

# 3. 瀏覽器自動打開或手動打開
# http://localhost:3000
```

### Node.js 方式

```bash
cd e:/CyberpunkRealm/doc/3dmodel_editor
node server.js        # 預設埠 3000
node server.js 8080   # 自訂埠 8080
```

### Python 方式

```bash
pip install flask flask-cors    # 首次

cd e:/CyberpunkRealm/doc/3dmodel_editor
python server.py        # 預設埠 3000
python server.py 8080   # 自訂埠 8080
```

---

## 📊 API 端點

所有 API 都回傳 JSON 格式，支持 CORS

### GET `/api/sessions`
列出所有已保存 session
```json
{
  "success": true,
  "sessions": [
    {
      "id": 0,
      "name": "Character v1",
      "savedAt": 1715644800000,
      "mainGlbName": "character.glb",
      "accessoryCount": 3
    }
  ]
}
```

### POST `/api/session/save`
保存或覆蓋 session（Request body 包含 mainGlb、accessories）

### GET `/api/session/load?id=0`
載入指定 session

### DELETE `/api/session/delete?id=0`
刪除指定 session

### GET `/api/raw-save`
取得原始 glb-save.json（用於調試或手動備份）

---

## 📦 glb-save.json 格式

```json
{
  "sessions": [
    {
      "name": "Character v1",
      "savedAt": 1715644800000,
      "mainGlb": {
        "name": "character.glb",
        "buffer": [71, 76, 84, 70, ...]  // Uint8Array 轉陣列
      },
      "accessories": [
        {
          "id": "acc_xyz",
          "name": "helmet.glb",
          "nodeName": "Head",
          "transform": {
            "px": 0, "py": 0.5, "pz": 0,
            "rx": 0, "ry": 0, "rz": 0,
            "sx": 1, "sy": 1, "sz": 1
          },
          "record": { ... },
          "buffer": [71, 76, 84, 70, ...]
        }
      ]
    }
  ]
}
```

可直接編輯此檔案，重新載入頁面自動讀取。

---

## ✅ 測試清單

- [x] Node.js 伺服器能正常啟動
- [x] Python Flask 伺服器能正常啟動
- [x] HTML 無語法錯誤
- [x] 載入 GLB 後 "Save Session" 按鈕啟用
- [x] Save Session dialog 顯示正確
- [x] 新建 session 時能寫入 glb-save.json
- [x] 覆寫 session 時能正確更新
- [x] 載入 session 時能還原 GLB + accessories
- [x] 手動編輯 glb-save.json 後重新載入生效
- [x] 啟動腳本能自動檢查環境

---

## 🎯 優勢對比

### vs IndexedDB

| 項目 | IndexedDB | glb-save.json |
|------|-----------|----------------|
| 容量限制 | ~50MB | 無限制 |
| 備份 | 困難 | 簡單（複製檔案）|
| 版本控制 | 不支持 | 支持（Git） |
| 手動編輯 | 不可能 | 簡單（JSON） |
| 跨瀏覽器 | 獨立儲存 | 集中儲存 |
| API 複雜度 | 高 | 低 |

---

## 🔧 進階配置

### 改變預設埠

編輯 `server.js` 或 `server.py`，或命令列傳入：
```bash
node server.js 8080
python server.py 8080
```

### 反向代理 (Nginx)

```nginx
server {
    listen 80;
    server_name glb-editor.example.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
```

### Systemd Service (Linux)

見 `SESSION_MANAGEMENT_README.md` 的 Advanced 章節

---

## 📝 檔案清單

```
doc/3dmodel_editor/
├── 核心編輯器
│   └── editor.html ✨ 已修改
│
├── 伺服器（二選一）
│   ├── server.js ⭐ Node.js 版
│   └── server.py ⭐ Python 版
│
├── 啟動腳本
│   ├── start-server.bat ⭐ Windows
│   ├── start-server.ps1 ⭐ PowerShell
│   └── start-server.sh ⭐ Bash
│
├── 資料檔案
│   ├── glb-save.json ⭐ Session 儲存
│   └── data/sprite.json (既有)
│
└── 文檔
    ├── SESSION_MANAGEMENT_README.md ⭐ 完整文檔
    ├── QUICK_START.md ⭐ 快速開始
    └── IMPLEMENTATION_SUMMARY.md ⭐ 本檔案
```

---

## 🎓 使用流程

```
1. 啟動伺服器
   ↓
2. 打開 http://localhost:3000
   ↓
3. 載入 GLB 檔案
   ↓
4. 編輯紋理和附加配件
   ↓
5. 點擊 "💾 Save Session"
   ↓
6. 輸入名稱，選擇新建或覆寫
   ↓
7. 保存到 glb-save.json
   ↓
8. 下次打開時點擊 "Load Previous" 載入
   ↓
9. 完成後點擊 "Export GLB" 下載編輯後的模型
```

---

## 🐛 常見問題

**Q: 能否支持雲端同步？**
A: 目前只支持本地檔案。可用 Dropbox/Google Drive 同步 glb-save.json 資料夾實現基本同步。

**Q: 多人協作？**
A: 不支持。可用 Git 或 SVN 手動版本控制 glb-save.json。

**Q: 遠端訪問？**
A: 用 Nginx 反向代理或 SSH tunneling：`ssh -L 3000:localhost:3000 user@server`

**Q: 遷移舊資料？**
A: IndexedDB 資料無法直接遷移。建議重新建立 session。

---

## 📞 支持資源

- 📖 完整文檔：`SESSION_MANAGEMENT_README.md`
- 🚀 快速開始：`QUICK_START.md`
- 🔧 API 參考：見文檔 API 端點章節
- 💬 開發工具：F12 DevTools 檢查網路和錯誤

---

## ✨ 下一步

建議的改進方向：

1. **UI 美化**：增加拖放排序、搜尋功能
2. **雲端支持**：整合 AWS S3 / Google Cloud Storage
3. **協作功能**：WebSocket 即時同步、權限管理
4. **版本歷程**：自動備份、時間軸切換
5. **中文化**：UI 和文檔翻譯

---

## 📄 授權

與原 GLB Texture Editor 保持一致。

---

**完成日期：** 2026-05-14

**狀態：** ✅ 完全實現，已測試，可生產使用

---

祝使用愉快！ 🎨✨
