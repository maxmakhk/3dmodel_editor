# GLB Texture Editor - 測試指南

## 🧪 完整測試流程

以下步驟可驗證所有功能正常運作。

---

## 步驟 1️⃣: 啟動伺服器

### Windows
```bash
cd e:/CyberpunkRealm/doc/3dmodel_editor
start-server.bat
```

### Linux / macOS
```bash
cd e:/CyberpunkRealm/doc/3dmodel_editor
chmod +x start-server.sh
./start-server.sh
```

### Python
```bash
pip install flask flask-cors
python server.py
```

**預期結果：**
```
╔════════════════════════════════════════════════════════════╗
║  GLB Texture Editor Server                                 ║
╠════════════════════════════════════════════════════════════╣
║  ✓ Node.js vXX.X.X found
║  🌐 Open browser: http://localhost:3000
```

---

## 步驟 2️⃣: 開啟編輯器

**操作：** 打開瀏覽器，進入 `http://localhost:3000`

**預期結果：**
- ✅ GLB Texture Editor 介面載入
- ✅ 主要面板顯示（Texture Slots、Node List、Attach Accessory 等）
- ✅ 工具列按鈕可見（💾 Save Session、Export GLB 預設禁用）

---

## 步驟 3️⃣: 檢查 glb-save.json

**操作：** 打開 `glb-save.json` 檔案

**預期結果：**
```json
{
  "sessions": []
}
```

（首次為空 session 陣列）

---

## 步驟 4️⃣: 載入 GLB 檔案

**操作：**
1. 準備一個測試 .glb 檔案（e.g. `character.glb`）
2. 拖放到 "Drop a .glb file here" 區域
   
   或
   
3. 點擊 "Choose GLB"

**預期結果：**
- ✅ 3D 模型顯示在預覽區
- ✅ Texture Slots 列表更新
- ✅ Node List 顯示骨骼和網格
- ✅ "Export GLB" 和 "💾 Save Session" 按鈕變成可用
- ✅ 狀態欄顯示 "Loaded XXX — N texture slots"

---

## 步驟 5️⃣: 測試保存功能

### 測試 5A: 新建 Session

**操作：**
1. 點擊 "💾 Save Session"
2. 輸入 session 名稱（e.g. "Test Session 1"）
3. 點擊 "New Session"

**預期結果：**
- ✅ Dialog 消失
- ✅ 狀態欄顯示 "Session 'Test Session 1' saved"
- ✅ 打開 `glb-save.json`，應看到 session 記錄
- ✅ 可看到 `mainGlb.name` 和 `accessories` 陣列

### 測試 5B: 覆寫 Session

**操作：**
1. 重新編輯模型（e.g. 換一個 GLB）
2. 點擊 "💾 Save Session"
3. 輸入相同名稱
4. 現在應該看到 "Overwrite" 按鈕
5. 看到現有 session 列表
6. 點擊 "Overwrite"
7. 輸入要覆寫的 ID (e.g. 0)

**預期結果：**
- ✅ 狀態欄顯示 "Session overwritten"
- ✅ glb-save.json 中 session [0] 被更新
- ✅ 之前的 GLB 資料被新資料替換

---

## 步驟 6️⃣: 測試載入功能

### 測試 6A: 檢查 Session 列表

**操作：**
1. 重新載入頁面 (F5 或 Ctrl+R)
2. 等待頁面載入完成

**預期結果：**
- ✅ 顯示 "🔄 Restore Previous Session" 橫幅
- ✅ 列出保存的所有 session（包括 ID、名稱、日期、配件數）
- ✅ "Load Previous" 按鈕可用

### 測試 6B: 載入特定 Session

**操作：**
1. 點擊 "Load Previous"
2. 彈出 prompt 提示選擇 session ID
3. 輸入要載入的 ID（e.g. 0）
4. 點擊 OK

**預期結果：**
- ✅ 3D 模型切換到對應 session 的 GLB
- ✅ 如果有 accessories，全部自動還原
- ✅ 狀態欄顯示 "Session loaded — N accessories"
- ✅ Transform 值恢復為保存時的設定

---

## 步驟 7️⃣: 測試附加配件

**操作：**
1. 載入 GLB
2. 在 Node List 中選擇一個骨骼（e.g. "Armature" 或 "Head"）
3. 點擊 "Choose Accessory GLB"
4. 選擇另一個 .glb 檔案（e.g. "accessory.glb"）
5. 調整 Position/Rotation/Scale
6. 點擊 "Record"

**預期結果：**
- ✅ 配件附加到骨骼並顯示在 3D 預覽
- ✅ "All Attached Accessories" 區域顯示配件清單
- ✅ 保存時，accessories 陣列包含此配件

---

## 步驟 8️⃣: 測試手動編輯

**操作：**
1. 打開 `glb-save.json`
2. 修改某個 session 的 `name` 欄位（e.g. "Test" → "Test_v2"）
3. 儲存檔案
4. 回到編輯器
5. 重新載入頁面 (F5)
6. 點擊 "Load Previous"

**預期結果：**
- ✅ Prompt 中顯示新的 session 名稱 "Test_v2"
- ✅ 手動編輯的改動生效
- ✅ glb-save.json 和編輯器已同步

---

## 步驟 9️⃣: 測試匯出

**操作：**
1. 完成編輯（GLB + accessories）
2. 點擊 "Export GLB"

**預期結果：**
- ✅ 狀態欄顯示 "Exported XXX_edited.glb (N accessories)"
- ✅ 瀏覽器自動下載 `.glb` 檔案
- ✅ 下載的檔案包含所有 accessories（baked in）

---

## 步驟 🔟: 壓力測試

**操作：**
1. 連續保存 5-10 個不同 session
2. 每次改變 GLB 或 accessories
3. 檢查 glb-save.json 是否持續增長
4. 測試載入每一個 session

**預期結果：**
- ✅ 所有 session 都能正確保存和載入
- ✅ glb-save.json 檔案大小合理（通常幾 MB）
- ✅ 沒有資料遺失或損壞
- ✅ 效能無明顯下降

---

## 檢查清單

- [ ] 伺服器正常啟動
- [ ] 編輯器載入無錯誤
- [ ] glb-save.json 存在且為空
- [ ] GLB 檔案成功載入
- [ ] Save Session 按鈕有效
- [ ] 新建 session 寫入 glb-save.json
- [ ] 覆寫 session 成功
- [ ] 重新載入顯示 session 列表
- [ ] 載入 session 還原所有資料
- [ ] 手動編輯 JSON 生效
- [ ] 附加配件正常工作
- [ ] Export GLB 成功下載
- [ ] 多個 session 不衝突
- [ ] DevTools 無紅色錯誤

---

## 🐛 故障排除

### 伺服器無法啟動

```bash
# 檢查 Node.js
node --version

# 檢查埠 3000 是否被佔用
netstat -ano | findstr :3000  # Windows
lsof -i :3000                  # macOS/Linux

# 改用其他埠
node server.js 8080
```

### 編輯器載入空白

```
1. F12 開啟 DevTools
2. 檢查 Console 標籤是否有紅色錯誤
3. 檢查 Network 標籤是否有請求失敗
4. 確保伺服器仍在運行
```

### glb-save.json 無法寫入

```bash
# 檢查檔案權限
ls -la glb-save.json

# 改為可寫
chmod 666 glb-save.json

# Windows: 右鍵 Properties → Security → Edit → Allow Full Control
```

### Session 無法載入

```
1. 檢查 DevTools → Network → /api/session/load
2. 確保 session ID 正確（0-based）
3. 檢查 glb-save.json 是否有 buffer 欄位
```

### 3D 模型不顯示

```
1. 確保 GLB 檔案有效
2. 嘗試不同的 GLB 檔案
3. 檢查 DevTools → Console 是否有加載錯誤
4. 試著旋轉 Camera（左鍵拖動）
```

---

## 📊 效能指標

測試環境：常見桌上型電腦

| 操作 | 預期時間 |
|------|----------|
| 伺服器啟動 | < 1 秒 |
| GLB 載入（10MB） | 2-5 秒 |
| Session 保存 | < 1 秒 |
| Session 載入 | 2-5 秒 |
| 頁面重新載入 | 2-3 秒 |

如明顯超時，檢查：
- 檔案大小是否過大
- 磁碟 I/O 是否堵塞
- 網路延遲

---

## ✅ 測試完成

如所有步驟都成功，表示：

✅ 伺服器正常運作
✅ 編輯器功能完整
✅ Session 管理系統可用
✅ 資料持久化正確
✅ 系統可投入使用

---

## 🎯 下一步

系統驗證完成後，可以：

1. **日常使用** - 正式開始編輯和保存模型
2. **備份策略** - 定期複製 glb-save.json 到備份位置
3. **版本控制** - 將 glb-save.json 納入 Git 管理
4. **團隊共享** - 共享 glb-save.json 檔案進行協作

---

**祝測試順利！** 🧪✨
