# 🚦 智慧交通燈控制系統 v4.0

[![部署狀態](https://img.shields.io/badge/deploy-active-success)](https://me0608623.github.io/pico_traffic/)
[![授權](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Three.js Tesla Cybertruck 交通模擬系統 - 結合 Pico W 硬體控制與 AI 決策的智慧交通系統

**🌐 線上展示：** https://me0608623.github.io/pico_traffic/

---

## 📸 專案預覽

- ✅ 3D Tesla Cybertruck 模型
- ✅ 真實的紅綠燈控制邏輯
- ✅ 智能車輛避障與重疊檢測
- ✅ 黃燈邏輯（已越過停止線的車輛繼續通過）
- ✅ 動態車流生成系統
- ✅ 支援 Pico W 硬體連接
- ✅ 可切換多個車輛模型

---

## 🚀 快速開始

### 方法 1：線上訪問（推薦）

直接訪問：**https://me0608623.github.io/pico_traffic/**

無需安裝任何東西！

### 方法 2：本地運行

#### 前置需求
- Python 3 或 Node.js

#### 使用 Python
```bash
cd pico_traffic
python3 -m http.server 8000
# 訪問 http://localhost:8000/index.html
```

#### 使用 Node.js
```bash
cd pico_traffic
npx http-server -p 8000
# 訪問 http://localhost:8000/index.html
```

---

## 📋 專案結構

```
pico_traffic/
├── index.html              # 主程序（包含所有代碼）
├── tesla_cybertruck.glb    # Tesla Cybertruck 3D 模型（預設）
├── tesla_cybertruck2.glb   # 備用模型 2
├── tesla_cybertruck3.glb   # 備用模型 3
├── README.md               # 專案說明
├── 打包說明.txt            # 部署與分享指南
└── .github/
    └── workflows/
        └── deploy.yml      # GitHub Actions 自動部署配置
```

---

## 🎮 使用說明

### 1️⃣ 基本操作

1. **設定車流量**
   - 使用滑桿調整四個方向（北、南、東、西）的車流量
   - 每個方向可設定：低、中、高三種流量

2. **啟動系統**
   - 點擊「📡 發送至 Pico W」連接硬體（需要 Pico W）
   - 或點擊「測試南北向」/「測試東西向」按鈕測試

3. **觀察模擬**
   - 車輛會根據紅綠燈狀態自動停止或通過
   - 右側面板顯示系統狀態、燈號倒數等資訊

4. **切換模型**
   - 使用「車輛模型選擇」下拉選單切換不同的 Tesla Cybertruck 模型

5. **重置系統**
   - 點擊左下角「🔄 重置所有車輛」清空所有車輛

### 2️⃣ 連接 Pico W（選用）

如果有實體 Pico W 設備：

1. 確保 Pico W 已連接到網路
2. 輸入 Pico W 的 IP 位址和連接埠
3. 點擊「發送至 Pico W」
4. 系統會將車流數據發送到硬體，並接收 AI 決策

---

## 🚦 交通規則

### 車輛行為

- **🟢 綠燈**：車輛加速通過路口
- **🟡 黃燈**：
  - 未越過停止線 → 減速停止
  - 已越過停止線 → 繼續通過（不會停在路口中間）
- **🔴 紅燈**：車輛停在停止線前

### 智能避障

- ✅ 同一方向的車輛不會在生成位置重疊
- ✅ 停在紅燈前的車輛不會重疊
- ✅ 最多同時顯示 10 輛車
- ✅ 車輛間保持安全距離

### 車流生成規則

| 流量等級 | 生成間隔 | 說明 |
|---------|---------|------|
| **低** | 3 秒 | 輕鬆的交通流量 |
| **中** | 1.5 秒 | 適中的交通流量 |
| **高** | 0.8 秒 | 繁忙的交通流量 |

---

## 🔧 技術架構

### 前端技術

- **框架**：Three.js v0.159.0
- **3D 模型**：GLTF (.glb)
- **渲染器**：WebGL
- **控制器**：OrbitControls
- **物理**：自定義車輛運動邏輯

### 核心功能

1. **車輛系統**
   - 動態生成與銷毀
   - 速度與加速度控制
   - 停止線檢測
   - 路口通過邏輯

2. **燈號系統**
   - 紅綠燈狀態管理
   - 倒數計時器
   - 黃燈過渡邏輯
   - 互鎖機制（南北向與東西向互斥）

3. **重疊檢測**
   - 生成位置檢測
   - 停止線附近檢測
   - 車道內距離檢測

4. **模型系統**
   - 多模型支援
   - 動態旋轉補償
   - 高度偏移調整

---

## 🌐 部署方式

### GitHub Pages（已配置）

本專案已配置 GitHub Actions 自動部署：

1. 推送代碼到 `main` 或 `final` 分支
2. GitHub Actions 自動構建並部署
3. 2-3 分鐘後可訪問：https://me0608623.github.io/pico_traffic/

### 本地伺服器

#### Python
```bash
python3 -m http.server 8000 --bind 0.0.0.0
# 區域網路訪問：http://你的IP:8000/index.html
```

#### Node.js
```bash
npx http-server -p 8000 -a 0.0.0.0
# 區域網路訪問：http://你的IP:8000/index.html
```

### 其他部署選項

- **Netlify**: `netlify deploy --prod`
- **Vercel**: `vercel --prod`
- **Cloudflare Pages**: 連接 GitHub 倉庫自動部署

---

## 🛠️ 開發指南

### 克隆專案

```bash
git clone git@github.com:me0608623/pico_traffic.git
cd pico_traffic
```

### 修改代碼

所有代碼都在 `index.html` 中：

- **車輛生成速率**：搜尋 `SPAWN_RATE`
- **車輛速度**：搜尋 `maxSpeed`, `acceleration`
- **車輛上限**：搜尋 `vehicles.length >= 10`
- **模型旋轉**：搜尋 `modelRotationOffset`
- **停止線位置**：搜尋 `stopLines`

### 提交更新

```bash
git add .
git commit -m "更新說明"
git push origin final
```

GitHub Pages 會自動重新部署！

---

## 🔍 故障排除

### 問題 1：模型無法載入

**症狀**：顯示灰色方塊代替車輛

**解決方法**：
1. ✅ 確認 `.glb` 文件存在
2. ✅ 使用本地伺服器（不要直接打開 HTML）
3. ✅ 檢查瀏覽器控制台（F12）錯誤訊息
4. ✅ 確認網路連接（需載入 Three.js CDN）

### 問題 2：車輛重疊

**症狀**：多輛車輛在同一位置

**解決方法**：
1. 點擊「🔄 重置所有車輛」
2. 重新整理頁面（F5）

### 問題 3：車輛停在路口

**症狀**：黃燈時車輛停在路口中間

**解決方法**：
- ✅ 本專案已修正此問題
- ✅ 已越過停止線的車輛會繼續通過
- ✅ 如仍有問題，請重新整理頁面並強制刷新緩存（Ctrl+Shift+R）

### 問題 4：無法連接 Pico W

**症狀**：顯示連線錯誤

**解決方法**：
1. ✅ 確認 Pico W 已開機並連接網路
2. ✅ 確認 IP 位址正確
3. ✅ 確認電腦和 Pico W 在同一網路
4. ✅ 使用測試按鈕（不需要 Pico W）

### 問題 5：網站顯示舊版本

**症狀**：修改後網站沒有更新

**解決方法**：
1. ✅ 強制刷新：`Ctrl + Shift + R`（Windows/Linux）或 `Cmd + Shift + R`（Mac）
2. ✅ 清除瀏覽器緩存
3. ✅ 檢查 GitHub Actions 是否部署完成
4. ✅ 等待 2-3 分鐘讓 CDN 更新

---

## 💻 瀏覽器支援

| 瀏覽器 | 版本 | 支援程度 |
|--------|------|---------|
| Chrome | 90+ | ✅ 完全支援 |
| Firefox | 88+ | ✅ 完全支援 |
| Safari | 14+ | ✅ 完全支援 |
| Edge | 90+ | ✅ 完全支援 |
| Opera | 76+ | ✅ 完全支援 |

---

## 📦 檔案大小

| 檔案 | 大小 | 說明 |
|------|------|------|
| `index.html` | 81 KB | 主程序 |
| `tesla_cybertruck.glb` | 60 MB | 主要 3D 模型 |
| `tesla_cybertruck2.glb` | 398 KB | 備用模型 2 |
| `tesla_cybertruck3.glb` | 590 KB | 備用模型 3 |
| **總計（最小）** | **~60 MB** | index.html + 主模型 |
| **總計（完整）** | **~61 MB** | 包含所有模型 |

> ⚠️ 注意：`tesla_cybertruck.glb` (60MB) 超過 GitHub 建議的 50MB，但仍可正常使用。

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 開發流程

1. Fork 本專案
2. 創建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

---

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

---

## 🎓 學習資源

### Three.js
- [Three.js 官方文檔](https://threejs.org/docs/)
- [Three.js 範例](https://threejs.org/examples/)

### GLTF 模型
- [glTF 官方網站](https://www.khronos.org/gltf/)
- [Sketchfab](https://sketchfab.com/) - 免費 3D 模型

### WebGL
- [WebGL 基礎教程](https://webglfundamentals.org/)

---

## 🌟 致謝

- **Three.js** - 3D 圖形庫
- **GitHub Pages** - 免費託管服務
- **Pico W** - 硬體控制平台

---

## 📧 聯繫方式

- **GitHub**: [@me0608623](https://github.com/me0608623)
- **Email**: me0608623@gmail.com
- **專案網址**: https://me0608623.github.io/pico_traffic/

---

## 📝 更新日誌

### v4.0 (2025-12-12)
- ✅ 完整的 Tesla Cybertruck 3D 模型
- ✅ 智能重疊檢測系統
- ✅ 黃燈邏輯優化（路口內車輛繼續通過）
- ✅ 多模型支援與旋轉補償
- ✅ GitHub Pages 自動部署
- ✅ 完整的文檔與部署指南

---

<p align="center">
  <strong>🚗 開發者：AA 團隊 | 版本：v4.0 | 更新：2025-12-12 🚦</strong>
</p>

<p align="center">
  Made with ❤️ using Three.js and Pico W
</p>
