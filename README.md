[简体中文](#c-sorting) | [English](#c-sorting-en)

# C-SORTING

**C-SORTING** 是一款基于 PyQt6 开发的现代化智能照片分类工具，采用极简主义设计，旨在帮助用户快速整理杂乱的照片库。

## 🌟 核心功能

- **极简 UI**：采用流畅的 PyQt6 动画、侧边栏导航和圆角卡片布局。
- **智能分类**：
  - **支持多种格式**：不仅支持照片（JPG, PNG, HEIC, WebP, BMP 等），还支持视频文件（MP4, MOV, AVI, MKV 等）。
  - **按日期**：精确到天（YYYY-MM-DD）。
  - **按月份**：将媒体按月归档（YYYY-MM）。
  - **按地点**：读取 EXIF GPS 信息，采用 **内置离线城市数据库**（337 个地级行政区坐标）自动识别最近的城市名。
  - **媒体分拣**：自动将照片和视频分流至不同的目标文件夹。
- **个性化设置**：内置 10 种配色方案，支持一键切换**深色模式**。
- **交互优化**：处理完成后可直接点击对话框中的“打开文件夹”按钮查看结果。
- **历史记录**：自动记录处理任务，方便一键打开目标文件夹。
- **多语言**：完整支持简体中文与英文。
- **无损整理**：支持“保留原文件（复制）”或“移动文件”模式。
- **高性能**：采用异步多线程处理，大批量照片整理时界面不卡顿。

## 🚀 快速开始

### Windows
1. 克隆项目后，在根目录下创建并激活虚拟环境：
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. 安装依赖：
```powershell
pip install -r requirements.txt
```
3. 启动程序：
```powershell
python src/main.py
```

### Linux (Arch Linux)
建议使用内置的打包方案安装，以获得原生菜单图标支持：
```bash
cd packaging/arch
makepkg -si
```

### Linux (Debian / Ubuntu)
你可以下载并安装预构建的 `.deb` 包：
```bash
sudo apt install ./packaging/debian/c-sorting_1.1.0-1_all.deb
```
安装后即可通过应用菜单或终端命令 `c-sorting` 直接运行。

## 🛠️ 项目结构

- `src/`：源代码
  - `gui/app.py`：现代化的 PyQt6 界面逻辑、主题引擎与翻译系统。
  - `sorter.py`：核心分类算法（日期/月份/城市分析）。
  - `exif_utils.py`：照片 EXIF 元数据解析（时间、GPS）。
  - `geocode.py`：地理编码服务，内置 337 个中国地级行政区坐标的离线查询逻辑。
  - `models/`：预留 AI 识别接口（如人脸/物体识别）。
- `readme-history/`：存放历史版本的 README 文件。
- `assets/`：程序图标与内部资源。
- `config.json`：用户配置持久化（主题色、语言、深色模式）。
- `history.json`：处理历史数据。

## 📝 注意事项

- **离线支持**：得益于内置的轻量级城市坐标数据库，地理位置分类现在完全支持离线运行，无需互联网。
- **配置文件**：程序会在所在目录下自动生成 `config.json` 和 `history.json` 以保存您的偏好和历史记录。

## 🔄 版本更新

- **v1.1.0** (2026-02-20): 2026 年度大版本。
  - **增强格式支持**：支持 WebP, GIF, BMP, JFIF 等更多图片格式。
  - **增加视频分类**：支持 MP4, MOV, AVI, MKV 等主流视频分类。
  - **媒体分拣逻辑**：自动按媒体类型（照片/视频）分送不同的顶级文件夹。
  - **UI 交互改进**：任务结束后支持在弹窗内一键打开文件夹，统一了按钮视觉风格。
- **v1.0.8**: 重构地理分类逻辑。从腾讯地图 API 迁移至**内置本地城市数据库**方案，实现 100% 离线运行，显著提升隐私性与处理速度。

## 许可证
MIT

---

# C-SORTING <a id="c-sorting-en"></a>

**C-SORTING** is a modern intelligent photo sorting tool developed based on PyQt6, featuring a minimalist design aimed at helping users quickly organize cluttered photo libraries.

## 🌟 Core Features

- **Minimalist UI**: Utilizes smooth PyQt6 animations, sidebar navigation, and rounded corner card layouts.
- **Smart Sorting**:
  - **Multi-format Support**: Supports not only photos (JPG, PNG, HEIC, WebP, BMP, etc.) but also video files (MP4, MOV, AVI, MKV, etc.).
  - **By Date**: Precision to the day (YYYY-MM-DD).
  - **By Month**: Archives media by month (YYYY-MM).
  - **By Location**: Reads EXIF GPS information and identifies the nearest city using a **built-in offline city database** (337 prefecture-level cities).
  - **Media Sorting**: Automatically steers photos and videos into separate target folders.
- **Personalized Settings**: Built-in 10 color schemes, supporting one-click switching to **Dark Mode**.
- **Interaction Optimization**: One-click "Open Folder" button in the completion dialog for immediate results preview.
- **History**: Automatically records processing tasks for easy one-click opening of target folders.
- **Multi-language**: Full support for Simplified Chinese and English.
- **Lossless Organization**: Supports "Keep original files (Copy)" or "Move files" modes.
- **High Performance**: Uses asynchronous multi-threaded processing, ensuring the interface remains responsive during bulk photo organization.

## 🚀 Quick Start

### Windows
1. After cloning the project, create and activate a virtual environment in the root directory:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install dependencies:
```powershell
pip install -r requirements.txt
```
3. Run the program:
```powershell
python src/main.py
```

### Linux (Arch Linux)
It's recommended to use the built-in packaging solution for native menu icon support:
```bash
cd packaging/arch
makepkg -si
```

### Linux (Debian / Ubuntu)
You can download and install the pre-built `.deb` package:
```bash
sudo apt install ./packaging/debian/c-sorting_1.1.0-1_all.deb
```
Once installed, you can start it via the application menu or the terminal command `c-sorting`.
3. Start the program:
```powershell
python src/main.py
```

## 🛠️ Project Structure

- `src/`: Source Code
  - `gui/app.py`: Modern PyQt6 interface logic, theme engine, and translation system.
  - `sorter.py`: Core sorting algorithm (Date/Month/City analysis).
  - `exif_utils.py`: Photo EXIF metadata parsing (Time, GPS).
  - `geocode.py`: Geocoding service with a **built-in offline database** of 337 Chinese prefecture-level administrative regions.
  - `models/`: Reserved for AI recognition interfaces (e.g., face/object recognition).
- `readme-history/`: Archive of historical README files.
- `assets/`: Program icons and internal resources.
- `config.json`: User configuration persistence (Theme color, language, dark mode).
- `history.json`: Processing history data.

## 📝 Notes

- **Offline Support**: Thanks to the built-in lightweight city database, location-based sorting now fully supports offline operation, with no internet required.
- **Configuration Files**: The program automatically generates `config.json` and `history.json` in its directory to save your preferences and history.

## 🔄 Updates

- **v1.1.0** (2026-02-20): Major 2026 Release.
  - **Enhanced Format Support**: Supports WebP, GIF, BMP, JFIF, and more.
  - **Video Classification**: Added support for major formats like MP4, MOV, AVI, and MKV.
  - **Media Steering**: Automatically organizes photos and videos into designated top-level folders.
  - **UX Improvements**: Added "Open Folder" button to completion dialog and unified button visual styles.
- **v1.0.8**: Major refactor of geocoding logic. Migrated from Tencent Maps API to a **built-in offline city database**, enabling 100% offline operation with improved privacy and speed.

## License
MIT

