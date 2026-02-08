"""
反向地理编码：经纬度 -> 城市名。
由于 Nominatim (OpenStreetMap) 在国内访问不稳定，
此处改为使用高德地图 (Amap) 或百度地图的 API 逻辑。
为了让新手直接能跑，我们先提供一个“离线/备用”逻辑，并注释如何接入高德 API。
"""
import requests
import time
from typing import Optional, Dict

# 简单的内存缓存
_city_cache: Dict[str, str] = {}

def latlon_to_city(lat: float, lon: float) -> Optional[str]:
    """
    将经纬度转换为城市。
    """
    cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
    if cache_key in _city_cache:
        return _city_cache[cache_key]

    # --- 方案 A: 使用腾讯位置服务 API ---
    # 请再次核对这个 Key 是否正确
    api_key = "YKRBZ-67C6W-SOORA-Y6243-4VSXJ-R5BMG"
    url = f"https://apis.map.qq.com/ws/geocoder/v1/?location={lat},{lon}&key={api_key}"
    
    # 增加较长的延迟，确保不触发腾讯地图每秒仅 5 次（未认证）或更低的并发限制
    time.sleep(0.33) 
    
    try:
        # 腾讯地图 API 默认并发限制较低，我们通过增加间隔来规避
        resp = requests.get(url, timeout=5).json()
        status = resp.get('status')
        message = resp.get('message')
        
        if status == 0:
            ad_info = resp['result']['ad_info']
            city = ad_info.get('city') or ad_info.get('province')
            if city:
                _city_cache[cache_key] = city
                return city
        else:
            # 打印非常详细的错误，请在终端查看
            print(f"--- 腾讯 API 调试信息 ---")
            print(f"状态码: {status}")
            print(f"错误消息: {message}")
            print(f"请求坐标: {lat}, {lon}")
            print(f"------------------------")
            
            if status == 121:
                print("提示: 腾讯云显示 0 调用但返回 121，请检查是否开启了 'WebServiceAPI' 权限，或 Key 是否有 IP 白名单限制。")
    except Exception as e:
        print(f"请求腾讯地图 API 发生异常: {e}")

    return f"位置_{round(lat, 2)}_{round(lon, 2)}"
    # 注意：这些接口在国内依然可能不稳定，但我们可以尝试一个更友好的返回
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
    headers = {'User-Agent': 'c-sorting-app-v1'}
    try:
        # 尝试增加超时时间并使用 headers 伪装
        resp = requests.get(url, headers=headers, timeout=10).json()
        addr = resp.get('address', {})
        # 优先获取城市、城镇或区
        city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('county')
        if city:
            return city
    except:
        pass

    # --- 方案 C: 备用逻辑 ---
    return f"位置_{round(lat, 2)}_{round(lon, 2)}"

# 原有的 geopy 逻辑由于网络原因暂时弃用
# from geopy.geocoders import Nominatim
# ...
