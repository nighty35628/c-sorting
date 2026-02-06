# C-SORTING

[简体中文](README.md) | [English](README.md#english)

**C-SORTING** 是一款基于 PyQt6 开发的现代化智能照片分类工具，采用极简主义设计，旨在帮助用户快速整理杂乱的照片库。

**C-SORTING** is a modern intelligent photo sorting tool built with PyQt6. Designed with minimalism in mind, it helps users quickly organize cluttered photo libraries.

---

## ?? 核心功能 / Core Features

- **极简 UI / Minimalist UI**: 采用流畅的 PyQt6 动画、侧边栏导航和圆角卡片布局。 / Features smooth PyQt6 animations, sidebar navigation, and rounded card layouts.
- **智能分类 / Smart Sorting**:
  - **按日期 / By Date**: 精确到天 (YYYY-MM-DD)。 / Precise to the day (YYYY-MM-DD).
  - **按月份 / By Month**: 将照片按月归档 (YYYY-MM)。 / Archive photos by month (YYYY-MM).
  - **按地点 / By Location**: 读取 EXIF GPS 信息，调用地理编码服务自动识别城市名称。 / Reads EXIF GPS info and uses geocoding services to identify city names.
- **个性化设置 / Personalization**: 内置 10 种配色方案，支持一键切换**深色模式**。 / Built-in 10 color schemes with one-click **Dark Mode** toggle.
- **历史记录 / History**: 自动记录处理任务，方便一键打开目标文件夹。 / Automatically logs tasks for easy one-click access to target folders.
- **多语言 / Multi-language**: 完整支持简体中文与英文。 / Full support for Simplified Chinese and English.
- **无损整理 / Lossless Organization**: 支持保留原文件 (复制)或移动文件模式。 / Supports both "Keep Originals (Copy)" and "Move Files" modes.
- **高性能 / High Performance**: 采用异步多线程处理，大批量照片整理时界面不卡顿。 / Uses asynchronous multi-threading to ensure a smooth UI even when handling large batches.

---

## ?? 快速开始 / Quick Start

### 方式 A：直接运行 (推荐) / Option A: Direct Run (Recommended)
已提供打包好的单文件版本，无需安装 Python 环境。 / A pre-packaged single-file version is provided, no Python installation required.
1. 进入 `dist/` 文件夹。 / Enter the `dist/` folder.
2. 运行 `C-SORTING.exe` 即可开始使用。 / Run `C-SORTING.exe` to start.

### 方式 B：开发者模式 (源码运行) / Option B: Developer Mode (Run from Source)
1. 克隆项目后，在根目录下创建并激活虚拟环境： / After cloning, create and activate a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. 安装依赖： / Install dependencies:
```powershell
pip install -r requirements.txt
```
3. 启动程序： / Start the application:
```powershell
python src/main.py
```

---

## ??? 项目结构 / Project Structure

- `src/`: 源代码 / Source Code
  - `gui/app.py`: 现代化的 PyQt6 界面逻辑、主题引擎与翻译系统. / Modern PyQt6 UI logic, theme engine, and translation system.
  - `sorter.py`: 核心分类算法 (日期/月份/城市分析). / Core sorting algorithms (Date/Month/City analysis).
  - `exif_utils.py`: 照片 EXIF 元数据解析 (时间、GPS). / Photo EXIF metadata parsing (Time, GPS).
  - `geocode.py`: 地理编码服务支持. / Geocoding service support.
  - `models/`: 预留 AI 识别接口. / Reserved AI recognition interfaces.
- `dist/`: 发布版本目录 / Distribution directory
- `assets/`: 程序图标与内部资源 / App icons and internal assets
- `config.json`: 用户配置持久化 / User configuration persistence
- `history.json`: 处理历史数据 / Processing history data

---

## ?? 注意事项 / Notes

- **网络要求 / Network Requirements**: 使用按地理位置分类时需连接互联网。 / Internet connection is required for "By Location" sorting.
- **配置文件 / Configuration Files**: 程序会在所在目录下自动生成 `config.json` 和 `history.json`。 / The app automatically generates `config.json` and `history.json` in its directory.

## 许可证 / License
MIT
MIT
