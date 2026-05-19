# Accessory Texture Editor Guide

## 新增功能概述

GLB Texture Editor 现已支持为 **Accessories（配件）** 编辑和替换纹理！

### 功能列表

✅ **为 Accessories 应用纹理** - 选中 accessory 后，编辑其所有纹理  
✅ **纹理预览** - 查看当前纹理的预览图  
✅ **纹理替换** - 上传新的纹理图片（PNG、JPEG、WebP）  
✅ **纹理恢复** - 一键恢复到原始纹理  
✅ **Export 包含纹理** - 导出时所有纹理都被烘焙进 GLB  

---

## 使用步骤

### 1️⃣ 加载主模型

- 点击 **"Choose GLB"** 或拖放 `.glb` 文件
- 等待模型加载完成

### 2️⃣ 选择附加节点

- 在 **"🔗 Attach Accessory GLB"** 区域
- 点击左边的节点列表选择目标节点（Bone 或 Mesh）
- 你会看到该节点高亮显示在 3D 视图中

### 3️⃣ 附加 Accessory

- 点击 **"Choose Accessory GLB"** 选择 accessory 文件
- 选择后 accessory 会自动添加到节点
- 系统会进入 Transform 编辑模式

### 4️⃣ ✨ 编辑 Accessory 纹理 ✨ (新功能)

当编辑 accessory 时，你会在 **Transform 控制下方** 看到新的 **"🎨 Textures"** 部分：

```
🎨 Textures
├── Base Color (map)          [Preview] [Replace] [Revert]
├── Normal Map                [Preview] [Replace] [Revert]
├── Metalness                 [Preview] [Replace] [Revert]
└── ... 其他纹理 slots
```

#### 替换纹理步骤：

1. 在 **"🎨 Textures"** 区域找到要修改的纹理 slot
2. 点击 **"Replace"** 按钮
3. 选择新的纹理文件（PNG、JPEG 或 WebP）
4. 预览会自动更新，3D 视图中的 accessory 也会实时显示新纹理

#### 恢复纹理：

- 点击 **"Revert"** 按钮恢复该 slot 的原始纹理

### 5️⃣ 微调 Transform（可选）

- **Position** - 调整位置 (X, Y, Z)
- **Rotation** - 调整旋转角度（度数）
- **Scale** - 调整大小比例
- 点击 **"📋 Record"** 保存当前 transform 配置

### 6️⃣ 导出包含纹理的 GLB

- 点击 **"Export GLB"** 按钮
- 所有 accessories 及其应用的纹理都会被烘焙到输出文件中
- 文件名为：`{原始模型名}_edited.glb`

---

## 保存和恢复会话

### 保存会话

1. 完成所有 accessories 编辑后，点击 **"💾 Save Session"**
2. 输入会话名称（例如："Character_with_gear_v1"）
3. 点击 **"New Session"** 保存

**注意：** 会话保存的是：
- ✅ Main GLB 路径
- ✅ 每个 Accessory 的路径和 transform
- ✅ Transform record 信息
- ⚠️ **NOT** 纹理数据（为了保持文件大小小）

### 恢复会话

1. 点击 **"📂 Load Session"**
2. 从列表中选择一个会话
3. 所有 accessories 会自动加载并恢复到保存时的 transform
4. **纹理会是原始状态**，如需修改需要重新应用

---

## 工作流建议

### 场景 A：编辑单个 Accessory

```
1. 加载主模型
2. 选择节点 → 附加 accessory
3. 点击 "Edit" 编辑
4. 修改 Transform 和纹理
5. 点击 "Export GLB" 导出
```

### 场景 B：完整角色装备

```
1. 加载主模型
2. 多次附加不同 accessories 到不同节点
3. 逐个编辑每个 accessory 的 transform 和纹理
4. 点击 "💾 Save Session" 保存完整装备配置
5. 点击 "Export GLB" 导出完整模型
```

### 场景 C：快速迭代

```
1. 加载之前保存的会话
2. 点击单个 accessory 的 "Edit"
3. 调整纹理或位置
4. Export
5. (需要时) 再次保存会话
```

---

## 技术细节

### 纹理 Slots 说明

| Slot 名称 | 用途 | 色彩空间 |
|-----------|------|---------|
| `map` | Base Color (基础颜色) | sRGB |
| `normalMap` | Normal Map (法线贴图) | Linear |
| `roughnessMap` | Roughness (粗糙度) | Linear |
| `metalnessMap` | Metalness (金属度) | Linear |
| `aoMap` | Ambient Occlusion | Linear |
| `emissiveMap` | Emissive (自发光) | sRGB |
| `alphaMap` | Alpha (透明度) | Linear |
| `bumpMap` | Bump Map (凹凸贴图) | Linear |
| `displacementMap` | Displacement (位移) | Linear |

### 支持的纹理格式

- ✅ PNG (推荐，支持透明度)
- ✅ JPEG (推荐用于无透明度的纹理)
- ✅ WebP (现代格式，文件更小)

### 文件大小优化

- **Session 文件** 不包含纹理二进制数据，保持较小
- **Exported GLB** 包含所有应用的纹理，文件较大但完整
- **Accessories** 可选择是否上传到 `model/` 文件夹

---

## 常见问题

### Q: 保存会话后，纹理会被保存吗？

**A:** 否。会话保存的是 transform 和配置，纹理修改**仅在当前编辑会话中保持**。重新加载会话时，纹理会恢复到原始状态。这样做是为了保持会话文件较小。

### Q: 如何长期保存带纹理的模型？

**A:** 使用 **"Export GLB"** 功能。导出的文件会包含所有当前应用的纹理，可以永久保存。

### Q: 可以一次替换多个 accessories 的纹理吗？

**A:** 目前需要逐个编辑。点击每个 accessory 的 "Edit" 按钮，分别修改其纹理。

### Q: 纹理替换失败了怎么办？

**A:** 检查以下几点：
- 文件格式是否正确（PNG、JPEG 或 WebP）
- 文件是否损坏
- 浏览器控制台是否有错误信息（F12 打开开发工具）

### Q: 如何恢复不小心修改的纹理？

**A:** 在该纹理 slot 右侧点击 **"Revert"** 按钮即可。

---

## 相关代码文件

- **主文件** `editor.html`
- **关键函数：**
  - `buildAccessoryTextureSlots()` - 扫描 accessory 的纹理
  - `renderAccessoryTextureSlots()` - 渲染纹理编辑 UI
  - `replaceAccessoryTexture()` - 替换纹理
  - `exportCurrentGlb()` - 导出包含纹理的 GLB

---

## 更新日志

### v3.0 - Accessory Texture Support (Latest)

✨ **新增功能：**
- 为 Accessories 添加纹理编辑界面
- 支持替换和恢复单个纹理 slots
- Export 时自动烘焙 accessory 纹理
- 实时纹理预览

🔧 **优化：**
- mainGlb 不再保存二进制 buffer（仅保存路径）
- Accessory 纹理编辑 UI 集成到 Transform 控制面板
- 改进的纹理加载性能

---

## 使用建议

1. **定期保存** - 使用 "💾 Save Session" 保存你的装备配置
2. **定期导出** - 完成编辑后立即 "Export GLB"，防止意外丢失
3. **组织管理** - 为不同的变体创建不同的会话名称
4. **质量检查** - 导出前在 3D 视图中检查效果

---

## 技术支持

如遇到问题，请检查：
- 浏览器控制台错误（F12 打开开发工具）
- 文件路径是否正确
- GLB 文件是否有效
- 网络连接状态（如使用远程服务器）

祝你使用愉快！ 🎉
