
import sys
import json
import os
import subprocess
import base64
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QRadioButton, QCheckBox, QFileDialog, 
    QMessageBox, QGroupBox, QButtonGroup, QProgressBar,
    QGraphicsOpacityEffect, QApplication, QStackedWidget,
    QGridLayout, QScrollArea, QFrame, QDialog, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, QAbstractAnimation, QByteArray,
    QParallelAnimationGroup
)
from PyQt6.QtGui import QPixmap, QIcon
from ..sorter import scan_folder, group_by_date, group_by_month, group_by_city, move_grouped_items

TRANSLATIONS = {
    "zh-cn": {
        "app_name": "C-SORTING",
        "nav_dashboard": "🏠 整理照片",
        "nav_history": "🕒 处理历史",
        "nav_settings": "⚙️ 偏好设置",
        "dash_header": "欢迎使用照片智能整理",
        "dash_desc": "简单几步，让您的照片库井井有条。",
        "label_source": "选择源文件夹",
        "btn_browse": "选取...",
        "group_mode": "分类方式",
        "mode_date": "按日期 (推荐)",
        "mode_month": "按月份",
        "mode_city": "按地理位置",
        "group_extra": "操作选项",
        "copy_mode": "保留原文件 (副本)",
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
    },
    "en": {
        "app_name": "C-SORTING",
        "nav_dashboard": "🏠 Dashboard",
        "nav_history": "🕒 History",
        "nav_settings": "⚙️ Settings",
        "dash_header": "Smart Photo Sorter",
        "dash_desc": "Organize your photo library in a few simple steps.",
        "label_source": "Select Source Folder",
        "btn_browse": "Browse...",
        "group_mode": "Sorting Mode",
        "mode_date": "By Date (Recommended)",
        "mode_month": "By Month",
        "mode_city": "By Location",
        "group_extra": "Options",
        "copy_mode": "Keep Originals (Copy)",
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
    }
}

class ModernMessageBox(QDialog):
    def __init__(self, parent, title, message, mode="info", theme_color="#fa2d48", is_dark=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
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
        
        # OK Button - Minimalist Style
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumHeight(44)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_color};
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 15px;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: {theme_color};
                opacity: 0.9;
            }}
        """)
        frame_layout.addWidget(ok_btn)
        
        layout.addWidget(self.frame)

    @staticmethod
    def show_message(parent, title, message, mode="info"):
        theme = parent.current_theme_color if hasattr(parent, 'current_theme_color') else "#fa2d48"
        dark = parent.is_dark_mode if hasattr(parent, 'is_dark_mode') else False
        dlg = ModernMessageBox(parent, title, message, mode, theme, dark)
        dlg.exec()

class SortWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)  # Changed to dict to return more info
    error = pyqtSignal(str)

    def __init__(self, folder, mode, copy_mode, lang="zh-cn"):
        super().__init__()
        self.folder = Path(folder)
        self.mode = mode
        self.copy_mode = copy_mode
        self.lang = lang

    def t(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["zh-cn"]).get(key, key)

    def run(self):
        try:
            self.progress.emit(self.t("proc_scanning"))
            items = scan_folder(self.folder)
            count = len(items)
            if not items:
                self.finished.emit({"success": False, "msg": self.t("proc_no_files")})
                return

            self.progress.emit(self.t("proc_organizing").format(count))
            
            if self.mode == 'date':
                groups = group_by_date(items)
                target = self.folder.parent / (self.folder.name + '_sorted_by_date')
            elif self.mode == 'month':
                groups = group_by_month(items)
                target = self.folder.parent / (self.folder.name + '_sorted_by_month')
            else: # city
                groups = group_by_city(items)
                target = self.folder.parent / (self.folder.name + '_sorted_by_city')
            
            action_key = "proc_copying" if self.copy_mode else "proc_moving"
            self.progress.emit(self.t(action_key))
            
            move_grouped_items(groups, target, copy=self.copy_mode)
            
            self.finished.emit({
                "success": True,
                "msg": self.t("proc_done").format(target),
                "count": count,
                "target": str(target),
                "source": str(self.folder),
                "mode": self.mode,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        except Exception as e:
            self.error.emit(str(e))


class App(QWidget):
    def __init__(self):
        super().__init__()
        
        # Path configuration for portability (Handles Dev and EXE)
        if getattr(sys, 'frozen', False):
            # For data (configs): Next to the EXE
            self.base_dir = Path(sys.executable).parent
            # For resources (images/assets): Inside the bundled directory (_internal)
            self.res_dir = Path(getattr(sys, '_MEIPASS', self.base_dir))
        else:
            self.base_dir = Path(__file__).parent.parent.parent
            self.res_dir = self.base_dir
            
        # Load config (theme/color)
        self.config_file = self.base_dir / "config.json"
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
        
        self.history_file = self.base_dir / "history.json"
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
            
        self.apply_theme()
        self.setup_ui()

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
        #Sidebar QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 12px;
            padding: 12px;
            font-weight: 500;
            margin: 4px 10px;
            color: {text_color};
            font-size: 16px;
        }}
        #Sidebar[collapsed="true"] QPushButton {{
            text-align: center;
            padding: 12px 0;
            margin: 4px 5px;
        }}
        #Sidebar[collapsed="false"] QPushButton {{
            text-align: left;
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
            image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAGVKw4bAAABCklEQVRYhe2UO27CQBQA3zMSDR0lNX24ADkAmBvAGbhAGiRuADUdOUIipU8OkPS0UFJBQaKhYBEPK4mNP0uzI7mwvX4z0lorEggE7oxWORxQEemJCCLyqqpU6fstYMKFnm/5gGv6PuVtYGvkL0DkS94Avox8BTR9yRV4NvId8OBF7gLGiX0f5h0UAbG7Mu0d8Ah8G/ksl9wNi82gRVoE0AI25pt3oF5WwL8RQB34MGvXQCu33A2NnDQ1ApibNQegW0h+SwQwSrwflyLPEgF0gL15vuR09pfLHxFLTgfMmU+gUbo8JeLMFmhXJs8QEVcuT0S82a0oOvPmnwaoiciTu52q6k/RiEAgcFeOrMjv32JtTssAAAAASUVORK5CYII=);
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
        
        self.sidebar_buttons = [self.btn_dashboard, self.btn_history, self.btn_settings]
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

        self.version_label = QLabel("v1.0.8")
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
        self.mode_group_box.setMinimumWidth(180) # Prevent text squishing
        mode_v = QVBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.rb_date = QRadioButton(self.t("mode_date"))
        self.rb_date.setChecked(True)
        self.rb_month = QRadioButton(self.t("mode_month"))
        self.rb_city = QRadioButton(self.t("mode_city"))
        for rb in [self.rb_date, self.rb_month, self.rb_city]:
            self.mode_group.addButton(rb)
            mode_v.addWidget(rb)
        self.mode_group_box.setLayout(mode_v)
        
        self.extra_group_box = QGroupBox(self.t("group_extra"))
        self.extra_group_box.setMinimumWidth(180)
        extra_v = QVBoxLayout()
        self.cb_copy = QCheckBox(self.t("copy_mode"))
        self.cb_copy.setChecked(True)
        extra_v.addWidget(self.cb_copy)
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

        # Status
        self.status_label = QLabel(self.t("status_ready"))
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.addWidget(self.status_label)
        dash_layout.addStretch()
        
        self.stack.addWidget(dash_page)

        # --- Page 1: History ---
        self.history_page = QWidget()
        self.hist_v = QVBoxLayout(self.history_page)
        self.hist_v.setContentsMargins(15, 30, 15, 30)
        
        self.hist_header_label = QLabel(self.t("hist_header"))
        self.hist_header_label.setObjectName("Header")
        self.hist_v.addWidget(self.hist_header_label)
        
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

        hbox.addWidget(self.stack)

        # Animations
        self.opacity_effect = QGraphicsOpacityEffect(self.status_label)
        self.status_label.setGraphicsEffect(self.opacity_effect)
        
        self.status_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.status_anim.setDuration(800)
        self.status_anim.setStartValue(0.3)
        self.status_anim.setEndValue(1.0)
        self.status_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.pulse_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.pulse_anim.setDuration(1000)
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

    def update_sidebar_text(self):
        keys = ["nav_dashboard", "nav_history", "nav_settings"]
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
        self.start_btn.setText(self.t("btn_start"))
        self.status_label.setText(self.t("status_ready"))
        
        # History
        self.hist_header_label.setText(self.t("hist_header"))
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
        self.app_title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; margin-left: 20px; margin-bottom: 2px; color: {color};")
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
        
        # Determine mode
        mode = 'date'
        if self.rb_month.isChecked():
            mode = 'month'
        elif self.rb_city.isChecked():
            mode = 'city'
            
        # Start Thread
        self.worker = SortWorker(folder, mode, self.cb_copy.isChecked(), self.lang)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def update_status(self, msg):
        self.status_label.setText(msg)
        # Restart animation to highlight update, but check if we are already pulsating
        if self.pulse_anim.state() != QAbstractAnimation.State.Running:
            self.status_anim.start()

    def set_ui_busy(self, busy):
        self.start_btn.setEnabled(not busy)
        self.path_input.setEnabled(not busy)
        if busy:
            self.status_anim.stop()
            self.pulse_anim.start()
        else:
            self.pulse_anim.stop()
            self.opacity_effect.setOpacity(1.0)

    def on_finished(self, result):
        self.set_ui_busy(False)
        msg = result["msg"]
        self.status_label.setText(self.t("status_done").format(result.get("count", 0)))
        
        if result.get("success"):
            self.save_history(result)
            self.refresh_history_ui()
            ModernMessageBox.show_message(self, self.t("msg_success"), msg, mode="success")
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

    def on_error(self, err):
        self.set_ui_busy(False)
        self.status_label.setText(self.t("status_error"))
        ModernMessageBox.show_message(self, self.t("msg_error"), f"{self.t('msg_proc_error')}\n{err}", mode="error")

if __name__ == '__main__':
    app_qt = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app_qt.exec())
