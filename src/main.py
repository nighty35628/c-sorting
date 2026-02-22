"""
程序入口：启动 PyQt6 GUI。
"""
import sys
from pathlib import Path

# 确保以模块方式导入 src 下的包时能找到路径
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.gui.app import App
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import ctypes
import os

def main():
    # 修复 Windows 任务栏不显示图标的问题
    # 仅在 Windows 上尝试设置 AppUserModelID，其他平台跳过
    if sys.platform.startswith("win"):
        try:
            myappid = 'nighty.csorting.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            # 在非 Windows 或无法设置时忽略错误
            pass

    app_qt = QApplication(sys.argv)
    
    # 动态获取资源路径（适配开发环境和打包环境）
    if getattr(sys, 'frozen', False):
        res_root = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    else:
        res_root = Path(__file__).resolve().parents[1]

    # 设置全程图标
    icon_path = res_root / "assets" / "app_icon.ico"
    if not icon_path.exists():
        icon_path = res_root / "assets" / "favicon.ico"
        
    if icon_path.exists():
        app_qt.setWindowIcon(QIcon(str(icon_path)))

    app = App()
    app.show()
    sys.exit(app_qt.exec())

if __name__ == '__main__':
    main()
