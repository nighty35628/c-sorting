
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
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QByteArray
from PyQt6.QtGui import QPixmap
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
        "sett_dark": "启用深色模式 (Night Mode)",
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

    def __init__(self, folder, mode, copy_mode):
        super().__init__()
        self.folder = Path(folder)
        self.mode = mode
        self.copy_mode = copy_mode

    def run(self):
        try:
            self.progress.emit("正在扫描文件...")
            items = scan_folder(self.folder)
            count = len(items)
            if not items:
                self.finished.emit({"success": False, "msg": "没有找到可分类的图片。"})
                return

            self.progress.emit(f"找到 {count} 张图片，正在分类...")
            
            if self.mode == 'date':
                groups = group_by_date(items)
                target = self.folder.parent / (self.folder.name + '_sorted_by_date')
            elif self.mode == 'month':
                groups = group_by_month(items)
                target = self.folder.parent / (self.folder.name + '_sorted_by_month')
            else: # city
                groups = group_by_city(items)
                target = self.folder.parent / (self.folder.name + '_sorted_by_city')
            
            action_str = "复制" if self.copy_mode else "移动"
            self.progress.emit(f"正在{action_str}文件...")
            
            move_grouped_items(groups, target, copy=self.copy_mode)
            
            self.finished.emit({
                "success": True,
                "msg": f"完成！目标文件夹：\n{target}",
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
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent.parent.parent
            
        # Load config (theme/color)
        self.config_file = self.base_dir / "config.json"
        self.config = self.load_config()
        
        # Theme state
        self.current_theme_color = self.config.get("theme_color", "#fa2d48")  # Default Apple Red
        self.is_dark_mode = self.config.get("dark_mode", False)
        self.lang = self.config.get("language", "zh-cn")
        
        self.history_file = self.base_dir / "history.json"
        self.history_data = self.load_history()
        
        self.setWindowTitle('C-SORTING')
        self.resize(760, 520)
        self.apply_theme()
        self.setup_ui()

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
        
        return f"""
        QWidget {{
            background-color: {bg};
            color: {text_color};
            font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            font-size: 14px;
        }}
        #Sidebar {{
            background-color: {sidebar_bg};
            border-right: 1px solid {border_color};
            min-width: 200px;
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
            border-radius: 8px;
            padding: 10px 15px;
            text-align: left;
            font-weight: 500;
            margin: 2px 10px;
            color: {text_color};
        }}
        #Sidebar QPushButton:hover {{
            background-color: {"#e8e8ed" if not self.is_dark_mode else "#2c2c2e"};
        }}
        #Sidebar QPushButton[active="true"] {{
            background-color: {bg};
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
            border-radius: 15px;
            margin-top: 20px;
            padding-top: 20px;
            font-weight: bold;
            color: {text_color};
        }}
        QRadioButton, QCheckBox {{
            spacing: 8px;
            color: {text_color};
        }}
        QRadioButton::indicator, QCheckBox::indicator {{
            width: 22px;
            height: 22px;
            border-radius: 11px;
            border: 2px solid {border_color};
            background-color: {bg};
        }}
        QRadioButton::indicator:checked, QCheckBox::indicator:checked {{
            background-color: {primary};
            border: 2px solid {primary};
            border-radius: 11px;
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
        # Overall Horizontal Layout
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        # 1. Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        self.app_title_label = QLabel(self.t("app_name"))
        self.app_title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; margin: 20px; color: {self.current_theme_color};")
        sidebar_layout.addWidget(self.app_title_label)

        self.btn_dashboard = QPushButton(self.t("nav_dashboard"))
        self.btn_dashboard.setProperty("active", "true")
        self.btn_history = QPushButton(self.t("nav_history"))
        self.btn_settings = QPushButton(self.t("nav_settings"))
        
        self.sidebar_buttons = [self.btn_dashboard, self.btn_history, self.btn_settings]
        for btn in self.sidebar_buttons:
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(self.on_sidebar_click)
        
        sidebar_layout.addStretch()
        
        version_label = QLabel("v2.1.0-Theme")
        version_label.setStyleSheet("color: #86868b; font-size: 11px; margin: 20px;")
        sidebar_layout.addWidget(version_label)
        
        hbox.addWidget(sidebar)

        # 2. Main content stack
        self.stack = QStackedWidget()
        self.stack.setObjectName("MainContent")
        
        # --- Page 0: Dashboard ---
        dash_page = QWidget()
        dash_layout = QVBoxLayout(dash_page)
        dash_layout.setContentsMargins(40, 40, 40, 40)
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

        # Options area
        options_layout = QHBoxLayout()
        
        self.mode_group_box = QGroupBox(self.t("group_mode"))
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
        extra_v = QVBoxLayout()
        self.cb_copy = QCheckBox(self.t("copy_mode"))
        self.cb_copy.setChecked(True)
        extra_v.addWidget(self.cb_copy)
        extra_v.addStretch()
        self.extra_group_box.setLayout(extra_v)
        
        options_layout.addWidget(self.mode_group_box)
        options_layout.addWidget(self.extra_group_box)
        dash_layout.addLayout(options_layout)

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
        self.hist_v.setContentsMargins(40, 40, 40, 40)
        
        self.hist_header_label = QLabel(self.t("hist_header"))
        self.hist_header_label.setObjectName("Header")
        self.hist_v.addWidget(self.hist_header_label)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
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
        
        # Dark mode toggle
        self.dark_mode_cb = QCheckBox(self.t("sett_dark"))
        self.dark_mode_cb.setChecked(self.is_dark_mode)
        self.dark_mode_cb.toggled.connect(self.toggle_dark_mode)
        theme_layout.addWidget(self.dark_mode_cb)
        
        # Theme color selection
        self.color_label_ui = QLabel(self.t("sett_color"))
        theme_layout.addWidget(self.color_label_ui)
        
        colors_grid = QGridLayout()
        themes = [
            ("红色", "#fa2d48"), ("蓝色", "#007aff"), ("绿色", "#34c759"), ("紫色", "#af52de"), ("橙色", "#ff9500"),
            ("粉色", "#ff2d55"), ("黄色", "#ffcc00"), ("青色", "#5ac8fa"), ("靛蓝", "#5856d6"), ("灰色", "#8e8e93")
        ]
        self.color_group = QButtonGroup(self)
        for i, (name, hex_code) in enumerate(themes):
            rb = QRadioButton(name)
            if hex_code == self.current_theme_color:
                rb.setChecked(True)
            self.color_group.addButton(rb, i)
            row = i // 5
            col = i % 5
            colors_grid.addWidget(rb, row, col)
        
        self.color_group.idClicked.connect(lambda id: self.change_theme_color(themes[id][1]))
        
        theme_layout.addLayout(colors_grid)
        self.theme_group_box.setLayout(theme_layout)
        sett_v.addWidget(self.theme_group_box)

        # Language Section
        self.lang_group_box = QGroupBox(self.t("sett_lang"))
        lang_layout = QHBoxLayout()
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
        
        self.lang_group_box.setLayout(lang_layout)
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
        self.btn_dashboard.setText(self.t("nav_dashboard"))
        self.btn_history.setText(self.t("nav_history"))
        self.btn_settings.setText(self.t("nav_settings"))
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

        ModernMessageBox.show_message(self, self.t("msg_success"), self.t("lang_changed"), mode="success")

    def toggle_dark_mode(self, enabled):
        self.is_dark_mode = enabled
        self.save_config()
        self.apply_theme()

    def change_theme_color(self, color):
        self.current_theme_color = color
        self.save_config()
        self.app_title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; margin: 20px; color: {color};")
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
        self.worker = SortWorker(folder, mode, self.cb_copy.isChecked())
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
            
            top_line = QHBoxLayout()
            time_label = QLabel(item["time"])
            time_label.setStyleSheet(f"font-weight: bold; color: {self.current_theme_color};")
            count_label = QLabel(self.t("hist_proc").format(item['count']))
            count_label.setStyleSheet("font-weight: bold;")
            top_line.addWidget(time_label)
            top_line.addStretch()
            top_line.addWidget(count_label)
            
            source_label = QLabel(f"{self.t('hist_src')}: {item['source']}")
            source_label.setStyleSheet("color: #86868b; font-size: 12px;")
            
            target_label = QLabel(f"{self.t('hist_dst')}: {item['target']}")
            target_label.setStyleSheet("color: #86868b; font-size: 12px;")
            
            bottom_line = QHBoxLayout()
            mode_map = {"date": self.t("opt_date"), "month": self.t("opt_month"), "city": self.t("opt_city")}
            mode_label = QLabel(f"{self.t('hist_mode')}: {mode_map.get(item['mode'], item['mode'])}")
            mode_label.setStyleSheet("font-size: 12px;")
            bottom_line.addWidget(mode_label)
            bottom_line.addStretch()

            open_btn = QPushButton(self.t('btn_open'))
            open_btn.setObjectName("SecondaryButton")
            open_btn.setFixedWidth(130)
            open_btn.setFixedHeight(32)
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.setStyleSheet(f"""
                QPushButton#SecondaryButton {{ 
                    font-size: 12px; 
                    padding: 5px;
                    border-radius: 8px;
                }}
            """)
            # 使用闭包捕获路径
            target_path = item['target']
            open_btn.clicked.connect(lambda checked, p=target_path: self.open_folder(p))
            bottom_line.addWidget(open_btn)

            f_layout.addLayout(top_line)
            f_layout.addWidget(source_label)
            f_layout.addWidget(target_label)
            f_layout.addLayout(bottom_line)
            
            self.hist_list_layout.addWidget(frame)

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
