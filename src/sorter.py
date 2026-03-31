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
照片扫描与排序核心逻辑。
- 支持按时间（YYYY-MM-DD）或按城市分类
- 会在目标目录下创建文件夹并移动文件
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import shutil
from .exif_utils import get_photo_metadata
from .geocode import latlon_to_city
from .models.recognition import Recognizer
import os
import time

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.jfif', '.png', '.heic', '.heif', '.tif', '.tiff', '.webp', '.bmp', '.gif'}
VIDEO_SUFFIXES = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'}

class MediaItem:
    def __init__(self, path: Path, media_type: str):
        self.path = path
        self.media_type = media_type  # 'image' or 'video'
        self.meta = self._get_metadata()
        self._ai_tag = None

    def _get_metadata(self) -> Dict[str, Optional[object]]:
        if self.media_type == 'image':
            meta = get_photo_metadata(str(self.path))
            # Fallback to file creation/modification time if EXIF is missing
            if not meta.get('datetime'):
                meta['datetime'] = self._get_file_datetime()
            return meta
        else:
            # Video metadata fallback to file time
            return {"datetime": self._get_file_datetime(), "gps": None}

    def ai_tag(self, recognizer: Optional[Recognizer], custom_labels: Optional[List[str]] = None, ai_quality: str = "precise") -> str:
        if self.media_type != 'image' or not recognizer:
            return "其他"
        if not self._ai_tag:
            self._ai_tag = recognizer.predict(str(self.path), custom_labels, ai_quality=ai_quality)
        return self._ai_tag

    def _get_file_datetime(self) -> str:
        """Fallback to file creation time if EXIF is missing (OS dependent)."""
        stat = self.path.stat()
        # In some OSes, st_ctime is the creation time, in others it's the metadata change time
        # On Windows, st_ctime is creation time. On Linux, it's metadata change time.
        # Commonly, min(st_mtime, st_ctime) might be closer to creation time on some systems.
        ctime = stat.st_ctime
        mtime = stat.st_mtime
        earliest = min(ctime, mtime)
        return time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(earliest))

    def date_key(self) -> Optional[str]:
        dt = self.meta.get('datetime')
        if not dt:
            return None
        # EXIF DateTime format: "YYYY:MM:DD HH:MM:SS"
        date_part = dt.split(' ')[0].replace(':', '-')
        return date_part

    def month_key(self) -> Optional[str]:
        dt = self.meta.get('datetime')
        if not dt:
            return None
        # 返回 YYYY-MM
        parts = dt.split(' ')[0].split(':')
        return f"{parts[0]}-{parts[1]}"

    def gps(self) -> Optional[Tuple[float,float]]:
        return self.meta.get('gps')

    def city(self) -> Optional[str]:
        gps = self.gps()
        if not gps:
            return None
        return latlon_to_city(gps[0], gps[1])

def scan_folder(folder: Path, recursive: bool = True) -> List[MediaItem]:
    items = []
    generator = folder.rglob('*') if recursive else folder.glob('*')
    for p in generator:
        if not p.is_file():
            continue
        suffix = p.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            items.append(MediaItem(p, 'image'))
        elif suffix in VIDEO_SUFFIXES:
            items.append(MediaItem(p, 'video'))
    return items

def group_by_date(items: List[MediaItem]) -> Dict[str, List[MediaItem]]:
    groups = {}
    for it in items:
        key = it.date_key() or 'unknown_date'
        groups.setdefault(key, []).append(it)
    return groups

def group_by_month(items: List[MediaItem]) -> Dict[str, List[MediaItem]]:
    groups = {}
    for it in items:
        key = it.month_key() or 'unknown_month'
        groups.setdefault(key, []).append(it)
    return groups

def group_by_city(items: List[MediaItem]) -> Dict[str, List[MediaItem]]:
    groups = {}
    for it in items:
        key = it.city() or 'unknown_city'
        groups.setdefault(key, []).append(it)
    return groups

def group_by_ai(items: List[MediaItem], recognizer: Recognizer, custom_labels: Optional[List[str]] = None, progress_callback=None, ai_quality: str = "precise") -> Dict[str, List[MediaItem]]:
    groups = {}
    total = len(items)
    for idx, it in enumerate(items):
        # 仅对图片进行 AI 识别
        if it.media_type == 'image':
            key = it.ai_tag(recognizer, custom_labels, ai_quality=ai_quality)
        else:
            key = "视频"
        groups.setdefault(key, []).append(it)
        if progress_callback:
            progress_callback(int((idx + 1) / total * 100))
    return groups

def move_grouped_items(groups: Dict[str, List[MediaItem]], target_base: Path, copy: bool = False) -> None:
    """把分组里的文件移动或拷贝到 target_base/<group>/ 下。"""
    target_base.mkdir(parents=True, exist_ok=True)
    for group, items in groups.items():
        safe_name = group.replace('/', '_')
        dest_dir = target_base / safe_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        for it in items:
            dest = dest_dir / it.path.name
            if dest.exists():
                # 避免覆盖，简单在文件名后加索引
                stem = dest.stem
                suffix = dest.suffix
                i = 1
                while True:
                    new_name = f"{stem}_{i}{suffix}"
                    new_dest = dest_dir / new_name
                    if not new_dest.exists():
                        dest = new_dest
                        break
                    i += 1
            try:
                if copy:
                    shutil.copy2(it.path, dest)
                else:
                    shutil.move(str(it.path), str(dest))
            except Exception:
                # 对新手用户暂时只做简单处理：继续下一张
                continue
