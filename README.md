[简体中文](#c-sorting) | [English](#c-sorting-en)

# C-SORTING

> **运行环境要求**：Python 3.12.0
>
> **依赖安装**：`pip install -r requirements.txt`

**C-SORTING** 是一款基于 PyQt6 开发的现代化智能照片分类工具，采用极简主义设计，旨在帮助用户快速整理杂乱的照片库。

## 🌟 核心功能

- **极简 UI**：采用流畅的 PyQt6 动画、侧边栏导航和圆角卡片布局。
- **智能分类**：
  - **支持多种格式**：不仅支持照片（JPG, PNG, HEIC, WebP, BMP 等），还支持视频文件（MP4, MOV, AVI, MKV 等）。
  - **按日期/月份/城市**：精确到天/月/地点（内置离线 337 城市数据库）。
  - **能工智人 (AI) - 零样本分类 (Zero-Shot Classification)**：
    - **深度学习驱动**：集成基于 Transformer 架构的 **Chinese-CLIP** 大模型（Vision-Language Pre-training）。
    - **跨模态理解**：不同于传统的物体识别，它能理解复杂的自然语言描述（如“阳光下的波光粼粼”、“穿着红色衣服的小女孩”），实现图像与语义的深度对齐。
    - **本地推理优化**：通过 ONNX Runtime FP16 量化加速，在保障毫秒级推理速度的同时，实现 100% 隐私化本地运行，无需任何云端 API 调用。
    - **十层多尺度采样 (10-View Multi-scale Sampling)**：对单张照片进行多尺度裁剪采样，确保不同角度与精细度的特征都能被精准捕获。
  - **媒体分拣**：自动将照片和视频分流至不同的目标文件夹。
- **个性化设置**：内置 10 种配色方案，支持一键切换**深色模式**。
- **交互优化**：
  - **丝滑进度条**：采用 5000 级超细分度与非线性动力学（Bezier/Sine）动画，模拟“努力工作”的节奏感。
  - **处理完成**：处理完成后可直接点击对话框中的“一键打开文件夹”查看结果。
- **历史管理**：自动记录处理任务，支持**实时清空历史记录**。
- **多语言**：完整支持简体中文与英文。
- **高性能**：采用异步多线程处理，大批量照片整理时界面不卡顿。

## 🚀 快速开始

### ⚠️ 环境准备 (重要)
由于模型文件较大（约 300MB+），本项目仓库未包含预训练模型。在使用 AI 分类功能前，请确保：
1. 在项目根目录下创建 `assets/models/chinese-clip-vit-base-patch16/` 文件夹。
2. 下载模型文件并放入上述文件夹内。
   - **百度网盘**: [点击下载](https://pan.baidu.com/s/1fCbXxHOEJfCzXDD5zBNsUg?pwd=nity) (提取码: `nity`)
   - **ModelScope**：[点击下载](https://www.modelscope.cn/models/nighty35628/clip-chinese-base-fp16/)
   - **更多下载地址**: 我们后续将同步上线 **Hugging Face**镜像，敬请期待。

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
sudo apt install ./packaging/debian/c-sorting_1.2.0-1_amd64.deb
```

## 🛠️ 项目结构

- `src/`：源代码
  - `gui/app.py`：现代化的 PyQt6 界面逻辑、主题引擎与进度条动画系统。
  - `models/recognition.py`：基于 ONNX 的 Chinese-CLIP 识别模型。
  - `sorter.py`：核心分类算法（日期/月份/城市/AI 识别）。
- `assets/`：程序图标、内置库与 AI 模型。
- `config.json`：用户配置持久化（主题色、语言、深色模式）。
- `history.json`：处理历史数据。

## 🔄 版本更新

- **v1.2.1** (2026-03-07): **交互体验与感知升级**。
  - **交互大飞跃**：所有无边框弹窗均支持拖拽；“使用说明”文本支持鼠标选中复制。
  - **智能感知**：进度条新增预计剩余时间（倒计时）显示。
  - **常驻后台**：新增系统托盘支持，支持关闭时隐藏至后台运行。
- **v1.2.0** (2026-03-06): **AI 与感知性能升级**。
  - **能工智人 (AI) 分类**：新增基于 Chinese-CLIP 的智能分类功能。
  - **感知性能优化**：重构进度条逻辑，引入 5000 级分度与非线性 Keyframe 动画。
  - **UI 细节打磨**：优化 Dashboard 布局，新增物理 SVG 勾选框图标。
  - **历史管理**：新增“清空历史记录”功能。
- **v1.1.0**: 增加多格式支持与初步视频处理。

## 许可证
AGPLv3

---

# C-SORTING <a id="c-sorting-en"></a>

**C-SORTING** is a modern intelligent photo sorting tool developed based on PyQt6, featuring a minimalist design aimed at helping users quickly organize cluttered photo libraries.

## 🌟 Core Features

- **Minimalist UI**: Utilizes smooth PyQt6 animations, sidebar navigation, and rounded corner card layouts.
- **Smart Sorting**:
  - **Multi-format Support**: Photos (JPG, PNG, HEIC, WebP, BMP, etc.) and video files (MP4, MOV, AVI, MKV, etc.).
  - **By Date/Month/Location**: Organized by time or offline city name.
  * **Clever Craftsman AI - Zero-Shot Deep Learning**:
    - **Vision-Language Alignment**: Driven by **Chinese-CLIP** (Transformer-based), enabling semantic understanding of natural language prompts like *"Sparkling water in the sunlight"* or *"Girl in red dress"*.
    - **Cross-Modal Retrieval**: Unlike simple object detection, it understands full descriptive concepts through its massive pre-trained knowledge base.
    - **Privacy-First Inference**: Fully localized **ONNX Runtime (FP16)** inference ensures that no photo data ever leaves your computer, achieving millisecond-level processing.
    - **10-View Multi-scale Sampling**: Employs multi-scale cropping strategies to capture subtle details and improve recognition accuracy.
- **Perception Optimization**:
  * **Buttery Smooth Progress**: 5000-level granularity with non-linear kinetic (Bezier/Sine) animations that mimic "computational effort".
- **History Management**: Track tasks and **Clear History** with one click.
- **Multi-language**: Full Chinese and English support.

## 🚀 Quick Start

### ⚠️ Model Preparation (Important)
Due to file size limits, the pre-trained models are not included in this repository. To use the AI sorting feature:
1. Create a folder at `assets/models/chinese-clip-vit-base-patch16/` in the project root.
2. Download and place the model files into the folder.
   - **Baidu Netdisk**: [Download here](https://pan.baidu.com/s/1fCbXxHOEJfCzXDD5zBNsUg?pwd=nity) (Password: `nity`)
   - **Coming Soon**: We will soon provide mirrors on **Hugging Face** and **ModelScope**.

### Windows
1. Clone the project, then create and activate a virtual environment in the root directory:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install dependencies:
```powershell
pip install -r requirements.txt
```
3. Start the application:
```powershell
python src/main.py
```

## 🔄 What's New

- **v1.2.1** (2026-03-07): **UX & Perception Overhaul**.
  - **Interaction**: All frameless dialogs are now draggable; User Guide text is now selectable.
  - **Smart Perception**: Added real-time 'Time Remaining' estimation to progress bars.
  - **Background Persistence**: Added System Tray support with 'Run in Background' option.
- **v1.2.0** (2026-03-06): **AI & Perception Performance Update**.
  - **Clever Craftsman AI**: Smart categorization using Chinese-CLIP models.
  - **Smooth UI Progress**: New 5k-res non-linear animation system.
  - **History**: Added 'Clear History' button with immediate UI feedback.

## License
AGPLv3