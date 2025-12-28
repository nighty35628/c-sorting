# Photo Sorter

这是一个Python 项目，用于按时间或按地点（城市）对一个文件夹内的照片进行分类。目标：一个简单的桌面 GUI，便于选择文件夹并执行分类；并为将来接入本地训练的小模型（人脸/物体识别）保留接口。

## 功能
- 读取照片 EXIF 元数据（拍摄时间、GPS 信息）
- 支持按拍摄时间或按城市名称分类照片（新建文件夹并移动照片）
- 简单的 Tkinter 图形界面，选择文件夹和分类方式
- 为本地识别模型保留接口（`src/models/recognition.py`）

## 快速开始（Windows）
1. 克隆或下载到本地：`c-sorting` 目录
2. 建议使用虚拟环境（在项目根目录下打开 PowerShell）：

```powershell
# 创建虚拟环境
python -m venv .venv
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1
# 安装必要的库
pip install -r requirements.txt
```

3. 运行程序：

```powershell
python -m src.main
```

## 如何使用
1. **启动程序**：运行上述命令后，会弹出一个窗口。
2. **选择文件夹**：点击“浏览”按钮，选择你存放照片的文件夹。
3. **选择分类方式**：
   - **按时间**：程序会读取照片的拍摄日期，并按 `YYYY-MM-DD` 格式创建文件夹。
   - **按城市**：程序会读取照片的 GPS 信息，并通过网络查询对应的城市名称。如果没有 GPS 信息，会归类到 `unknown_city`。
4. **保留原文件**：勾选此项后，程序会“复制”照片到新文件夹；不勾选则会“移动”照片。
5. **开始分类**：点击按钮，稍等片刻即可在原文件夹同级目录下看到分类好的新文件夹。

## 目录结构
- `src/`：源码
  - `exif_utils.py`：EXIF 解析工具
  - `geocode.py`：反向地理编码（经纬度->城市），使用 `geopy`（需要网络）
  - `sorter.py`：扫描、分组、移动文件逻辑
  - `gui/app.py`：Tkinter GUI
  - `models/recognition.py`：识别接口占位
- `requirements.txt`：依赖

## 注意与扩展
- 反向地理编码使用在线服务（OpenStreetMap / Nominatim）。如果需要离线城市解析，需要自行准备离线地图/数据库。
- 长期可以接入本地小模型（如使用 `face_recognition`、`onnx` 推理等），`models/recognition.py` 中留有接口。

## 许可证
MIT
                                                                                                