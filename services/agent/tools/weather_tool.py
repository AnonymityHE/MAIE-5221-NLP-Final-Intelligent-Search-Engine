"""
天气查询工具 - 使用免费的天气API
"""
import requests
from typing import Dict, Optional
import re


def get_weather(location: str) -> Dict:
    """
    获取天气信息（使用OpenWeatherMap免费API，或wttr.in）
    
    Args:
        location: 地点名称（如"Hong Kong", "Shenzhen"）
        
    Returns:
        天气信息字典
    """
    try:
        # 使用wttr.in（免费，无需API key，适合快速测试）
        # 格式：wttr.in/{location}?format=j1 返回JSON
        location_clean = re.sub(r'[^\w\s-]', '', location).strip()
        url = f"http://wttr.in/{location_clean}?format=j1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 提取当前天气信息
        current = data.get("current_condition", [{}])[0]
        weather_info = {
            "location": location,
            "temperature": current.get("temp_C", "N/A"),
            "feels_like": current.get("FeelsLikeC", "N/A"),
            "condition": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
            "humidity": current.get("humidity", "N/A"),
            "wind_speed": current.get("windspeedKmph", "N/A"),
            "wind_direction": current.get("winddir16Point", "N/A")
        }
        
        return {
            "success": True,
            "weather": weather_info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "weather": {}
        }


def get_weather_context(location: str) -> str:
    """
    获取天气信息的文本描述
    
    Args:
        location: 地点名称
        
    Returns:
        格式化的天气信息文本
    """
    weather_result = get_weather(location)
    
    if not weather_result["success"]:
        return ""
    
    w = weather_result["weather"]
    context = (
        f"{w.get('location', location)}的天气情况：\n"
        f"- 温度: {w.get('temperature', 'N/A')}°C (体感 {w.get('feels_like', 'N/A')}°C)\n"
        f"- 天气状况: {w.get('condition', 'N/A')}\n"
        f"- 湿度: {w.get('humidity', 'N/A')}%\n"
        f"- 风速: {w.get('wind_speed', 'N/A')} km/h, 风向: {w.get('wind_direction', 'N/A')}"
    )
    
    return context

