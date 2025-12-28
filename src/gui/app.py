"""
基于 Tkinter 的简单 GUI：
- 选择文件夹
- 选择分类方式（按时间或按城市）
- 开始排序（会在选择文件夹旁边创建目标文件夹）

注：为了避免复杂依赖，GUI 设计尽量简单，便于初学者阅读。
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from threading import Thread
from ..sorter import scan_folder, group_by_date, group_by_city, move_grouped_items

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title('Photo Sorter')
        self.folder_path = tk.StringVar()
        self.mode = tk.StringVar(value='date')
        self.copy_mode = tk.BooleanVar(value=False)

        tk.Label(root, text='选择要分类的照片文件夹：').grid(row=0, column=0, sticky='w')
        tk.Entry(root, textvariable=self.folder_path, width=50).grid(row=1, column=0, columnspan=2)
        tk.Button(root, text='浏览', command=self.browse).grid(row=1, column=2)

        tk.Radiobutton(root, text='按日 (YYYY-MM-DD)', variable=self.mode, value='date').grid(row=2, column=0, sticky='w')
        tk.Radiobutton(root, text='按月 (YYYY-MM)', variable=self.mode, value='month').grid(row=3, column=0, sticky='w')
        tk.Radiobutton(root, text='按城市', variable=self.mode, value='city').grid(row=4, column=0, sticky='w')
        tk.Checkbutton(root, text='保留原文件（复制而非移动）', variable=self.copy_mode).grid(row=5, column=0, sticky='w')

        tk.Button(root, text='开始分类', command=self.start).grid(row=6, column=0)
        self.status = tk.Label(root, text='状态: 等待操作')
        self.status.grid(row=7, column=0, columnspan=3, sticky='w')

    def browse(self):
        p = filedialog.askdirectory()
        if p:
            self.folder_path.set(p)

    def start(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning('未选择文件夹', '请先选择包含照片的文件夹')
            return
        thread = Thread(target=self._run_sort, args=(Path(folder),), daemon=True)
        thread.start()

    def _run_sort(self, folder: Path):
        self._set_status('扫描文件...')
        items = scan_folder(folder)
        self._set_status(f'找到 {len(items)} 张图片，准备分类...')
        
        mode = self.mode.get()
        if mode == 'date':
            groups = group_by_date(items)
            target = folder.parent / (folder.name + '_sorted_by_date')
        elif mode == 'month':
            from ..sorter import group_by_month
            groups = group_by_month(items)
            target = folder.parent / (folder.name + '_sorted_by_month')
        else:
            groups = group_by_city(items)
            target = folder.parent / (folder.name + '_sorted_by_city')
            
        self._set_status('正在移动/复制文件（请耐心等待）...')
        move_grouped_items(groups, target, copy=self.copy_mode.get())
        self._set_status('完成')
        messagebox.showinfo('完成', f'已完成分类，目标文件夹：{target}')

    def _set_status(self, text: str):
        self.status.config(text='状态: ' + text)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
