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

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.heic', '.tif', '.tiff'}

class PhotoItem:
    def __init__(self, path: Path):
        self.path = path
        self.meta = get_photo_metadata(str(path))

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

def scan_folder(folder: Path) -> List[PhotoItem]:
    items = []
    for p in folder.rglob('*'):
        if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES:
            items.append(PhotoItem(p))
    return items

def group_by_date(items: List[PhotoItem]) -> Dict[str, List[PhotoItem]]:
    groups = {}
    for it in items:
        key = it.date_key() or 'unknown_date'
        groups.setdefault(key, []).append(it)
    return groups

def group_by_month(items: List[PhotoItem]) -> Dict[str, List[PhotoItem]]:
    groups = {}
    for it in items:
        key = it.month_key() or 'unknown_month'
        groups.setdefault(key, []).append(it)
    return groups

def group_by_city(items: List[PhotoItem]) -> Dict[str, List[PhotoItem]]:
    groups = {}
    for it in items:
        key = it.city() or 'unknown_city'
        groups.setdefault(key, []).append(it)
    return groups

def move_grouped_items(groups: Dict[str, List[PhotoItem]], target_base: Path, copy: bool = False) -> None:
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
