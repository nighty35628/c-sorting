[简体中文](#c-sorting) | [English](#c-sorting-en)

# C-SORTING

**C-SORTING** 是一款基于 PyQt6 开发的现代化智能照片分类工具，采用极简主义设计，旨在帮助用户快速整理杂乱的照片库。

## 🌟 核心功能

- **极简 UI**：采用流畅的 PyQt6 动画、侧边栏导航和圆角卡片布局。
- **智能分类**：
  - **按日期**：精确到天（YYYY-MM-DD）。
  - **按月份**：将照片按月归档（YYYY-MM）。
  - **按地点**：读取 EXIF GPS 信息，调用腾讯地图服务自动识别城市名称。
- **个性化设置**：内置 10 种配色方案，支持一键切换**深色模式**。
- **历史记录**：自动记录处理任务，方便一键打开目标文件夹。
- **多语言**：完整支持简体中文与英文。
- **无损整理**：支持“保留原文件（复制）”或“移动文件”模式。
- **高性能**：采用异步多线程处理，大批量照片整理时界面不卡顿。

## 🚀 快速开始

### 方式 A：直接运行 (推荐)
已提供打包好的单文件版本，无需安装 Python 环境。
1. 进入 `dist/` 文件夹。
2. 运行 `C-SORTING.exe` 即可开始使用。

### 方式 B：开发者模式 (源码运行)
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

## 🛠️ 项目结构

- `src/`：源代码
  - `gui/app.py`：现代化的 PyQt6 界面逻辑、主题引擎与翻译系统。
  - `sorter.py`：核心分类算法（日期/月份/城市分析）。
  - `exif_utils.py`：照片 EXIF 元数据解析（时间、GPS）。
  - `geocode.py`：地理编码服务，集成腾讯地图 WebService API。
  - `models/`：预留 AI 识别接口（如人脸/物体识别）。
- `dist/`：发布版本目录。
- `assets/`：程序图标与内部资源。
- `config.json`：用户配置持久化（主题色、语言、深色模式）。
- `history.json`：处理历史数据。

## 📝 注意事项

- **网络要求**：使用“按地理位置”分类时需连接互联网。
- **配置文件**：程序会在所在目录下自动生成 `config.json` 和 `history.json` 以保存您的偏好和历史记录。

## 许可证
MIT

---

# C-SORTING <a id="c-sorting-en"></a>

**C-SORTING** is a modern intelligent photo sorting tool developed based on PyQt6, featuring a minimalist design aimed at helping users quickly organize cluttered photo libraries.

## 🌟 Core Features

- **Minimalist UI**: Utilizes smooth PyQt6 animations, sidebar navigation, and rounded corner card layouts.
- **Smart Sorting**:
  - **By Date**: Precision to the day (YYYY-MM-DD).
  - **By Month**: Archives photos by month (YYYY-MM).
  - **By Location**: Reads EXIF GPS information and uses Tencent Maps service to automatically identify city names.
- **Personalized Settings**: Built-in 10 color schemes, supporting one-click switching to **Dark Mode**.
- **History**: Automatically records processing tasks for easy one-click opening of target folders.
- **Multi-language**: Full support for Simplified Chinese and English.
- **Lossless Organization**: Supports "Keep original files (Copy)" or "Move files" modes.
- **High Performance**: Uses asynchronous multi-threaded processing, ensuring the interface remains responsive during bulk photo organization.

## 🚀 Quick Start

### Option A: Run Directly (Recommended)
A packaged single-file version is provided; no Python environment installation is required.
1. Enter the `dist/` folder.
2. Run `C-SORTING.exe` to start using it.

### Option B: Developer Mode (Run from Source)
1. After cloning the project, create and activate a virtual environment in the root directory:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install dependencies:
```powershell
pip install -r requirements.txt
```
3. Start the program:
```powershell
python src/main.py
```

## 🛠️ Project Structure

- `src/`: Source Code
  - `gui/app.py`: Modern PyQt6 interface logic, theme engine, and translation system.
  - `sorter.py`: Core sorting algorithm (Date/Month/City analysis).
  - `exif_utils.py`: Photo EXIF metadata parsing (Time, GPS).
  - `geocode.py`: Geocoding service, integrated with Tencent Maps WebService API.
  - `models/`: Reserved for AI recognition interfaces (e.g., face/object recognition).
- `dist/`: Distribution directory.
- `assets/`: Program icons and internal resources.
- `config.json`: User configuration persistence (Theme color, language, dark mode).
- `history.json`: Processing history data.

## 📝 Notes

- **Network Requirements**: An internet connection is required when using "By Location" sorting.
- **Configuration Files**: The program automatically generates `config.json` and `history.json` in its directory to save your preferences and history.

## License
MIT

