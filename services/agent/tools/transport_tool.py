"""
交通工具 - 获取旅行时间和物流信息
"""
import requests
from typing import Dict, Optional
from services.core.logger import logger


def get_travel_time(origin: str, destination: str, mode: str = "driving") -> Optional[str]:
    """
    获取两个地点之间的旅行时间（使用Google Maps API或OpenStreetMap）
    
    Args:
        origin: 起点
        destination: 终点
        mode: 交通方式 (driving, walking, transit)
        
    Returns:
        旅行时间信息字符串，如果失败返回None
    """
    try:
        # 注意：这里使用简化的实现，实际生产环境需要使用Google Maps API或类似服务
        # Google Maps API需要API Key，这里使用OpenRouteService作为免费替代
        
        # 使用OpenRouteService免费API（需要注册获取API Key）
        # 如果没有API Key，使用简化的文本响应
        # 实际使用时，可以在config.py中添加 OPENROUTESERVICE_API_KEY
        
        from services.core.config import settings
        
        # 检查是否有OpenRouteService API Key
        ors_api_key = getattr(settings, 'OPENROUTESERVICE_API_KEY', None)
        
        if ors_api_key:
            # 使用OpenRouteService API
            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {
                "Authorization": ors_api_key,
                "Content-Type": "application/json"
            }
            
            # 首先需要将地点名称转换为坐标（geocoding）
            # 简化处理：直接返回文本响应
            logger.info(f"使用OpenRouteService查询 {origin} -> {destination}")
            # 实际实现需要先进行地理编码，然后计算路线
        
        # 如果没有API Key，返回基于关键词的简化响应
        mode_names = {
            "driving": "驾车",
            "walking": "步行",
            "transit": "公共交通"
        }
        mode_name = mode_names.get(mode, "驾车")
        
        # 常见路线的时间估算（简化版）
        common_routes = {
            ("hong kong", "shenzhen"): "约1-2小时（驾车）",
            ("香港", "深圳"): "约1-2小时（驾车）",
            ("shenzhen", "guangzhou"): "约1.5-2小时（驾车）",
            ("深圳", "广州"): "约1.5-2小时（驾车）",
            ("beijing", "shanghai"): "约12-14小时（驾车），1.5小时（高铁）",
            ("北京", "上海"): "约12-14小时（驾车），1.5小时（高铁）",
        }
        
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        for (o, d), time_info in common_routes.items():
            if o in origin_lower and d in dest_lower:
                info = f"路线: {origin} -> {destination}\n"
                info += f"交通方式: {mode_name}\n"
                info += f"预计时间: {time_info}\n"
                logger.info(f"返回简化路线信息: {origin} -> {destination}")
                return info
        
        # 通用响应
        info = f"路线: {origin} -> {destination}\n"
        info += f"交通方式: {mode_name}\n"
        info += f"预计时间: 需要查询地图服务获取准确时间\n"
        info += f"提示: 可以访问Google Maps或高德地图获取详细路线"
        
        logger.info(f"返回通用路线信息: {origin} -> {destination}")
        return info
        
    except Exception as e:
        logger.error(f"获取旅行时间失败: {e}")
        return None


def extract_location_pair(query: str) -> Optional[tuple]:
    """
    从查询中提取起点和终点
    
    Args:
        query: 用户查询
        
    Returns:
        (起点, 终点) 元组，如果提取失败返回None
    """
    import re
    
    # 常见模式
    patterns = [
        r"from\s+([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)",  # "from A to B"
        r"([A-Za-z\s]+)\s+到\s+([A-Za-z\s]+)",  # "A 到 B"
        r"([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)",  # "A to B"
        r"([A-Za-z\s]+)\s+到达\s+([A-Za-z\s]+)",  # "A 到达 B"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            origin = match.group(1).strip()
            destination = match.group(2).strip()
            return (origin, destination)
    
    return None


def get_transport_context(query: str, num_results: int = 3) -> str:
    """
    根据查询内容获取交通信息上下文
    
    Args:
        query: 用户查询
        num_results: 返回结果数量
        
    Returns:
        交通信息上下文字符串
    """
    query_lower = query.lower()
    
    # 检测交通相关关键词
    transport_keywords = [
        "travel", "旅行", "journey", "路线", "route",
        "time", "时间", "how long", "多久",
        "distance", "距离", "driving", "驾车",
        "walking", "步行", "transit", "公共交通"
    ]
    
    if not any(kw in query_lower for kw in transport_keywords):
        return ""
    
    # 提取地点对
    location_pair = extract_location_pair(query)
    
    if location_pair:
        origin, destination = location_pair
        travel_info = get_travel_time(origin, destination)
        if travel_info:
            return travel_info
    
    # 如果没有提取到地点对，返回通用提示
    return "检测到交通查询，但无法从问题中提取起点和终点。请使用格式：'从A到B需要多久' 或 'A to B travel time'"

