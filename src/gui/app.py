
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

import sys
import json
import os
import subprocess
import base64
import shutil
import time
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QRadioButton, QCheckBox, QFileDialog, 
    QMessageBox, QGroupBox, QButtonGroup, QProgressBar,
    QGraphicsOpacityEffect, QApplication, QStackedWidget,
    QGridLayout, QScrollArea, QFrame, QDialog, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, QAbstractAnimation, QByteArray,
    QParallelAnimationGroup, QUrl
)
from PyQt6.QtGui import QPixmap, QIcon, QAction, QDesktopServices

# Fix relative import when running as a script
if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path
    # Add project root to sys.path
    project_root = str(Path(__file__).parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    __package__ = "src.gui"

from ..sorter import scan_folder, group_by_date, group_by_month, group_by_city, group_by_ai, move_grouped_items
from ..models.recognition import Recognizer

TRANSLATIONS = {
    "zh-cn": {
        "app_name": "C-SORTING",
        "nav_dashboard": "🏠 整理照片",
        "nav_history": "🕒 处理历史",
        "nav_settings": "⚙️ 偏好设置",
        "nav_guide": "📖 使用说明",
        "dash_header": "欢迎使用照片智能整理",
        "dash_desc": "简单几步，让您的照片库井井有条。",
        "label_source": "选择源文件夹",
        "btn_browse": "选取...",
        "group_mode": "分类方式",
        "mode_date": "按日期",
        "mode_month": "按月份",
        "mode_city": "按地理位置",
        "group_extra": "操作选项",
        "copy_mode": "保留原文件",
        "recursive_mode": "读取子文件夹",
        "btn_start": "立即开始整理",
        "status_ready": "准备就绪",
        "status_done": "处理完成！成功整理了 {} 张照片。",
        "status_error": "整理过程中出现错误。",
        "hist_header": "处理历史记录",
        "hist_empty": "暂无处理历史记录。",
        "hist_proc": "成功整理 {} 张照片",
        "hist_src": "源目录",
        "hist_dst": "目标",
        "hist_mode": "模式",
        "sett_header": "偏好设置",
        "sett_theme": "个性化主题",
        "sett_dark": "启用深色模式",
        "sett_color": "选择主题色：",
        "sett_lang": "语言设置 / Language",
        "btn_open": "📂 打开文件夹",
        "btn_clear_hist": "🗑️ 清空记录",
        "msg_success": "完成",
        "msg_warning": "提示",
        "msg_error": "错误",
        "msg_path_error": "文件夹已不存在。",
        "msg_open_error": "无法打开文件夹",
        "msg_proc_error": "处理过程出错",
        "lang_changed": "语言已切换为简体中文",
        "color_red": "红色",
        "color_blue": "蓝色",
        "color_green": "绿色",
        "color_purple": "紫色",
        "color_orange": "橙色",
        "color_pink": "粉色",
        "color_yellow": "黄色",
        "color_cyan": "青色",
        "color_indigo": "靛蓝",
        "color_gray": "灰色",
        "proc_scanning": "正在扫描文件...",
        "proc_no_files": "没有找到可分类的图片。",
        "proc_organizing": "找到 {} 张图片，正在分类...",
        "proc_copying": "正在复制文件...",
        "proc_moving": "正在移动文件...",
        "proc_done": "完成！目标文件夹：\n{}",
        "opt_date": "按日期",
        "opt_month": "按月份",
        "opt_city": "按地理位置",
        "mode_ai": "AI 智能分类",
        "ai_label_tip": "自定义标签 (逗号分隔):",
        "ai_loading": "能工智人分类中...",
        "ai_predefined": "预设标签:",
        "tag_catdog": "猫狗",
        "tag_parrot": "鹦鹉",
        "tag_selfie": "自拍",
        "tag_seaside": "海边",
        "tag_group": "合照",
        "tag_couple": "双人",
        "tag_food": "食物",
        "tag_doc": "文档",
        "tag_night": "夜景",
        "tag_firework": "烟花",
        "tag_plant": "绿植",
        "tag_flower": "花",
        "remaining_time": "预计剩余时间: {}",
        "time_min_sec": "{}分钟",
        "time_sec": "1分钟",
        "close_title": "退出确认",
        "close_msg": "是否将程序转入后台运行？",
        "btn_background": "后台运行",
        "btn_exit": "直接关闭",
        "msg_ai_running_title": "AI 任务运行中",
        "msg_ai_running_body": "程序已转入后台继续为您分类照片，预计还需 {} 完成。",
        "tray_show": "显示主界面",
        "tray_exit": "退出程序",
    },
    "en": {
        "app_name": "C-SORTING",
        "nav_dashboard": "🏠 Dashboard",
        "nav_history": "🕒 History",
        "nav_settings": "⚙️ Settings",
        "nav_guide": "📖 User Guide",
        "dash_header": "Smart Photo Sorter",
        "dash_desc": "Organize your photo library in a few simple steps.",
        "label_source": "Select Source Folder",
        "btn_browse": "Browse...",
        "group_mode": "Sorting Mode",
        "mode_date": "By Date (Recommended)",
        "mode_month": "By Month",
        "mode_city": "By Location",
        "group_extra": "Options",
        "copy_mode": "Keep Originals",
        "recursive_mode": "Read Subfolders",
        "btn_start": "Start Sorting Now",
        "status_ready": "Ready",
        "status_done": "Done! Organized {} photos successfully.",
        "status_error": "Error occurred during sorting.",
        "hist_header": "Processing History",
        "hist_empty": "No recent history found.",
        "hist_proc": "Organized {} photos",
        "hist_src": "Source",
        "hist_dst": "Target",
        "hist_mode": "Mode",
        "sett_header": "Preferences",
        "sett_theme": "Appearance",
        "sett_dark": "Enable Dark Mode",
        "sett_color": "Pick Theme Color:",
        "sett_lang": "Language Settings",
        "btn_open": "📂 Open Folder",
        "btn_clear_hist": "🗑️ Clear History",
        "msg_success": "Success",
        "msg_warning": "Warning",
        "msg_error": "Error",
        "msg_path_error": "Folder no longer exists.",
        "msg_open_error": "Could not open folder",
        "msg_proc_error": "Error processing files",
        "lang_changed": "Language switched to English",
        "color_red": "Red",
        "color_blue": "Blue",
        "color_green": "Green",
        "color_purple": "Purple",
        "color_orange": "Orange",
        "color_pink": "Pink",
        "color_yellow": "Yellow",
        "color_cyan": "Cyan",
        "color_indigo": "Indigo",
        "color_gray": "Gray",
        "proc_scanning": "Scanning files...",
        "proc_no_files": "No images found to organize.",
        "proc_organizing": "Found {} images, organizing...",
        "proc_copying": "Copying files...",
        "proc_moving": "Moving files...",
        "proc_done": "Done! Target folder:\n{}",
        "opt_date": "By Date",
        "opt_month": "By Month",
        "opt_city": "By Location",
        "mode_ai": "AI Smart Sort",
        "ai_label_tip": "Custom Labels (comma split):",
        "ai_loading": "Al Sorting...",
        "ai_predefined": "Predefined:",
        "tag_catdog": "Cats & Dogs",
        "tag_parrot": "Parrot",
        "tag_selfie": "Selfie",
        "tag_seaside": "Seaside",
        "tag_group": "Group",
        "tag_couple": "Couple",
        "tag_food": "Food",
        "tag_doc": "Document",
        "tag_night": "Night",
        "tag_firework": "Firework",
        "tag_plant": "Plant",
        "tag_flower": "Flower",
        "remaining_time": "Estimated: {}",
        "time_min_sec": "{} min",
        "time_sec": "1 min",
        "close_title": "Exit Confirmation",
        "close_msg": "Should the program run in the background?",
        "btn_background": "Run in Background",
        "btn_exit": "Exit Now",
        "msg_ai_running_title": "AI Task Running",
        "msg_ai_running_body": "Running in background to organize photos. Approx. {} left.",
        "tray_show": "Show Window",
        "tray_exit": "Quit",
    }
}

class ClickableLabel(QLabel):
    """A label that emits a signal when clicked, used for links."""
    clicked = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # Default cursor should be arrow
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # For QLabel, anchorAt is not available, but we can use openExternalLinks 
            # or rely on the underlying text Document if needed.
            # Here we let the default handler and setOpenExternalLinks do their job,
            # but we can also manually check for the link if openExternalLinks is buggy.
            pass
        super().mousePressEvent(event)

    def event(self, e):
        # QHelpEvent or QHoverEvent can be used, but since we want to know if we are over a link
        # In PyQt6 QLabel with HTML, the cursor automatically changes if openExternalLinks is True
        # but if it doesn't, we'd need a more complex way to find the anchor.
        # Since 'anchorAt' failed, it means QLabel doesn't have it (it's in QTextEdit/QTextBrowser).
        return super().event(e)

class ModernMessageBox(QDialog):
    def __init__(self, parent, title, message, mode="info", theme_color="#fa2d48", is_dark=False, target_path=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        bg_color = "#1c1c1e" if is_dark else "#ffffff"
        text_color = "#ffffff" if is_dark else "#000000"
        border_color = "#3a3a3c" if is_dark else "#d1d1d6"
        
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 24px;
            }}
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(Qt.GlobalColor.black if is_dark else Qt.GlobalColor.gray)
        self.frame.setGraphicsEffect(shadow)

        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(35, 35, 35, 30)
        frame_layout.setSpacing(20)
        
        # Styled Icon Circle (Unified with theme)
        icon_container = QLabel()
        icon_container.setFixedSize(64, 64)
        
        icon_color = theme_color
        if mode == "error": icon_color = "#ff3b30"
        elif mode == "warning": icon_color = "#ffcc00"
        
        icon_container.setStyleSheet(f"""
            QLabel {{
                background-color: {icon_color};
                border-radius: 32px;
            }}
        """)
        
        # USE QPixmap to handle Icon instead of QSS 'image'
        overlap_icon = QLabel(icon_container)
        overlap_icon.setFixedSize(64, 64)
        overlap_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # High-compatibility PNG base64 for icons (Sharp & Symmetric)
        # Success (Symmetric Checkmark)
        checkmark_png = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAGVKw4bAAABCklEQVRYhe2UO27CQBQA3zMSDR0lNX24ADkAmBvAGbhAGiRuADUdOUIipU8OkPS0UFJBQaKhYBEPK4mNP0uzI7mwvX4z0lorEggE7oxWORxQEemJCCLyqqpU6fstYMKFnm/5gGv6PuVtYGvkL0DkS94Avox8BTR9yRV4NvId8OBF7gLGiX0f5h0UAbG7Mu0d8Ah8G/ksl9wNi82gRVoE0AI25pt3oF5WwL8RQB34MGvXQCu33A2NnDQ1ApibNQegW0h+SwQwSrwflyLPEgF0gL15vuR09pfLHxFLTgfMmU+gUbo8JeLMFmhXJs8QEVcuT0S82a0oOvPmnwaoiciTu52q6k/RiEAgcFeOrMjv32JtTssAAAAASUVORK5CYII="
        # Error (X)
        error_png = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAGVKw4bAAABM0lEQVRYhe2WsUoDQRSGv3N2NyIKYpEq2InYitpYWFoqPoKlpS0+gK0PYis+gK0vYmllp9hYWFglpBARuUhi7p0yxmRzRHe9G9Sfy8DMv79h5mEGEAgEmisHNooAVK0E7KkqVXVn2hYFfHjhI7zGDeS7itpA66I28MvIb6A1kb9AZ9+0BPrTfAncm7kH5I5jX0N3YI9DndD9AX7GvgY6vNEML6XlY7AFdCpgB6AtR59Ad7mDPyKAAnY8ErcX7G7ZAn4jYAnIqRE6mXv1+hW9v6D3G3o/oI8j+m0RwEj9vWp170XyR0QAVeC9Yl354Nf8mC8jT0QAtXm90u1zH/9D/YpYchJgi9WpE6jXGk9O8kImsYhI994Ym6BfCQQCgUCD8gdC5268vWp9OAAAAABJRU5ErkJggg=="
        # Info (!)
        info_png = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAArUlEQVRYhe2Uuw3CMBRFz09Ag8QCZAnYAhYgsQI7MCRmYAWYgM4I7MAS7FApTBCR8hRIuE860uXeR67C7xYIBBYpPHE4sAByUQM3qqpVNVreDAl7XugWd6DkS9YAtS5pA+yXpA2wv2+6A+e+0xPoNPNlyP0N2ANzZ+Y7sPch97f9j31r5rv7bA67vYFmDdgCaE7R3Snt+uVuXMBPAsG/CHXFvU8gcD89uNIDTwXvV4X7CgAAAABJRU5ErkJggg=="

        icon_map = {"success": checkmark_png, "error": error_png, "info": info_png}
        current_b64 = icon_map.get(mode if mode in icon_map else "info")
        
        png_data = QByteArray.fromBase64(current_b64.encode())
        pixmap = QPixmap()
        pixmap.loadFromData(png_data, "PNG")
        
        # INCREASE RENDER QUALITY: Scale to absolute pixels instead of relative and use smooth transformation
        device_ratio = self.devicePixelRatio()
        target_size = 40 * device_ratio
        scaled_pixmap = pixmap.scaled(int(target_size), int(target_size), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        scaled_pixmap.setDevicePixelRatio(device_ratio)
        
        overlap_icon.setPixmap(scaled_pixmap)
        
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(icon_container)
        icon_layout.addStretch()
        frame_layout.addLayout(icon_layout)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {text_color}; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title_label)
        
        msg_label = QLabel(message)
        msg_label.setStyleSheet(f"font-size: 15px; color: {'#86868b' if not is_dark else '#98989d'}; border: none; line-height: 1.4;")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        frame_layout.addWidget(msg_label)
        
        # Buttons Setup
        btn_v_layout = QVBoxLayout()
        btn_v_layout.setSpacing(10)
        btn_v_layout.setContentsMargins(0, 5, 0, 0)

        # Style constants for secondary (neutral) style
        s_bg = "#f5f5f7" if not is_dark else "#2c2c2e"
        s_text = "#000000" if not is_dark else "#ffffff"
        s_border = "#d2d2d7" if not is_dark else "#3a3a3c"
        s_hover = "#e8e8ed" if not is_dark else "#3a3a3c"

        # Open Folder Button (If path provided)
        if target_path and hasattr(parent, 'open_folder'):
            open_text = parent.t("btn_open") if hasattr(parent, "t") else "📂 Open"
            open_btn = QPushButton(open_text)
            open_btn.setMinimumHeight(44)
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            open_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {s_bg};
                    color: {s_text};
                    border: 1px solid {s_border};
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 15px;
                }}
                QPushButton:hover {{
                    background-color: {s_hover};
                }}
            """)
            open_btn.clicked.connect(lambda: parent.open_folder(target_path))
            btn_v_layout.addWidget(open_btn)

        # OK Button - Now uses the same consistent neutral style
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumHeight(44)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {s_bg};
                color: {s_text};
                border: 1px solid {s_border};
                border-radius: 12px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {s_hover};
            }}
        """)
        btn_v_layout.addWidget(ok_btn)
        frame_layout.addLayout(btn_v_layout)
        
        layout.addWidget(self.frame)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    @staticmethod
    def show_message(parent, title, message, mode="info", target_path=None):
        theme = parent.current_theme_color if hasattr(parent, 'current_theme_color') else "#fa2d48"
        dark = parent.is_dark_mode if hasattr(parent, 'is_dark_mode') else False
        dlg = ModernMessageBox(parent, title, message, mode, theme, dark, target_path)
        dlg.exec()

    @staticmethod
    def ask_exit_mode(parent):
        theme = parent.current_theme_color if hasattr(parent, 'current_theme_color') else "#fa2d48"
        dark = parent.is_dark_mode if hasattr(parent, 'is_dark_mode') else False
        
        class DraggableExitDialog(QDialog):
            def __init__(self, parent):
                super().__init__(parent)
                self._drag_pos = None
            def mousePressEvent(self, event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
            def mouseMoveEvent(self, event):
                if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
                    self.move(event.globalPosition().toPoint() - self._drag_pos)
                    event.accept()
            def mouseReleaseEvent(self, event):
                self._drag_pos = None
                event.accept()

        dlg = DraggableExitDialog(parent)
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        bg_color = "#1c1c1e" if dark else "#ffffff"
        text_color = "#ffffff" if dark else "#000000"
        border_color = "#3a3a3c" if dark else "#d1d1d6"
        s_bg = "#f5f5f7" if not dark else "#2c2c2e"
        s_text = "#000000" if not dark else "#ffffff"
        s_border = "#d2d2d7" if not dark else "#3a3a3c"
        s_hover = "#e8e8ed" if not dark else "#3a3a3c"

        layout = QVBoxLayout(dlg)
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 24px; }}")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(Qt.GlobalColor.black if dark else Qt.GlobalColor.gray)
        frame.setGraphicsEffect(shadow)

        f_layout = QVBoxLayout(frame)
        f_layout.setContentsMargins(35, 35, 35, 30)
        f_layout.setSpacing(20)

        title_label = QLabel(parent.t("close_title"))
        title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {text_color}; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.addWidget(title_label)
        
        msg_label = QLabel(parent.t("close_msg"))
        msg_label.setStyleSheet(f"font-size: 15px; color: {'#86868b' if not dark else '#98989d'}; border: none; line-height: 1.4;")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        f_layout.addWidget(msg_label)

        btn_v = QVBoxLayout()
        btn_v.setSpacing(12)
        btn_v.setContentsMargins(0, 10, 0, 0)

        bg_btn = QPushButton(parent.t("btn_background"))
        bg_btn.setMinimumHeight(48)
        bg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bg_btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {s_bg}; 
                color: {s_text}; 
                border: 1px solid {s_border}; 
                border-radius: 14px; 
                font-weight: bold; 
                font-size: 15px; 
            }}
            QPushButton:hover {{
                background-color: {s_hover};
            }}
        """)
        bg_btn.clicked.connect(lambda: dlg.done(1))
        btn_v.addWidget(bg_btn)

        exit_btn = QPushButton(parent.t("btn_exit"))
        exit_btn.setMinimumHeight(48)
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {s_bg}; 
                color: {s_text}; 
                border: 1px solid {s_border}; 
                border-radius: 14px; 
                font-weight: bold; 
                font-size: 15px; 
            }}
            QPushButton:hover {{
                background-color: {s_hover};
            }}
        """)
        exit_btn.clicked.connect(lambda: dlg.done(2))
        btn_v.addWidget(exit_btn)

        f_layout.addLayout(btn_v)
        layout.addWidget(frame)
        
        return dlg.exec() # returns 1 for background, 2 for exit

class SortWorker(QThread):
    progress = pyqtSignal(str)
    progress_val = pyqtSignal(int)
    total_count_ready = pyqtSignal(int) # New signal to report total count
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, folder, mode, copy_mode, recursive=True, lang="zh-cn", model_dir=None, custom_labels=None):
        super().__init__()
        self.folder = Path(folder)
        self.mode = mode
        self.copy_mode = copy_mode
        self.recursive = recursive
        self.lang = lang
        self.model_dir = model_dir
        self.custom_labels = custom_labels

    def t(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["zh-cn"]).get(key, key)

    def run(self):
        try:
            self.progress.emit(self.t("proc_scanning"))
            items = scan_folder(self.folder, recursive=self.recursive)
            count = len(items)
            self.total_count_ready.emit(count) # Emit total count
            if not items:
                self.finished.emit({"success": False, "msg": self.t("proc_no_files")})
                return

            self.progress.emit(self.t("proc_organizing").format(count))
            
            # Separate photos and videos
            photos = [it for it in items if it.media_type == 'image']
            videos = [it for it in items if it.media_type == 'video']
            
            base_target = self.folder.parent
            def get_target_paths(mode_suffix):
                p_target = base_target / f"{self.folder.name}_photos_sorted_by_{mode_suffix}"
                v_target = base_target / f"{self.folder.name}_videos_sorted_by_{mode_suffix}"
                return p_target, v_target

            if self.mode == 'date':
                p_groups = group_by_date(photos)
                v_groups = group_by_date(videos)
                p_target, v_target = get_target_paths("date")
            elif self.mode == 'month':
                p_groups = group_by_month(photos)
                v_groups = group_by_month(videos)
                p_target, v_target = get_target_paths("month")
            elif self.mode == 'city':
                p_groups = group_by_city(photos)
                v_groups = group_by_city(videos)
                p_target, v_target = get_target_paths("city")
            elif self.mode == 'ai':
                self.progress.emit(self.t("ai_loading"))
                recognizer = Recognizer(self.model_dir)
                recognizer.load_model()
                p_groups = group_by_ai(photos, recognizer, self.custom_labels, progress_callback=lambda v: self.progress_val.emit(v))
                v_groups = {"视频": videos} if videos else {}
                p_target, v_target = get_target_paths("ai")
            
            action_key = "proc_copying" if self.copy_mode else "proc_moving"
            self.progress.emit(self.t(action_key))
            
            if photos:
                move_grouped_items(p_groups, p_target, copy=self.copy_mode)
            if videos:
                move_grouped_items(v_groups, v_target, copy=self.copy_mode)
            
            # Prepare result message
            res_msg = []
            if photos:
                res_msg.append(f"Photos: {p_target.name}")
            if videos:
                res_msg.append(f"Videos: {v_target.name}")
            
            final_msg = self.t("proc_done").format("\n".join(res_msg))

            self.finished.emit({
                "success": True,
                "msg": final_msg,
                "count": count,
                "target": str(p_target if photos else v_target),
                "source": str(self.folder),
                "mode": self.mode,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        except Exception as e:
            self.error.emit(str(e))


class App(QWidget):
    def contextMenuEvent(self, event):
        """Disable right-click context menu across the app."""
        event.ignore()

    def __init__(self):
        super().__init__()
        
        # Path configuration for portability (Handles Dev and EXE)
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
            # For resources (images/assets): Inside the bundled directory (_internal)
            self.res_dir = Path(getattr(sys, '_MEIPASS', self.base_dir))
            self.data_dir = self.get_user_data_dir()
        else:
            self.base_dir = Path(__file__).parent.parent.parent
            self.res_dir = self.base_dir
            self.data_dir = self.base_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.migrate_legacy_data_files()
            
        # Load config (theme/color)
        self.config_file = self.data_dir / "config.json"
        self.config = self.load_config()
        
        # Theme state
        self.current_theme_color = self.config.get("theme_color", "#fa2d48")  # Default Apple Red
        self.is_dark_mode = self.config.get("dark_mode", False)
        self.lang = self.config.get("language", "zh-cn")
        
        # Available Themes
        self.themes = [
            ("color_red", "#fa2d48"), ("color_blue", "#007aff"), ("color_green", "#34c759"), ("color_purple", "#af52de"), ("color_orange", "#ff9500"),
            ("color_pink", "#ff2d8c"), ("color_yellow", "#ffcc00"), ("color_cyan", "#5ac8fa"), ("color_indigo", "#5856d6"), ("color_gray", "#8e8e93")
        ]
        
        # Resource Path for QSS
        self.svg_check = (self.res_dir / "assets" / "check.svg").as_posix()
        
        self.history_file = self.data_dir / "history.json"
        self.history_data = self.load_history()
        
        self.setWindowTitle('C-SORTING')
        self.resize(760, 520)
        self.setMinimumWidth(405) # Ensure window doesn't get too small (set to 405 per request)
        
        # Set Window Icon (Desktop/Taskbar)
        # Use favicon.ico for window/taskbar, icon.png as high-res fallback
        icon_path = self.res_dir / "assets" / "favicon.ico"
        app_icon_path = self.res_dir / "assets" / "icon.png"
        
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        elif app_icon_path.exists():
            self.setWindowIcon(QIcon(str(app_icon_path)))
            
        self.init_tray_icon()
        self.setup_ui()
        self.apply_theme()

    def init_tray_icon(self):
        """Initialize system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use available icon
        icon_path = self.res_dir / "assets" / "favicon.ico"
        if not icon_path.exists():
            icon_path = self.res_dir / "assets" / "icon.png"
            
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        
        self.tray_menu = QMenu()
        self.show_action = QAction(self.t("tray_show"), self)
        self.exit_action = QAction(self.t("tray_exit"), self)
        
        self.show_action.triggered.connect(self.show_and_raise)
        self.exit_action.triggered.connect(self.quit_app)
        
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.exit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        self.apply_tray_style()

    def apply_tray_style(self):
        """Apply modern styling to the tray menu."""
        bg = "#ffffff" if not self.is_dark_mode else "#1c1c1e"
        text = "#1d1d1f" if not self.is_dark_mode else "#f5f5f7"
        hover = "#f5f5f7" if not self.is_dark_mode else "#2c2c2e"
        border = "#d2d2d7" if not self.is_dark_mode else "#38383a"
        
        # Set Window Flags to ensure we can have transparency
        self.tray_menu.setWindowFlags(self.tray_menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.tray_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.tray_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 8px 25px 8px 15px;
                border-radius: 6px;
                color: {text};
                font-size: 13px;
                background-color: transparent;
                margin: 1px 0px;
            }}
            QMenu::item:selected {{
                background-color: {hover};
                color: {self.current_theme_color};
            }}
            QMenu::separator {{
                height: 1px;
                background: {border};
                margin: 4px 10px;
            }}
        """)

    def show_and_raise(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger: # Left click
            if self.isVisible():
                self.hide()
            else:
                self.show_and_raise()

    def quit_app(self, force=True):
        """Quit the application directly without confirmation."""
        if hasattr(self, 'current_worker') and self.current_worker.isRunning():
            if not force:
                res = ModernMessageBox.ask_exit_mode(self)
                if res != 2: # Unless choose exit, don't quit
                    return
            self.current_worker.terminate()
        
        QApplication.quit()

    def resizeEvent(self, event):
        """Handle responsive sidebar and main content layout adjustment."""
        super().resizeEvent(event)
        
        # 1. Sidebar transition threshold: 680px
        curr_width = self.width()
        should_expand = curr_width > 680
        
        if should_expand != self.sidebar_expanded:
            self.sidebar_expanded = should_expand
            self.refresh_sidebar_ui()
        else:
            # Always sync content even if sidebar state didn't flip
            self.sync_content_layout()

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self):
        config_data = {
            "theme_color": self.current_theme_color,
            "dark_mode": self.is_dark_mode,
            "language": self.lang
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_user_data_dir(self):
        if sys.platform == "win32":
            appdata = os.getenv("APPDATA")
            if appdata:
                return Path(appdata) / "C-SORTING"
            return Path.home() / "AppData" / "Roaming" / "C-SORTING"

        if sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "C-SORTING"

        xdg_config_home = os.getenv("XDG_CONFIG_HOME")
        if xdg_config_home:
            return Path(xdg_config_home) / "c-sorting"
        return Path.home() / ".config" / "c-sorting"

    def migrate_legacy_data_files(self):
        legacy_files = {
            "config.json": self.base_dir / "config.json",
            "history.json": self.base_dir / "history.json",
        }

        for name, legacy_path in legacy_files.items():
            target_path = self.data_dir / name
            if target_path.exists() or not legacy_path.exists() or legacy_path == target_path:
                continue

            try:
                shutil.copy2(legacy_path, target_path)
            except OSError:
                continue

    def t(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["zh-cn"]).get(key, key)

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self, item):
        self.history_data.insert(0, item)
        # Limit to 50 items
        self.history_data = self.history_data[:50]
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def apply_theme(self):
        self.setStyleSheet(self.get_stylesheet())
        if hasattr(self, 'refresh_guide_page'):
            self.refresh_guide_page()
            
        # Update Tray style if exists
        if hasattr(self, 'apply_tray_style'):
            self.apply_tray_style()
        
        # Update App Title color separately
        if hasattr(self, 'app_title_label'):
            self.app_title_label.setStyleSheet(f"background: transparent; font-size: 20px; font-weight: bold; color: {self.current_theme_color}; margin-bottom: 2px;")

        # Update preset tags checkboxes with current theme color
        if hasattr(self, 'check_boxes'):
            for cb in self.check_boxes:
                cb.setStyleSheet(f"""
                    QCheckBox {{
                        font-size: 11px;
                        color: #8e8e93;
                        spacing: 4px;
                    }}
                    QCheckBox:checked {{
                        color: {self.current_theme_color};
                        font-weight: bold;
                    }}
                    QCheckBox::indicator {{
                        width: 16px;
                        height: 16px;
                        border-radius: 4px;
                        border: 1.5px solid #d1d1d6;
                        background-color: transparent;
                    }}
                    QCheckBox::indicator:hover {{
                        border-color: {self.current_theme_color};
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {self.current_theme_color};
                        border-color: {self.current_theme_color};
                        image: url("{self.svg_check}");
                    }}
                """)

        if hasattr(self, 'hist_list_layout'):
            self.refresh_history_ui()

    def get_stylesheet(self):
        primary = self.current_theme_color
        bg = "#ffffff" if not self.is_dark_mode else "#1c1c1e"
        sidebar_bg = "#f5f5f7" if not self.is_dark_mode else "#121212"
        text_color = "#1d1d1f" if not self.is_dark_mode else "#f5f5f7"
        secondary_text = "#86868b" if not self.is_dark_mode else "#a1a1a6"
        border_color = "#d2d2d7" if not self.is_dark_mode else "#38383a"
        input_bg = "#f5f5f7" if not self.is_dark_mode else "#2c2c2e"
        
        # Specific hover colors for theme selection buttons
        theme_hover_rules = ""
        for i, (key, hex_code) in enumerate(self.themes):
            theme_hover_rules += f"""
            #ThemeRB_{i}::indicator:hover {{
                border: 2px solid {hex_code};
            }}
            """

        guide_card_style = f"""
        #GuideCard {{
            background-color: {input_bg};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        #GuideCard QLabel {{
            background-color: transparent;
            border: none;
        }}
        #GuideCardTitle {{
            font-size: 18px;
            font-weight: bold;
            color: {primary};
            margin-bottom: 8px;
        }}
        #GuideCardContent {{
            font-size: 14px;
            color: {text_color};
            line-height: 1.5;
        }}
        #GuideCardSection {{
            font-weight: bold;
            color: {text_color};
            margin-top: 10px;
            margin-bottom: 5px;
        }}
        #GuideBadge {{
            background-color: {primary}22;
            color: {primary};
            border-radius: 4px;
            padding: 2px 6px;
            font-weight: bold;
            font-size: 12px;
        }}
        """

        # Sidebar Buttons Base
        # We ensure consistent alignment by always using text-align: left when expanded,
        # but with sufficient padding to feel centered if preferred.
        # If the user wants "ALWAYS CENTERED", we will set text-align: center for both.
        # The reported bug happens because of property toggles affecting layout.
        
        # FIXED: Always use text-align: center to maintain consistency as requested.
        sidebar_button_style = f"""
        #Sidebar QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 12px;
            padding: 12px;
            font-weight: 500;
            margin: 4px 10px;
            color: {text_color};
            font-size: 16px;
            text-align: center;
        }}
        """

        return f"""
        QWidget {{
            background-color: {bg};
            color: {text_color};
            font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            font-size: 14px;
        }}
        {theme_hover_rules}
        #Sidebar {{
            background-color: {sidebar_bg};
            border-right: 1px solid {border_color};
        }}
        #Sidebar QLabel {{
            background-color: transparent;
        }}
        #HistoryItem {{
            background-color: {input_bg};
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        #HistoryItem QLabel {{
            background-color: transparent;
        }}
        {sidebar_button_style}
        #Sidebar[collapsed="true"] QPushButton {{
            padding: 12px 0;
            margin: 4px 5px;
        }}
        #Sidebar[collapsed="false"] QPushButton {{
            padding: 12px 15px;
            margin: 4px 10px;
        }}
        #Sidebar #MenuBtn {{
            margin-bottom: 5px;
            font-size: 20px;
            padding: 10px;
            text-align: center;
            background-color: transparent;
            border: none;
        }}
        #Sidebar[collapsed="true"] #MenuBtn {{
            width: 100%;
        }}
        #Sidebar[collapsed="false"] #MenuBtn {{
            width: 50px;
        }}
        #Sidebar QPushButton:hover {{
            background-color: {"#e8e8ed" if not self.is_dark_mode else "#2c2c2e"};
        }}
        #Sidebar QPushButton[active="true"] {{
            background-color: {bg if self.is_dark_mode else "#e8e8ed"};
            color: {primary};
            border: 1px solid {border_color};
        }}
        #MainContent {{
            background-color: {bg};
            border-radius: 20px;
        }}
        QLineEdit {{
            background-color: {input_bg};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 8px 12px;
            color: {text_color};
            selection-background-color: {primary};
        }}
        QLineEdit:focus {{
            border: 2px solid {primary};
            background-color: {bg};
        }}
        QPushButton#PrimaryButton {{
            background-color: {primary};
            color: white;
            border-radius: 12px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 15px;
        }}
        QPushButton#SecondaryButton {{
            background-color: {input_bg};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 8px 15px;
            color: {text_color};
        }}
        QPushButton#SecondaryButton:hover {{
            background-color: {"#e8e8ed" if not self.is_dark_mode else "#3a3a3c"};
        }}
        QGroupBox {{
            border: 1px solid {border_color};
            border-radius: 12px;
            margin-top: 28px;
            padding-top: 5px;
            font-weight: bold;
            color: {text_color};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 0px;
            padding: 0 5px 3px 0;
            border-bottom: 2px solid {primary};
        }}
        QRadioButton, QCheckBox {{
            spacing: 8px;
            color: {text_color};
            padding: 2px;
        }}
        QRadioButton::indicator, QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid {border_color};
            background-color: {bg};
            margin: 2px;
        }}
        QRadioButton::indicator:checked, QCheckBox::indicator:checked {{
            background-color: {primary};
            border: 2px solid {primary};
            border-radius: 10px;
        }}
        QRadioButton::indicator:hover, QCheckBox::indicator:hover {{
            border: 2px solid {primary};
        }}
        #StatusLabel {{
            color: {secondary_text};
            font-size: 13px;
        }}
        #Header {{
            font-size: 28px; 
            font-weight: 600;
            color: {text_color};
        }}
        #LabelHeading {{
            font-weight: 600; 
            font-size: 15px;
            color: {text_color};
        }}
        """

    def setup_ui(self):
        # State for collapsible sidebar
        self.sidebar_expanded = False
        self.history_is_narrow = None
        
        # Overall Horizontal Layout
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        # 1. Sidebar
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("Sidebar")
        self.sidebar_widget.setProperty("collapsed", "true")
        self.sidebar_widget.setFixedWidth(70)
        
        # Sidebar animation
        self.sidebar_anim = QPropertyAnimation(self.sidebar_widget, b"minimumWidth")
        self.sidebar_anim.setDuration(300)
        self.sidebar_anim.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        self.sidebar_anim_max = QPropertyAnimation(self.sidebar_widget, b"maximumWidth")
        self.sidebar_anim_max.setDuration(300)
        self.sidebar_anim_max.setEasingCurve(QEasingCurve.Type.OutQuint)

        self.sidebar_group = QParallelAnimationGroup()
        self.sidebar_group.addAnimation(self.sidebar_anim)
        self.sidebar_group.addAnimation(self.sidebar_anim_max)
        
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 5, 0, 15)
        sidebar_layout.setSpacing(2)
        
        # Menu / Toggle Button
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setObjectName("MenuBtn")
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.btn_menu)

        self.btn_dashboard = QPushButton()
        self.btn_dashboard.setProperty("active", "true")
        self.btn_history = QPushButton()
        self.btn_settings = QPushButton()
        self.btn_guide = QPushButton()
        
        self.sidebar_buttons = [self.btn_dashboard, self.btn_history, self.btn_settings, self.btn_guide]
        self.update_sidebar_text()
        
        for btn in self.sidebar_buttons:
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(self.on_sidebar_click)
        
        sidebar_layout.addStretch()
        
        # App Icon, Title and Version at the bottom
        self.sidebar_logo_label = QLabel()
        self.sidebar_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_icon_path = self.res_dir / "assets" / "icon.png"
        if app_icon_path.exists():
            pixmap = QPixmap(str(app_icon_path))
            target_size = 100
            # High-quality scaling for HiDPI screens (prevents blurriness)
            dpr = self.devicePixelRatioF()
            scaled_pixmap = pixmap.scaled(
                int(target_size * dpr), 
                int(target_size * dpr), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            scaled_pixmap.setDevicePixelRatio(dpr)
            self.sidebar_logo_label.setPixmap(scaled_pixmap)
        self.sidebar_logo_label.setStyleSheet("background: transparent; margin-bottom: 20px;")
        self.sidebar_logo_label.setVisible(False)
        sidebar_layout.addWidget(self.sidebar_logo_label)

        self.app_title_label = QLabel(self.t("app_name"))
        self.app_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_title_label.setStyleSheet(f"background: transparent; font-size: 20px; font-weight: bold; color: {self.current_theme_color}; margin-bottom: 2px;")
        self.app_title_label.setVisible(False)
        sidebar_layout.addWidget(self.app_title_label)

        self.version_label = QLabel("v1.2.1")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet("background: transparent; color: #86868b; font-size: 11px; margin-bottom: 10px;")
        self.version_label.setVisible(False)
        sidebar_layout.addWidget(self.version_label)
        
        hbox.addWidget(self.sidebar_widget)

        # 2. Main content stack
        self.stack = QStackedWidget()
        self.stack.setObjectName("MainContent")
        
        # --- Page 0: Dashboard ---
        dash_page = QWidget()
        dash_layout = QVBoxLayout(dash_page)
        dash_layout.setContentsMargins(40, 30, 40, 30) # Increased margins
        dash_layout.setSpacing(25)

        self.dash_header = QLabel(self.t("dash_header"))
        self.dash_header.setObjectName("Header")
        dash_layout.addWidget(self.dash_header)

        self.dash_desc = QLabel(self.t("dash_desc"))
        self.dash_desc.setObjectName("SubHeader")
        dash_layout.addWidget(self.dash_desc)

        # Folder selection area
        folder_group = QVBoxLayout()
        self.folder_label = QLabel(self.t("label_source"))
        self.folder_label.setObjectName("LabelHeading")
        folder_group.addWidget(self.folder_label)
        
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("/Users/photos/trip-2025")
        self.browse_btn = QPushButton(self.t("btn_browse"))
        self.browse_btn.setObjectName("SecondaryButton")
        self.browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        folder_group.addLayout(path_layout)
        dash_layout.addLayout(folder_group)

        # Options area (using responsive flow-like layout)
        self.options_container = QWidget()
        options_layout = QHBoxLayout(self.options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(15)
        
        self.mode_group_box = QGroupBox(self.t("group_mode"))
        self.mode_group_box.setMinimumWidth(180) # Initial width set to 180 explicitly
        self.mode_group_box.setFixedHeight(230) 
        mode_v = QVBoxLayout()
        mode_v.setContentsMargins(15, 12, 15, 15) # Standardized margins
        mode_v.setSpacing(10)
        self.mode_group = QButtonGroup(self)
        self.rb_date = QRadioButton(self.t("mode_date"))
        self.rb_date.setChecked(True)
        self.rb_month = QRadioButton(self.t("mode_month"))
        self.rb_city = QRadioButton(self.t("mode_city"))
        self.rb_ai = QRadioButton(self.t("mode_ai"))
        
        # AI labels input area (Hidden, only one copy in extra_group_box)
        for rb in [self.rb_date, self.rb_month, self.rb_city, self.rb_ai]:
            self.mode_group.addButton(rb)
            mode_v.addWidget(rb)
        self.mode_group_box.setLayout(mode_v)
        
        self.extra_group_box = QGroupBox(self.t("group_extra"))
        self.extra_group_box.setMinimumWidth(180) 
        self.extra_group_box.setFixedHeight(230) # Match height with mode_group_box
        extra_v = QVBoxLayout()
        extra_v.setContentsMargins(15, 12, 15, 15) # Match left side exactly
        extra_v.setSpacing(10)
        
        # Options row: Copy mode & Recursive mode
        options_row = QHBoxLayout()
        options_row.setContentsMargins(0, 0, 0, 0)
        options_row.setSpacing(10)
        
        self.cb_copy = QCheckBox(self.t("copy_mode"))
        self.cb_copy.setChecked(True)
        
        self.cb_recursive = QCheckBox(self.t("recursive_mode"))
        self.cb_recursive.setChecked(True)
        
        options_row.addWidget(self.cb_copy)
        options_row.addWidget(self.cb_recursive)
        options_row.addStretch() 
        extra_v.addLayout(options_row)
        
        # AI Options moved here for balance
        self.ai_options_widget = QWidget()
        self.ai_options_widget.setMaximumHeight(0) # Start with 0 height
        self.ai_options_widget.setContentsMargins(0, 0, 0, 0)
        ai_options_layout = QVBoxLayout(self.ai_options_widget)
        ai_options_layout.setContentsMargins(0, 5, 0, 0)
        ai_options_layout.setSpacing(8)

        self.labels_container = QWidget()
        labels_grid = QGridLayout(self.labels_container)
        labels_grid.setContentsMargins(0, 0, 0, 0)
        labels_grid.setSpacing(4)
        
        self.preset_tags = [
            ("tag_parrot", "鹦鹉"), ("tag_catdog", "猫狗"), ("tag_selfie", "自拍"), 
            ("tag_couple", "双人"), ("tag_group", "合照"), ("tag_food", "食物"), 
            ("tag_seaside", "海边"), ("tag_night", "夜景"), ("tag_firework", "烟花"), 
            ("tag_plant", "绿植"), ("tag_doc", "文档"), ("tag_flower", "花")
        ]
        self.check_boxes = []
        for i, (tag_key, tag_zh) in enumerate(self.preset_tags):
            cb = QCheckBox(self.t(tag_key))
            cb.setProperty("tag_key", tag_key)
            cb.setChecked(False) # Default UNCHECKED
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    font-size: 11px;
                    color: #8e8e93;
                    spacing: 4px;
                }}
                QCheckBox:checked {{
                    color: {self.current_theme_color};
                    font-weight: bold;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 1.5px solid #d1d1d6;
                    background-color: transparent;
                }}
                QCheckBox::indicator:hover {{
                    border-color: {self.current_theme_color};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {self.current_theme_color};
                    border-color: {self.current_theme_color};
                    image: url("{self.svg_check}");
                }}
            """)
            self.check_boxes.append(cb)
            # 4 columns for better balance (3 rows * 4 columns = 12 tags)
            labels_grid.addWidget(cb, i // 4, i % 4)
        ai_options_layout.addWidget(self.labels_container)

        self.ai_label_input = QLineEdit()
        self.ai_label_input.setPlaceholderText(self.t("ai_label_tip"))
        self.ai_label_input.setFixedHeight(32) # Increased height to match other options
        self.ai_label_input.setStyleSheet("font-size: 11px; padding: 0 8px;")
        ai_options_layout.addWidget(self.ai_label_input)
        
        # Animations
        self.ai_height_anim = QPropertyAnimation(self.ai_options_widget, b"maximumHeight")
        self.mode_width_anim = QPropertyAnimation(self.mode_group_box, b"minimumWidth")
        self.extra_width_anim = QPropertyAnimation(self.extra_group_box, b"minimumWidth")
        
        self.ai_height_anim.setDuration(400)
        self.mode_width_anim.setDuration(400)
        self.extra_width_anim.setDuration(400)
        
        curve = QEasingCurve.Type.OutQuart # Smoother "fast-to-slow" easing
        self.ai_height_anim.setEasingCurve(curve)
        self.mode_width_anim.setEasingCurve(curve)
        self.extra_width_anim.setEasingCurve(curve)

        def toggle_ai_layout(checked):
            self.mode_width_anim.stop()
            self.extra_width_anim.stop()
            self.ai_height_anim.stop()
            
            if checked:
                # Calculate required height
                target_height = 135 
                self.mode_width_anim.setEndValue(130)
                self.extra_width_anim.setEndValue(280)
                self.ai_height_anim.setStartValue(self.ai_options_widget.height())
                self.ai_height_anim.setEndValue(target_height)
            else:
                self.mode_width_anim.setEndValue(180)
                self.extra_width_anim.setEndValue(180)
                self.ai_height_anim.setStartValue(self.ai_options_widget.height())
                self.ai_height_anim.setEndValue(0)
                
            self.mode_width_anim.start()
            self.extra_width_anim.start()
            self.ai_height_anim.start()

        self.rb_ai.toggled.connect(toggle_ai_layout)
        
        extra_v.addWidget(self.ai_options_widget)
        extra_v.addStretch()
        self.extra_group_box.setLayout(extra_v)
        
        options_layout.addWidget(self.mode_group_box)
        options_layout.addWidget(self.extra_group_box)
        dash_layout.addWidget(self.options_container)

        # Action Button
        self.start_btn = QPushButton(self.t("btn_start"))
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_sorting)
        dash_layout.addWidget(self.start_btn)

        # Progress Area
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 5, 0, 5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 5000) # 扩大到 5000，实现超高精度步进，肉眼无法察觉任何跳变
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(6)

        # Status
        self.status_label = QLabel(self.t("status_ready"))
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.time_label = QLabel("")
        self.time_label.setObjectName("StatusLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setVisible(False)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.time_label)
        dash_layout.addWidget(self.progress_container)

        # Smooth Progress Animation
        self.progress_anim = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_anim.setDuration(800) # Longer duration for perceived continuity
        self.progress_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        def update_smooth_progress(val):
            if val == 0:
                self.progress_bar.setValue(0)
                return
            self.progress_anim.stop()
            self.progress_anim.setStartValue(self.progress_bar.value())
            self.progress_anim.setEndValue(val)
            self.progress_anim.start()

        dash_layout.addStretch()
        
        self.stack.addWidget(dash_page)

        # --- Page 1: History ---
        self.history_page = QWidget()
        self.hist_v = QVBoxLayout(self.history_page)
        self.hist_v.setContentsMargins(15, 30, 15, 30)
        
        self.hist_header_label = QLabel(self.t("hist_header"))
        self.hist_header_label.setObjectName("Header")
        
        hist_title_layout = QHBoxLayout()
        hist_title_layout.addWidget(self.hist_header_label)
        hist_title_layout.addStretch()
        
        self.btn_clear_hist = QPushButton(self.t("btn_clear_hist"))
        self.btn_clear_hist.setObjectName("SecondaryButton") # Use standard secondary style
        self.btn_clear_hist.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_hist.setFixedHeight(36)
        self.btn_clear_hist.clicked.connect(self.clear_history)
        hist_title_layout.addWidget(self.btn_clear_hist)
        
        self.hist_v.addLayout(hist_title_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background-color: transparent;")
        
        self.hist_container = QWidget()
        self.hist_list_layout = QVBoxLayout(self.hist_container)
        self.hist_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.hist_container)
        
        self.hist_v.addWidget(self.scroll)
        self.refresh_history_ui()
        
        self.stack.addWidget(self.history_page)

        # --- Page 2: Settings ---
        settings_page = QWidget()
        sett_v = QVBoxLayout(settings_page)
        sett_v.setContentsMargins(40, 40, 40, 40)
        sett_v.setSpacing(30)
        
        self.sett_header_label = QLabel(self.t("sett_header"))
        self.sett_header_label.setObjectName("Header")
        sett_v.addWidget(self.sett_header_label)

        # Theme Section
        self.theme_group_box = QGroupBox(self.t("sett_theme"))
        theme_layout = QVBoxLayout()
        theme_layout.setContentsMargins(15, 15, 15, 15)
        
        # Dark mode toggle
        self.dark_mode_cb = QCheckBox(self.t("sett_dark"))
        self.dark_mode_cb.setChecked(self.is_dark_mode)
        self.dark_mode_cb.toggled.connect(self.toggle_dark_mode)
        theme_layout.addWidget(self.dark_mode_cb)
        
        # Theme color selection
        self.color_label_ui = QLabel(self.t("sett_color"))
        theme_layout.addWidget(self.color_label_ui)
        
        colors_grid = QGridLayout()
        colors_grid.setContentsMargins(0, 5, 0, 0)
        colors_grid.setSpacing(10)
        self.color_group = QButtonGroup(self)
        self.color_rbs = []
        for i, (key, hex_code) in enumerate(self.themes):
            rb = QRadioButton(self.t(key))
            rb.setObjectName(f"ThemeRB_{i}")
            if hex_code == self.current_theme_color:
                rb.setChecked(True)
            self.color_group.addButton(rb, i)
            self.color_rbs.append(rb)
            # Initial grid placement
            colors_grid.addWidget(rb, i // 5, i % 5)
        
        self.color_group.idClicked.connect(lambda id: self.change_theme_color(self.themes[id][1]))
        
        self.theme_layout_container = QWidget()
        self.theme_layout_container.setLayout(colors_grid)
        self.theme_grid_cols = 5 # Track current column state
        theme_layout.addWidget(self.theme_layout_container)
        self.theme_group_box.setLayout(theme_layout)
        sett_v.addWidget(self.theme_group_box)

        # Language Section
        self.lang_group_box = QGroupBox(self.t("sett_lang"))
        self.lang_container = QWidget()
        lang_layout = QHBoxLayout(self.lang_container)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        self.lang_group = QButtonGroup(self)
        
        self.rb_zh = QRadioButton("简体中文")
        self.rb_en = QRadioButton("English")
        
        if self.lang == "zh-cn": self.rb_zh.setChecked(True)
        else: self.rb_en.setChecked(True)
        
        self.lang_group.addButton(self.rb_zh, 0)
        self.lang_group.addButton(self.rb_en, 1)
        
        lang_layout.addWidget(self.rb_zh)
        lang_layout.addWidget(self.rb_en)
        lang_layout.addStretch()
        
        self.lang_group.idClicked.connect(self.change_language)
        
        lang_v_layout = QVBoxLayout()
        lang_v_layout.setContentsMargins(15, 15, 15, 15)
        lang_v_layout.addWidget(self.lang_container)
        self.lang_group_box.setLayout(lang_v_layout)
        sett_v.addWidget(self.lang_group_box)
        
        sett_v.addStretch()
        self.stack.addWidget(settings_page)

        # --- Page 3: Guide ---
        self.guide_page = QWidget()
        self.guide_v = QVBoxLayout(self.guide_page)
        self.guide_v.setContentsMargins(40, 30, 10, 30)
        self.refresh_guide_page()
        self.stack.addWidget(self.guide_page)

        hbox.addWidget(self.stack)

        # Animations
        self.opacity_effect = QGraphicsOpacityEffect(self.status_label)
        self.status_label.setGraphicsEffect(self.opacity_effect)
        
        self.status_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.status_anim.setDuration(800) # 800ms 渐入
        self.status_anim.setStartValue(0.3)
        self.status_anim.setEndValue(1.0)
        self.status_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.pulse_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.pulse_anim.setDuration(2000) # 2000ms 呼吸周期
        self.pulse_anim.setStartValue(1.0)
        self.pulse_anim.setEndValue(0.3)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        self.refresh_sidebar_ui()

    def refresh_sidebar_ui(self):
        """Update sidebar visual state based on self.sidebar_expanded with animation."""
        target_width = 210 if self.sidebar_expanded else 70
        is_collapsed = "false" if self.sidebar_expanded else "true"
        
        # Animate width via group
        self.sidebar_group.stop()
        self.sidebar_anim.setStartValue(self.sidebar_widget.width())
        self.sidebar_anim.setEndValue(target_width)
        self.sidebar_anim_max.setStartValue(self.sidebar_widget.width())
        self.sidebar_anim_max.setEndValue(target_width)
        self.sidebar_group.start()

        self.sidebar_widget.setProperty("collapsed", is_collapsed)
        
        # Show/Hide labels
        self.sidebar_logo_label.setVisible(self.sidebar_expanded)
        self.app_title_label.setVisible(self.sidebar_expanded)
        self.version_label.setVisible(self.sidebar_expanded)
        self.update_sidebar_text()
        
        # Sync main content layout whenever sidebar state changes
        self.sync_content_layout()
        
        # Refresh style
        self.sidebar_widget.style().unpolish(self.sidebar_widget)
        self.sidebar_widget.style().polish(self.sidebar_widget)

    def sync_content_layout(self):
        """Synchronize main content 'Flex' layout with current sidebar state."""
        # FIX: Base layout decisions ONLY on the total window width to ensure coordination.
        window_width = self.width()
        
        # Increased threshold to 680 to ensure text has absolute breathing room
        is_small_mode = window_width < 680
        
        if is_small_mode:
            # Narrow mode logic
            if isinstance(self.options_container.layout(), QHBoxLayout):
                new_layout = QVBoxLayout()
                new_layout.addWidget(self.mode_group_box)
                new_layout.addWidget(self.extra_group_box)
                old_layout = self.options_container.layout()
                QWidget().setLayout(old_layout)
                self.options_container.setLayout(new_layout)

            if hasattr(self, 'theme_layout_container') and isinstance(self.theme_layout_container.layout(), QGridLayout):
                if self.theme_grid_cols != 2:
                    grid = self.theme_layout_container.layout()
                    for i, rb in enumerate(self.color_rbs):
                        grid.addWidget(rb, i // 2, i % 2)
                    self.theme_grid_cols = 2
            
            if isinstance(self.lang_container.layout(), QHBoxLayout):
                new_lang_layout = QVBoxLayout()
                new_lang_layout.addWidget(self.rb_zh)
                new_lang_layout.addWidget(self.rb_en)
                old_lang_layout = self.lang_container.layout()
                QWidget().setLayout(old_lang_layout)
                self.lang_container.setLayout(new_lang_layout)
        else:
            # Wide mode logic
            if isinstance(self.options_container.layout(), QVBoxLayout):
                new_layout = QHBoxLayout()
                new_layout.setContentsMargins(0, 0, 0, 0)
                new_layout.setSpacing(15)
                new_layout.addWidget(self.mode_group_box)
                new_layout.addWidget(self.extra_group_box)
                old_layout = self.options_container.layout()
                QWidget().setLayout(old_layout)
                self.options_container.setLayout(new_layout)

            if hasattr(self, 'theme_layout_container') and isinstance(self.theme_layout_container.layout(), QGridLayout):
                if self.theme_grid_cols != 5:
                    grid = self.theme_layout_container.layout()
                    for i, rb in enumerate(self.color_rbs):
                        grid.addWidget(rb, i // 5, i % 5)
                    self.theme_grid_cols = 5

            if isinstance(self.lang_container.layout(), QVBoxLayout):
                new_lang_layout = QHBoxLayout()
                new_lang_layout.setContentsMargins(0, 0, 0, 0)
                new_lang_layout.addWidget(self.rb_zh)
                new_lang_layout.addWidget(self.rb_en)
                new_lang_layout.addStretch()
                old_lang_layout = self.lang_container.layout()
                QWidget().setLayout(old_lang_layout)
                self.lang_container.setLayout(new_lang_layout)

    def refresh_guide_page(self):
        """Rebuilds the guide page content to adapt to theme or language changes."""
        # Clear existing layout
        while self.guide_v.count():
            item = self.guide_v.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Re-fetch theme colors
        primary = self.current_theme_color
        text_color = "#1d1d1f" if not self.is_dark_mode else "#f5f5f7"
        border_color = "#d2d2d7" if not self.is_dark_mode else "#38383a"
        input_bg = "#f5f5f7" if not self.is_dark_mode else "#2c2c2e"

        # Header
        guide_header = QLabel(self.t("nav_guide"))
        guide_header.setObjectName("Header")
        self.guide_v.addWidget(guide_header)

        # Scroll Area
        scrollbar_bg = "transparent"
        scrollbar_handle = "#c0c0c0" if not self.is_dark_mode else "#555555"
        scrollbar_handle_hover = "#a0a0a0" if not self.is_dark_mode else "#777777"
        guide_scroll = QScrollArea()
        guide_scroll.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        guide_scroll.setWidgetResizable(True)
        guide_scroll.setFrameShape(QFrame.Shape.NoFrame)
        guide_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {scrollbar_bg};
                width: 6px;
                margin: 0px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {scrollbar_handle};
                min-height: 30px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {scrollbar_handle_hover};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        guide_scroll_content = QWidget()
        guide_scroll_content.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        guide_scroll_content.setStyleSheet("background: transparent;")
        guide_scroll_v = QVBoxLayout(guide_scroll_content)
        guide_scroll_v.setContentsMargins(0, 20, 16, 20)
        guide_scroll_v.setSpacing(20)

        def create_guide_card(title, content):
            card = QFrame()
            card.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            card.setObjectName("GuideCard")
            card.setStyleSheet(f"""
                #GuideCard {{
                    background-color: {input_bg};
                    border: 1px solid {border_color};
                    border-radius: 16px;
                }}
            """)
            card_v = QVBoxLayout(card)
            card_v.setContentsMargins(15, 12, 15, 12)
            card_v.setSpacing(6)
            
            title_label = QLabel(title)
            title_label.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            title_label.setCursor(Qt.CursorShape.ArrowCursor)
            title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {primary}; background: transparent; border: none;")
            card_v.addWidget(title_label)
            
            # Using ClickableLabel for blocks that may contain links
            content_label = ClickableLabel(content)
            content_label.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            content_label.setWordWrap(True)
            content_label.setOpenExternalLinks(True)
            content_label.setStyleSheet(f"font-size: 14px; color: {text_color}; line-height: 1.5; background: transparent; border: none;")
            card_v.addWidget(content_label)
            return card

        # Content Sections
        if self.lang == "zh-cn":
            about_content = (
                "C-SORTING 是一款基于 PyQt6 开发的现代化智能照片分类工具，旨在帮助用户快速整理杂乱的照片库。"
                "无论是相机导出的海量照片，还是日常积累的随手拍，本工具都能通过多种分类方式让您的媒体库变得井井有条。"
                f"<div style='text-align: right; color: gray; font-style: italic; margin-top: 5px;'>“拿你所有的，换你想要的。”</div>"
            )
            guide_scroll_v.addWidget(create_guide_card("关于本软件", about_content))

            modes_content = (
                f"<p><b>📅 按日期分类</b><br>支持精确到天（YYYY-MM-DD）或按月份（YYYY-MM）归档，让时间线一目了然。</p>"
                f"<p><b>🌍 按地点分类</b><br>基于内置离线数据库，可精确识别到<b>县</b>或<b>县级市</b>级别（覆盖 337 个地级行政区）。所有地理信息解析均在本地完成。</p>"
                f"<p><b>🤖 AI 智能分类</b><br>"
                f"• <b>分类逻辑</b>：采用非监督思想分类，严格按你指定的标签进行归类，不会创建未选中的其他类别。<br>"
                f"• <b>模型支持</b>：本功能基于开源模型 <a href='https://github.com/OFA-Sys/Chinese-CLIP' style='color:{primary};'>Chinese CLIP</a> 实现（由 OFA-Sys 团队开发），遵循 <b>Apache License 2.0</b> 开源协议。<br>"
                f"• <b>重要提示</b>：若只想筛选出某类特定图片，请务必同时添加一个自定义的“其他”类别，否则所有图片将被归入你选择的单一标签中。<br>"
                f"• <b>示例说明</b>：<br>"
                f"&nbsp;&nbsp;- 如果只选择“花”，则所有照片都会被归到“花”中。<br>"
                f"&nbsp;&nbsp;- 如果选择“花”和“其他”，则花的照片归“花”，不是花的照片归“其他”。<br>"
                f"&nbsp;&nbsp;- 如果选择“花”和“鹦鹉”，则花的照片归“花”，不是花的照片归“鹦鹉”。</p>"
            )
            guide_scroll_v.addWidget(create_guide_card("分类方式", modes_content))

            tips_content = (
                f"<b>分类组合技巧</b><br>你可以灵活组合不同的分类方式，实现更精细的照片管理：<br>"
                f"• <b>地理 + 日期</b>：先按地点分类，再在每个地点文件夹内按日期归档，就能看到每个地方不同日子拍摄的照片。<br>"
                f"• <b>地理 + AI</b>：先按地点分类，再对特定地点的照片进行 AI 语义分类（如“猫”“狗”“风景”），轻松找到旅途中拍下的精彩瞬间。<br>"
                f"• <b>日期 + AI</b>：先按年月归档，再对某个月份的照片进行 AI 分类，回顾当月拍过的花鸟鱼虫。<br><br>"
                f"<b>AI 分类的创意玩法</b><br>你可以充分发挥创意，例如给全是人像的照片使用“猫”和“狗”的标签进行分类，就可以知道谁是小猫，谁是小狗了。"
            )
            guide_scroll_v.addWidget(create_guide_card("使用小技巧", tips_content))

            edition_content = (
                f"本软件体积较大的主要原因是内置了本地 AI 模型（Chinese CLIP），以实现完全本地化的智能分类功能。如果您不需要 AI 相关功能，可以选择下载轻量版 <b>C-SORTING Light</b>。<br><br>"
                f"轻量版将移除 AI 模型及相关依赖，保留基础的日期分类、地点分类等核心功能，体积更小、启动更快。Lite 版本将与主版本一同发布在 GitHub Releases 页面，项目地址为：<br><br>"
                f"<a href='https://github.com/nighty35628/c-sorting-lite' style='color:{primary};'>获取 c-sorting-lite</a>"
            )
            guide_scroll_v.addWidget(create_guide_card("关于软件体积", edition_content))

            guide_scroll_v.addWidget(create_guide_card("隐私说明", 
                "本软件采用完全本地化设计，所有分类处理均在您的设备上完成，<b>无需联网</b>，确保您的照片和隐私数据不会外传。"))

            icons_content = (
                f"本软件图标来源于模组 <b>Touhou Little Maid</b> 中的道具“文文的相机”。<br><br>"
                f"• <b>原作者</b>：TartaricAcid、Snownee 及美术团队<br>"
                f"• <b>许可证</b>：<a href='https://creativecommons.org/licenses/by-nc-sa/4.0/' style='color:{primary};'>CC BY-NC-SA 4.0</a><br>"
                f"• <b>模组发布页</b>：<a href='https://modrinth.com/mod/touhou-little-maid' style='color:{primary};'>Touhou Little Maid</a>"
            )
            guide_scroll_v.addWidget(create_guide_card("软件图标声明", icons_content))

            author_content = (
                f"• <b>项目地址</b>：<a href='https://github.com/nighty35628/c-sorting' style='color:{primary};'>GitHub Repository</a><br>"
                f"• <b>作者博客</b>：<a href='https://blog.nightytech.com' style='color:{primary};'>nightytech.com</a><br>"
                f"• <b>开源协议</b>：本项目遵循 <b>GNU Affero General Public License v3.0</b> 开源协议。"
            )
            guide_scroll_v.addWidget(create_guide_card("作者声明", author_content))
        else:
            about_content = (
                "C-SORTING is a modern AI-powered photo organization tool built with PyQt6, designed to help users quickly organize cluttered photo libraries."
                "Whether it's a massive export from a camera or daily casual shots, this tool keeps your media library tidy through various sorting methods."
                f"<div style='text-align: right; color: gray; font-style: italic; margin-top: 5px;'>\"Take all you have, for all you want.\"</div>"
            )
            guide_scroll_v.addWidget(create_guide_card("About", about_content))

            modes_content = (
                f"<p><b>📅 Sort by Date</b><br>Supports archiving by day (YYYY-MM-DD) or month (YYYY-MM), making your timeline clear at a glance.</p>"
                f"<p><b>🌍 Sort by Location</b><br>Based on a built-in offline database, it can identify down to the <b>county</b> level (covering 337 prefecture-level cities). All geolocation parsing is done locally.</p>"
                f"<p><b>🤖 AI Smart Sort</b><br>"
                f"• <b>Logic</b>: Uses an unsupervised classification approach, strictly categorizing based on labels you specify without creating unwanted categories.<br>"
                f"• <b>Model</b>: Powered by the open-source <a href='https://github.com/OFA-Sys/Chinese-CLIP' style='color:{primary};'>Chinese CLIP</a> model (developed by OFA-Sys), following <b>Apache License 2.0</b>.<br>"
                f"• <b>Important</b>: If you only want to filter a specific category, be sure to add a custom \"Other\" label, otherwise all photos will be grouped into the single selected label.<br>"
                f"• <b>Example</b>:<br>"
                f"&nbsp;&nbsp;- Select only \"Flower\": all photos go to \"Flower\".<br>"
                f"&nbsp;&nbsp;- Select \"Flower\" and \"Other\": flowers go to \"Flower\", others go to \"Other\".<br>"
                f"&nbsp;&nbsp;- Select \"Flower\" and \"Parrot\": flowers go to \"Flower\", everything else goes to \"Parrot\".</p>"
            )
            guide_scroll_v.addWidget(create_guide_card("Sorting Modes", modes_content))

            tips_content = (
                f"<b>Pro Tips</b><br>Combine different sorting methods for finer photo management:<br>"
                f"• <b>Location + Date</b>: Sort by location first, then by date within each folder to see your journey unfold.<br>"
                f"• <b>Location + AI</b>: Sort by location, then use AI for semantic classification (e.g., \"Cat\", \"Dog\", \"Scenery\") to find specific trip highlights.<br>"
                f"• <b>Date + AI</b>: Archive by month, then apply AI to find specific subjects like flowers or birds from that period.<br><br>"
                f"<b>Creative AI Usage</b><br>Be creative! For example, label human portraits with \"Cat\" and \"Dog\" to find out who's the kitten or puppy in the group."
            )
            guide_scroll_v.addWidget(create_guide_card("Usage Tips", tips_content))

            edition_content = (
                f"The large file size is mainly due to the built-in local AI model (Chinese CLIP). If you don't need AI features, you can download the lightweight <b>C-SORTING Light</b>.<br><br>"
                f"The Light version removes AI models and dependencies, keeping core features like Date and Location sorting. It is smaller and faster, available on GitHub Releases:<br><br>"
                f"<a href='https://github.com/nighty35628/c-sorting-light' style='color:{primary};'>Get C-SORTING Light</a>"
            )
            guide_scroll_v.addWidget(create_guide_card("Software Size", edition_content))

            guide_scroll_v.addWidget(create_guide_card("Privacy", 
                "Designed with a local-first approach. All processing happens on your device <b>offline</b>, ensuring your photos and privacy never leave your computer."))

            icons_content = (
                f"The software icon is from the \"Aya's Camera\" item in the <b>Touhou Little Maid</b> mod.<br><br>"
                f"• <b>Original Authors</b>: TartaricAcid, Snownee & Art Team<br>"
                f"• <b>License</b>: <a href='https://creativecommons.org/licenses/by-nc-sa/4.0/' style='color:{primary};'>CC BY-NC-SA 4.0</a><br>"
                f"• <b>Mod Page</b>: <a href='https://modrinth.com/mod/touhou-little-maid' style='color:{primary};'>Touhou Little Maid</a>"
            )
            guide_scroll_v.addWidget(create_guide_card("Icon Credits", icons_content))

            author_content = (
                f"• <b>Repository</b>: <a href='https://github.com/nighty35628/c-sorting' style='color:{primary};'>GitHub Repository</a><br>"
                f"• <b>Author's Blog</b>: <a href='https://blog.nightytech.com' style='color:{primary};'>nightytech.com</a><br>"
                f"• <b>License</b>: Licensed under <b>GNU Affero General Public License v3.0</b>."
            )
            guide_scroll_v.addWidget(create_guide_card("Author Info", author_content))

        guide_scroll_v.addStretch()
        guide_scroll.setWidget(guide_scroll_content)
        self.guide_v.addWidget(guide_scroll)

    def update_sidebar_text(self):
        keys = ["nav_dashboard", "nav_history", "nav_settings", "nav_guide"]
        for i, btn in enumerate(self.sidebar_buttons):
            full_text = self.t(keys[i])
            if not self.sidebar_expanded:
                # Show only first character (emoji)
                btn.setText(full_text.split(" ")[0])
                btn.setToolTip(full_text)
            else:
                btn.setText(full_text)
                btn.setToolTip("")

    def on_sidebar_click(self):
        btn = self.sender()
        # Update active state
        for b in self.sidebar_buttons:
            b.setProperty("active", "false")
            b.style().unpolish(b)
            b.style().polish(b)
        
        btn.setProperty("active", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        
        # Switch stack
        if btn == self.btn_dashboard:
            self.stack.setCurrentIndex(0)
        elif btn == self.btn_history:
            self.stack.setCurrentIndex(1)
        elif btn == self.btn_settings:
            self.stack.setCurrentIndex(2)
        elif btn == self.btn_guide:
            self.stack.setCurrentIndex(3)

    def change_language(self, id):
        new_lang = "zh-cn" if id == 0 else "en"
        if new_lang == self.lang:
            return
            
        self.lang = new_lang
        self.config["language"] = self.lang
        self.save_config()
        
        # Update UI labels
        # Sidebar
        self.update_sidebar_text()
        self.app_title_label.setText(self.t("app_name"))

        # REBUILD Guide labels to ensure dynamic text and styles refresh
        self.refresh_guide_page()
        
        # Dashboard
        self.dash_header.setText(self.t("dash_header"))
        self.dash_desc.setText(self.t("dash_desc"))
        self.folder_label.setText(self.t("label_source"))
        self.browse_btn.setText(self.t("btn_browse"))
        self.mode_group_box.setTitle(self.t("group_mode"))
        self.rb_date.setText(self.t("mode_date"))
        self.rb_month.setText(self.t("mode_month"))
        self.rb_city.setText(self.t("mode_city"))
        self.extra_group_box.setTitle(self.t("group_extra"))
        self.cb_copy.setText(self.t("copy_mode"))
        self.cb_recursive.setText(self.t("recursive_mode"))
        self.start_btn.setText(self.t("btn_start"))
        self.status_label.setText(self.t("status_ready"))
        
        # Update AI Tags
        for cb in self.check_boxes:
            tag_key = cb.property("tag_key")
            if tag_key:
                cb.setText(self.t(tag_key))
        self.ai_label_input.setPlaceholderText(self.t("ai_label_tip"))
        self.rb_ai.setText(self.t("mode_ai"))

        # History
        self.hist_header_label.setText(self.t("hist_header"))
        self.btn_clear_hist.setText(self.t("btn_clear_hist"))
        self.refresh_history_ui()
        
        # Settings
        self.sett_header_label.setText(self.t("sett_header"))
        self.theme_group_box.setTitle(self.t("sett_theme"))
        self.dark_mode_cb.setText(self.t("sett_dark"))
        self.color_label_ui.setText(self.t("sett_color"))
        self.lang_group_box.setTitle(self.t("sett_lang"))
        
        # Update color radio buttons text
        for i, rb in enumerate(self.color_rbs):
            rb.setText(self.t(self.themes[i][0]))

        ModernMessageBox.show_message(self, self.t("msg_success"), self.t("lang_changed"), mode="success")

    def toggle_dark_mode(self, enabled):
        self.is_dark_mode = enabled
        self.save_config()
        self.apply_theme()

    def change_theme_color(self, color):
        self.current_theme_color = color
        self.save_config()
        # Ensure we don't accidentally override the entire stylesheet if it affects layout
        self.apply_theme()

    def browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, self.t("label_source"))
        if d:
            self.path_input.setText(d)

    def start_sorting(self):
        folder = self.path_input.text().strip()
        if not folder:
            ModernMessageBox.show_message(self, self.t("msg_warning"), self.t("label_source"), mode="warning")
            return
            
        if not Path(folder).exists():
            ModernMessageBox.show_message(self, self.t("msg_error"), self.t("msg_path_error"), mode="error")
            return

        # Disable UI
        self.set_ui_busy(True)

        # 重置进度条样式为主题色并隐藏（直到第一张图处理完）
        p_bg = "#e5e5ea" if not self.is_dark_mode else "#3a3a3c"
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {p_bg};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {self.current_theme_color};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        
        # Determine mode
        mode = 'date'
        custom_labels = None
        if self.rb_month.isChecked():
            mode = 'month'
        elif self.rb_city.isChecked():
            mode = 'city'
        elif self.rb_ai.isChecked():
            mode = 'ai'
            selected_labels = [cb.text() for cb in self.check_boxes if cb.isChecked()]
            label_text_extra = self.ai_label_input.text().strip()
            if label_text_extra:
                extra_labels = [l.strip() for l in label_text_extra.replace('，', ',').split(',') if l.strip()]
                selected_labels.extend(extra_labels)
            custom_labels = list(set(selected_labels)) # Unique labels
            
        # Start Thread
        model_dir = str(self.res_dir / "assets" / "models" / "chinese-clip-vit-base-patch16")
        self.worker = SortWorker(
            folder, mode, self.cb_copy.isChecked(), 
            recursive=self.cb_recursive.isChecked(),
            lang=self.lang, model_dir=model_dir, custom_labels=custom_labels
        )
        self.worker.progress.connect(self.update_status)
        self.worker.total_count_ready.connect(self.set_total_count)
        self.worker.progress_val.connect(self.update_progress_bar)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
        # Timing start for progress bar logic
        self.sorting_start_time = time.time()
        self.total_count = 0
        self.first_photo_done = False
        self.current_worker = self.worker # Store reference

    def set_total_count(self, count):
        self.total_count = count

    def format_time(self, seconds):
        if seconds < 60:
            return self.t("time_sec")
        else:
            m = int(seconds // 60)
            if seconds % 60 > 0: # 向上取整，让用户有心理预期
                m += 1
            return self.t("time_min_sec").format(m)

    def update_progress_bar(self, value):
        # If we already finished or it's the 100% signal, jump to 5000 (100% in new scale)
        if value >= 100:
            if hasattr(self, 'pb_anim'):
                self.pb_anim.stop()
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(5000)
            self.time_label.setVisible(False)
            return

        # We wait for the first real progress (>0) to calculate timing
        if not self.first_photo_done and value > 0:
            t1 = time.time() - self.sorting_start_time
            self.first_photo_done = True
            
            # Now show and animate fake progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0) # 强制从 0 开始
            self.time_label.setVisible(True)
            
            if self.total_count > 1:
                # T_fake = t1 * (total - 1.5)
                # Ensure t_fake is positive
                t_fake = t1 * max(0.1, (self.total_count - 1.2)) # Use a slightly more realistic multiplier
                t_fake_ms = int(t_fake * 1000)
                
                # Setup time countdown
                self.remaining_seconds = t_fake
                if hasattr(self, 'timer_countdown'):
                    self.timer_countdown.stop()
                else:
                    from PyQt6.QtCore import QTimer
                    self.timer_countdown = QTimer(self)
                    self.timer_countdown.timeout.connect(self.update_countdown)
                self.timer_countdown.start(1000)
                self.update_countdown() # Initial update
                
                if not hasattr(self, 'pb_anim'):
                    self.pb_anim = QPropertyAnimation(self.progress_bar, b"value")
                
                self.pb_anim.stop()
                
                self.pb_anim.setEasingCurve(QEasingCurve.Type.InOutSine) 
                self.pb_anim.setDuration(t_fake_ms)
                self.pb_anim.setStartValue(0)
                self.pb_anim.setEndValue(4800)
                
                self.pb_anim.setKeyValueAt(0.15, 4800 * 0.15) 
                self.pb_anim.setKeyValueAt(0.30, 4800 * 0.45) 
                self.pb_anim.setKeyValueAt(0.60, 4800 * 0.60) 
                self.pb_anim.setKeyValueAt(0.75, 4800 * 0.88) 
                
                self.pb_anim.start()
            elif self.total_count == 1:
                 self.progress_bar.setValue(2500)
            return

    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.time_label.setText(self.t("remaining_time").format(self.format_time(self.remaining_seconds)))
            self.remaining_seconds -= 1
        else:
            self.time_label.setText(self.t("remaining_time").format(self.format_time(0)))
            self.timer_countdown.stop()

    def closeEvent(self, event):
        res = ModernMessageBox.ask_exit_mode(self)
        if res == 1: # Background
            if hasattr(self, 'current_worker') and self.current_worker.isRunning() and self.rb_ai.isChecked():
                est = self.time_label.text().split(": ")[-1] if self.time_label.isVisible() else "..."
                self.tray_icon.showMessage(
                    self.t("msg_ai_running_title"),
                    self.t("msg_ai_running_body").format(est),
                    QSystemTrayIcon.MessageIcon.Information,
                    5000
                )
            self.hide()
            event.ignore() 
        elif res == 2: # Exit
            if hasattr(self, 'current_worker') and self.current_worker.isRunning():
                self.current_worker.terminate()
            event.accept()
        else:
            event.ignore()

    def update_status(self, msg):
        self.status_label.setText(msg)
        # Restart animation to highlight update, but check if we are already pulsating
        if self.pulse_anim.state() != QAbstractAnimation.State.Running:
            self.status_anim.start()

    def set_ui_busy(self, busy):
        self.start_btn.setEnabled(not busy)
        self.path_input.setEnabled(not busy)
        from PyQt6.QtCore import QTimer
        if busy:
            # 800ms 渐显
            self.status_anim.stop()
            self.pulse_anim.stop()
            self.status_label.show()
            self.status_label.setStyleSheet("opacity: 1.0;") # 确保开始时文字是不透明的
            self.status_anim.start()
            # 结束后接呼吸动画
            QTimer.singleShot(800, lambda: self.pulse_anim.start() if not self.start_btn.isEnabled() else None)
        else:
            # 处理完成后停止呼吸动画，但不 hide 也不设为透明，让它留存
            self.pulse_anim.stop()
            self.status_anim.stop()
            self.opacity_effect.setOpacity(1.0) # 强制设为不透明
            self.status_label.show()
            
    def on_finished(self, result):
        self.set_ui_busy(False)
        self.time_label.setVisible(False)
        if hasattr(self, 'timer_countdown') and self.timer_countdown.isActive():
            self.timer_countdown.stop()
        # 处理完成后进度条保持 100%
        if result.get("success"):
            self.progress_bar.setValue(5000)
            self.progress_bar.show()
            
            # 将结果留存在原本的 status_label 位置，而不是进度条里面
            count = result.get("count", 0)
            finish_text = self.t("status_done").format(count)
            self.status_label.setText(finish_text)
            self.status_label.show()
        else:
            self.progress_bar.hide()
            self.status_label.setText(self.t("status_ready"))
            
        msg = result["msg"]
        
        if result.get("success"):
            target_path = result.get("target")
            self.save_history(result)
            self.refresh_history_ui()
            ModernMessageBox.show_message(self, self.t("msg_success"), msg, mode="success", target_path=target_path)
        else:
            ModernMessageBox.show_message(self, self.t("msg_warning"), msg, mode="warning")

    def refresh_history_ui(self):
        # Clear current list
        for i in reversed(range(self.hist_list_layout.count())): 
            self.hist_list_layout.itemAt(i).widget().setParent(None)
            
        if not self.history_data:
            empty_label = QLabel(self.t("hist_empty"))
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #86868b; margin-top: 50px;")
            self.hist_list_layout.addWidget(empty_label)
            return

        for item in self.history_data:
            frame = QFrame()
            frame.setObjectName("HistoryItem")
            f_layout = QVBoxLayout(frame)
            f_layout.setSpacing(10)
            
            # --- Top Area ---
            top_line = QHBoxLayout()
            time_label = QLabel(item["time"])
            time_label.setStyleSheet(f"font-weight: bold; color: {self.current_theme_color};")
            count_label = QLabel(self.t("hist_proc").format(item['count']))
            count_label.setStyleSheet("font-weight: bold;")
            top_line.addWidget(time_label)
            top_line.addStretch()
            top_line.addWidget(count_label)
            f_layout.addLayout(top_line)
            
            # --- Paths ---
            source_label = QLabel(f"{self.t('hist_src')}: {item['source']}")
            source_label.setStyleSheet("color: #86868b; font-size: 12px;")
            source_label.setWordWrap(True)
            
            target_label = QLabel(f"{self.t('hist_dst')}: {item['target']}")
            target_label.setStyleSheet("color: #86868b; font-size: 12px;")
            target_label.setWordWrap(True)
            
            f_layout.addWidget(source_label)
            f_layout.addWidget(target_label)

            # --- Bottom Area ---
            mode_map = {"date": self.t("opt_date"), "month": self.t("opt_month"), "city": self.t("opt_city")}
            mode_text = f"{self.t('hist_mode')}: {mode_map.get(item['mode'], item['mode'])}"
            
            bottom_line = QHBoxLayout()
            mode_label = QLabel(mode_text)
            mode_label.setStyleSheet("font-size: 12px;")
            bottom_line.addWidget(mode_label)
            bottom_line.addStretch()
            
            open_btn = self._create_hist_btn(item['target'])
            bottom_line.addWidget(open_btn)
            f_layout.addLayout(bottom_line)
            
            self.hist_list_layout.addWidget(frame)

    def _create_hist_btn(self, target_path):
        btn = QPushButton(self.t('btn_open'))
        btn.setObjectName("SecondaryButton")
        btn.setFixedWidth(130)
        btn.setFixedHeight(32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton#SecondaryButton {{ font-size: 12px; padding: 5px; border-radius: 8px; }}")
        btn.clicked.connect(lambda checked, p=target_path: self.open_folder(p))
        return btn

    def open_folder(self, path):
        path = os.path.normpath(path)
        if not os.path.exists(path):
            ModernMessageBox.show_message(self, self.t("msg_warning"), self.t("msg_path_error"), mode="warning")
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            ModernMessageBox.show_message(self, self.t("msg_error"), f"{self.t('msg_open_error')}\n{str(e)}", mode="error")

    def clear_history(self):
        # Clear JSON file
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            # Update data and UI
            self.history_data = [] # Explicitly clear the in-memory data
            self.refresh_history_ui()
            ModernMessageBox.show_message(self, self.t("msg_success"), self.t("hist_empty"), mode="success")
        except Exception as e:
            print(f"Error clearing history: {e}")

    def on_error(self, err):
        self.set_ui_busy(False)
        self.progress_bar.setVisible(False)
        self.time_label.setVisible(False)
        if hasattr(self, 'timer_countdown') and self.timer_countdown.isActive():
            self.timer_countdown.stop()
        self.status_label.setText(self.t("status_error"))
        ModernMessageBox.show_message(self, self.t("msg_error"), f"{self.t('msg_proc_error')}\n{err}", mode="error")

if __name__ == '__main__':
    app_qt = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app_qt.exec())
