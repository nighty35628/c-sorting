"""
程序入口：启动 Tkinter GUI。
"""
import sys
from pathlib import Path

# 确保以模块方式导入 src 下的包时能找到路径
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.gui.app import App
import tkinter as tk

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
