# GLB Texture Editor - Session Management

改造了 GLB Texture Editor，將 IndexedDB 自動儲存改為伺服器 API，支持多個 session 記錄保存和載入。

## 新功能

✅ **多個 Session 記錄**  
- 支持保存多個 GLB + accessories 組合
- 每個 session 有名字、保存時間、配件數量

✅ **Save as / Overwrite**  
- 新建 session：自動命名或自訂名稱
- 覆寫已有 session：選擇要覆蓋的 session ID

✅ **Load Previous**  
- 列出所有已保存 session
- 選擇要載入的 session ID
- 自動恢復 GLB 和所有 accessories

✅ **手動編輯配置**  
- 所有 session 存在 `glb-save.json` 檔案
- 可用文字編輯器手動修改
- 重新載入頁面自動讀取

✅ **無 IndexedDB 限制**  
- IndexedDB 有容量限制（通常 50MB）
- JSON 檔案可無限擴展
- 方便備份和版本控制

---

## 使用方法

### 方法 1: Node.js 伺服器（推薦）

**前置需求：** Node.js 已安裝

```bash
cd e:/CyberpunkRealm/doc/3dmodel_editor
node server.js
# 或指定埠
node server.js 8080
```

然後開啟瀏覽器：`http://localhost:3000`

### 方法 2: Python Flask 伺服器

**前置需求：** Python 3.7+，已安裝 Flask 和 flask-cors

```bash
# 安裝依賴
pip install flask flask-cors

cd e:/CyberpunkRealm/doc/3dmodel_editor
python server.py
# 或指定埠
python server.py 8080
```

然後開啟瀏覽器：`http://localhost:3000`

### 方法 3: 簡單 HTTP 伺服器（無 API 支持）

如果只是想預覽 HTML（不支持 session 儲存）：

```bash
cd e:/CyberpunkRealm/doc/3dmodel_editor

# 用 Python
python -m http.server 3000

# 或 Node.js
npx http-server -p 3000
```

---

## 工作流程

### 1. **載入 GLB**
   - 點擊 "Drop a .glb file here" 或拖放 .glb 檔案
   - 編輯紋理、附加配件、調整位置

### 2. **保存 Session**
   - 點擊 "💾 Save Session" 按鈕
   - 輸入 session 名稱（預設為 GLB 檔名 + 時間戳）
   - 選擇 "New Session" 建立新記錄
   - 或選擇 "Overwrite" 覆蓋已有 session

### 3. **載入已保存 Session**
   - 初次載入會顯示 "🔄 Restore Previous Session" 橫幅
   - 點擊 "Load Previous" 選擇要載入的 session
   - 自動載入 GLB 和所有 accessories

### 4. **手動編輯**
   - 用文字編輯器打開 `glb-save.json`
   - 修改 session 名稱、transform 值、刪除記錄等
   - 重新載入頁面自動讀取最新配置

---

## glb-save.json 格式

```json
{
  "sessions": [
    {
      "name": "Character v1",
      "savedAt": 1715644800000,
      "mainGlb": {
        "name": "character.glb",
        "buffer": [71, 76, 84, 70, 2, 0, ...]  // Base64 或陣列
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

### 關鍵欄位

| 欄位 | 說明 |
|------|------|
| `name` | Session 顯示名稱 |
| `savedAt` | 保存時間戳 (ms) |
| `mainGlb.name` | 主 GLB 檔名 |
| `mainGlb.buffer` | GLB 二進制資料（陣列）|
| `accessories` | 附加配件陣列 |
| `nodeName` | 配件附加到的骨骼名稱 |
| `transform` | 位置 (px/py/pz)、旋轉 (rx/ry/rz°)、縮放 (sx/sy/sz) |
| `record` | 紀錄過的最終位置（用於預覽）|

---

## API 端點

### GET `/api/sessions`
列出所有已保存 session

**Response:**
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
保存或覆蓋 session

**Request Body:**
```json
{
  "name": "Character v1",
  "mainGlb": { "name": "...", "buffer": [...] },
  "accessories": [...],
  "mode": "new",
  "overwriteId": null
}
```

### GET `/api/session/load?id=0`
載入指定 session

### DELETE `/api/session/delete?id=0`
刪除指定 session

### GET `/api/raw-save`
取得原始 JSON（用於調試）

---

## 常見問題

### Q: 何時使用 Node.js vs Python?
- **Node.js**：更輕量，不需額外安裝，推薦
- **Python**：如果已有 Python 環境，方便整合其他工具

### Q: 支持多人協作嗎？
- 不支持。單個 glb-save.json 檔案同時只能一個伺服器讀寫

### Q: Buffer 過大會怎樣？
- JSON 檔案大小通常不是問題（GB 級別也沒問題）
- 但載入速度會變慢，建議定期整理舊 session

### Q: 可以備份和版本控制嗎？
- 是的，glb-save.json 是純 JSON，可用 Git 管理
- `git diff` 可看到每次修改

### Q: 如何加入新欄位？
- 編輯 `glb-save.json` 直接加入欄位
- 伺服器會自動保存（不驗證結構）

---

## 檔案結構

```
3dmodel_editor/
├── editor.html      # 修改後的編輯器 UI
├── server.js                       # Node.js 伺服器
├── server.py                       # Python Flask 伺服器
├── glb-save.json                   # Session 儲存檔案
└── data/
    └── sprite.json                 # VFX 配置（現有）
```

---

## 技術實現

### 改動點

1. **移除 IndexedDB**
   - 原來用 IndexedDB 儲存 session
   - 現在改用 REST API 到伺服器

2. **加入 Server API**
   - `/api/sessions` - 列表
   - `/api/session/save` - 保存
   - `/api/session/load` - 載入
   - `/api/session/delete` - 刪除

3. **UI 改進**
   - 新增 "💾 Save Session" 按鈕
   - Save dialog 支持 New/Overwrite 選擇
   - Load dialog 支持選擇 session ID

4. **Session 恢復**
   - 改用 fetch API 呼叫伺服器
   - 支持選擇要載入的 session
   - 自動還原 GLB + accessories

---

## 進階

### 建立 Systemd Service (Linux)

建立 `/etc/systemd/system/glb-editor.service`:
```ini
[Unit]
Description=GLB Texture Editor Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/3dmodel_editor
ExecStart=/usr/bin/node server.js 3000
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
sudo systemctl start glb-editor
sudo systemctl enable glb-editor
```

### 反向代理 (Nginx)

```nginx
server {
    listen 80;
    server_name glb-editor.local;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
```

---

## 更新歷程

### v2.0 (Current)
- ✅ 改為伺服器 API 儲存
- ✅ 支持多 session 記錄
- ✅ Save as / Overwrite UI
- ✅ Node.js 和 Python 伺服器
- ✅ 手動 JSON 編輯支持

### v1.0 (Previous)
- IndexedDB 自動儲存
- 單個 session 恢復

---

## 需要幫助？

如有問題或建議，請檢查：
1. 伺服器是否正常運行（檢查終端輸出）
2. 瀏覽器 DevTools (F12) 是否有錯誤
3. glb-save.json 是否可讀寫
4. 埠號 3000 是否被佔用

---

**祝使用愉快！** 🎨✨
