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

def main():
    app_qt = QApplication(sys.argv)
    app = App()
    app.show()
    sys.exit(app_qt.exec())

if __name__ == '__main__':
    main()
