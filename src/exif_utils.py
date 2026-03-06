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
EXIF 解析工具：读取拍摄时间与 GPS 信息（如果存在）。
对初学者作了较多注释，函数尽量返回易用结构。
"""
from typing import Optional, Tuple, Dict
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def _get_exif(img_path: str) -> Optional[dict]:
    try:
        img = Image.open(img_path)
        exif = img._getexif()
        if not exif:
            return None
        # 将数字 tag 转为可读名字
        exif_readable = {}
        for tag, val in exif.items():
            decoded = TAGS.get(tag, tag)
            exif_readable[decoded] = val
        return exif_readable
    except Exception:
        return None

def _get_gps_info(exif: dict) -> Optional[dict]:
    gps_info = exif.get('GPSInfo')
    if not gps_info:
        return None
    gps = {}
    for key in gps_info.keys():
        name = GPSTAGS.get(key, key)
        gps[name] = gps_info[key]
    return gps

def _convert_to_degrees(value) -> float:
    # EXIF GPS 值通常是 ((num, den), (num, den), (num, den)) 表示度/分/秒
    def _rational_to_float(r):
        return r[0] / r[1] if isinstance(r, tuple) else float(r)
    d = _rational_to_float(value[0])
    m = _rational_to_float(value[1])
    s = _rational_to_float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_photo_metadata(path: str) -> Dict[str, Optional[object]]:
    """
    返回字典，包含:
      - datetime: 照片拍摄时间字符串（如果存在），优先使用 DateTimeOriginal
      - gps: (lat, lon) 或 None
    """
    meta = {"datetime": None, "gps": None}
    exif = _get_exif(path)
    if not exif:
        return meta
    # 获取时间
    dt = exif.get('DateTimeOriginal') or exif.get('DateTime')
    if dt:
        meta['datetime'] = dt
    # 获取 GPS
    gps = _get_gps_info(exif)
    if gps:
        try:
            lat = _convert_to_degrees(gps['GPSLatitude'])
            if gps.get('GPSLatitudeRef') in ['S', 's']:
                lat = -lat
            lon = _convert_to_degrees(gps['GPSLongitude'])
            if gps.get('GPSLongitudeRef') in ['W', 'w']:
                lon = -lon
            meta['gps'] = (lat, lon)
        except Exception:
            meta['gps'] = None
    return meta
