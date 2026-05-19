# GLB Texture Editor - 快速開始

## 快速啟動

### 使用 Node.js（推薦）

```bash
cd e:/CyberpunkRealm/doc/3dmodel_editor
node server.js
```

打開瀏覽器：`http://localhost:3000`

---

### 使用 Python

```bash
# 安裝依賴（首次）
pip install flask flask-cors

cd e:/CyberpunkRealm/doc/3dmodel_editor
python server.py
```

打開瀏覽器：`http://localhost:3000`

---

## 主要功能

| 功能 | 說明 |
|------|------|
| **Drop GLB** | 拖放或選擇 .glb 檔案 |
| **Edit Textures** | 下載、替換、還原紋理 |
| **Attach Accessories** | 附加其他 GLB 到骨骼 |
| **Transform** | 調整位置、旋轉、縮放 |
| **Save Session** | 保存當前狀態到 glb-save.json |
| **Load Previous** | 載入已保存的 session |
| **Export GLB** | 匯出編輯後的 GLB（含 accessories） |

---

## 操作流程

### 1️⃣ 載入 GLB

```
點擊 "Choose GLB" 或拖放 .glb 檔案
↓
編輯器會自動掃描紋理和骨骼
```

### 2️⃣ 附加配件

```
1. 在左方選擇目標骨骼（e.g., Head、Spine）
2. 點擊 "Choose Accessory GLB"
3. 調整位置 (Pos)、旋轉 (Rot)、縮放 (Scale)
4. 點擊 "Record" 保存設定
```

### 3️⃣ 保存進度

```
點擊 "💾 Save Session"
↓
輸入 session 名稱（或使用預設）
↓
選擇 "New Session" 或 "Overwrite"
↓
保存到 glb-save.json
```

### 4️⃣ 載入已保存

```
初次開啟時會看到 "🔄 Restore Previous Session"
↓
點擊 "Load Previous"
↓
選擇要載入的 session ID
↓
自動還原 GLB + 所有 accessories
```

### 5️⃣ 匯出最終 GLB

```
完成編輯後，點擊 "Export GLB"
↓
自動下載 model_edited.glb（含 accessories）
```

---

## 檔案位置

```
e:/CyberpunkRealm/doc/3dmodel_editor/
├── editor.html        # 網頁編輯器
├── server.js                        # Node.js 伺服器
├── server.py                        # Python 伺服器
├── glb-save.json                    # 🔹 Session 儲存檔案
├── SESSION_MANAGEMENT_README.md     # 詳細文檔
└── QUICK_START.md                   # 本檔案
```

---

## glb-save.json 說明

自動保存所有 session 到 `glb-save.json`:

```json
{
  "sessions": [
    {
      "name": "My Character v1",
      "savedAt": 1715644800000,
      "mainGlb": { "name": "character.glb", "buffer": [...] },
      "accessories": [
        {
          "name": "helmet.glb",
          "nodeName": "Head",
          "transform": { "px": 0, "py": 0.5, "pz": 0, ... }
        }
      ]
    }
  ]
}
```

**可直接編輯此檔案：**
- 修改 session 名稱
- 刪除不需要的 session
- 重新載入頁面自動讀取

---

## 常見操作

### 🔄 切換多個角色

1. **Save Session "Character_A"**
2. **Drop 新 GLB（Character_B）**
3. **Attach accessories**
4. **Save Session "Character_B"**
5. **Click "Load Previous" 切換**

### 🎨 批量替換紋理

1. 在 "Texture Slots" 區域
2. 針對每個紋理槽點擊 "Replace"
3. 選擇新紋理檔案
4. 自動更新預覽

### 📋 複製所有配置

1. 點擊 "📋 Copy All Records"
2. 配置資料複製到剪貼板
3. 貼到備忘錄或共享文件

### 💾 匯出配置為 JSON

1. 打開 `glb-save.json`
2. 複製需要的 session
3. 分享或備份

---

## 進階技巧

### 🔌 API 呼叫

```javascript
// 列出所有 session
fetch('http://localhost:3000/api/sessions')
  .then(r => r.json())
  .then(d => console.log(d.sessions))

// 載入特定 session
fetch('http://localhost:3000/api/session/load?id=0')
  .then(r => r.json())
  .then(d => console.log(d.session))
```

### 🗂️ 備份 Session

```bash
# 複製 glb-save.json 到備份位置
cp glb-save.json glb-save.backup.json

# 或用 Git 追蹤
git add glb-save.json
git commit -m "Save character setup v2"
```

### 🚀 部署到遠端

```bash
# 遠端伺服器上執行
ssh user@server "cd glb-editor && node server.js"

# 或用 Nginx 反向代理
# 見 SESSION_MANAGEMENT_README.md 的 Advanced 章節
```

---

## 除錯

### 伺服器未響應

```bash
# 檢查 Node.js 是否安裝
node --version

# 檢查埠 3000 是否被佔用
lsof -i :3000          # macOS/Linux
netstat -ano | findstr :3000  # Windows

# 改用其他埠
node server.js 8080
```

### Session 無法保存

```bash
# 檢查 glb-save.json 權限
ls -la glb-save.json

# 確保檔案可寫
chmod 666 glb-save.json

# 檢查瀏覽器 DevTools (F12) 是否有錯誤
```

### 附件載入失敗

1. 檢查 .glb 檔案是否有效
2. 檢查骨骼名稱是否正確拼寫
3. 查看 DevTools 的 Network 標籤

---

## 快捷鍵

| 快捷鍵 | 功能 |
|--------|------|
| `Ctrl/Cmd + S` | 保存 session（如果實現） |
| `R` | 重置 camera |
| `F12` | 打開開發者工具 |

---

## 需要幫助？

📖 **詳細文檔：** `SESSION_MANAGEMENT_README.md`

🐛 **檢查清單：**
- [ ] Node.js 或 Python 已安裝
- [ ] 伺服器正在運行
- [ ] 瀏覽器開啟 `http://localhost:3000`
- [ ] glb-save.json 存在且可讀寫

---

**開始編輯吧！** ✨🎨
