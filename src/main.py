# Copyright (C) 2026 nighty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
