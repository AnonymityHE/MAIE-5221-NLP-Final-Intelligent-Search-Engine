"""
智能Agent - 根据问题类型自动选择和使用合适的工具
"""
from typing import Dict, List, Optional
from services.unified_llm_client import unified_llm_client
from services.tools.local_rag_tool import get_local_knowledge_context
from services.tools.web_search_tool import get_web_search_context
from services.tools.weather_tool import get_weather_context
import re


class RAGAgent:
    """简单的RAG Agent - 根据问题类型智能选择工具"""
    
    def __init__(self):
        self.tools = {
            "local_rag": get_local_knowledge_context,
            "web_search": get_web_search_context,
            "weather": get_weather_context
        }
    
    def detect_question_type(self, query: str) -> List[str]:
        """
        检测问题类型，返回应该使用的工具列表（按优先级排序）
        
        Args:
            query: 用户问题
            
        Returns:
            工具名称列表
        """
        query_lower = query.lower()
        tools_to_use = []
        
        # 检测天气相关
        weather_keywords = ["weather", "天气", "rain", "下雨", "temperature", "温度", "forecast", "预报"]
        if any(keyword in query_lower for keyword in weather_keywords):
            tools_to_use.append("weather")
        
        # 检测实时信息/新闻相关
        realtime_keywords = ["latest", "最新", "current", "当前", "today", "今天", "now", "现在", "recent", "最近"]
        web_search_keywords = ["news", "新闻", "search", "搜索", "find", "找到", "how to", "如何"]
        
        # 如果包含实时信息关键词，优先使用网页搜索
        if any(keyword in query_lower for keyword in (realtime_keywords + web_search_keywords)):
            tools_to_use.insert(0, "web_search")  # 插入到最前面，最高优先级
        
        # 只在没有特定查询类型时才添加本地知识库
        # 对于天气和实时查询，不自动添加local_rag（避免混淆）
        if not tools_to_use or "weather" not in tools_to_use:
            tools_to_use.append("local_rag")
        
        # 确保至少有一个工具
        if not tools_to_use:
            tools_to_use = ["web_search", "local_rag"]
        
        return list(dict.fromkeys(tools_to_use))  # 去重但保持顺序
    
    def extract_location(self, query: str) -> Optional[str]:
        """从问题中提取地点名称"""
        # 简单的地点提取（可以改进）
        location_patterns = [
            r"in\s+([A-Z][a-zA-Z\s]+)",  # "in Hong Kong"
            r"([A-Z][a-zA-Z]+)\s+的",     # "香港的"
            r"([A-Z][a-zA-Z]+)\s+weather", # "Hong Kong weather"
            r"rain\s+in\s+([A-Z][a-zA-Z]+)",  # "rain in Shenzhen"
            r"weather\s+in\s+([A-Z][a-zA-Z]+)",  # "weather in Beijing"
            r"([A-Z][a-zA-Z]+)\s+tomorrow",  # "Shenzhen tomorrow"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                loc = match.group(1).strip()
                # 过滤掉常见非地点单词
                if loc.lower() not in ["will", "it", "is", "the", "be", "what", "how"]:
                    return loc
        
        # 常见地点列表（更完整的列表）
        common_locations = {
            "hong kong": "Hong Kong",
            "香港": "Hong Kong",
            "shenzhen": "Shenzhen",
            "深圳": "Shenzhen",
            "beijing": "Beijing",
            "北京": "Beijing",
            "shanghai": "Shanghai",
            "上海": "Shanghai",
            "guangzhou": "Guangzhou",
            "广州": "Guangzhou",
            "shanghai": "Shanghai",
            "上海": "Shanghai",
            "macau": "Macau",
            "澳门": "Macau",
        }
        
        query_lower = query.lower()
        for key, value in common_locations.items():
            if key in query_lower:
                return value
        
        return None
    
    def execute(self, query: str, model: Optional[str] = None) -> Dict:
        """
        执行Agent推理，选择合适的工具并获取答案
        
        Args:
            query: 用户问题
            model: 可选的模型名称
            
        Returns:
            包含答案、使用的工具和上下文的字典
        """
        # 1. 检测问题类型，决定使用哪些工具
        tools_to_use = self.detect_question_type(query)
        
        # 2. 按优先级收集上下文
        contexts = []
        tools_used = []
        
        # 对于特定类型的问题，只使用对应的工具（不fallback）
        query_lower = query.lower()
        is_weather_query = any(kw in query_lower for kw in ["weather", "天气", "rain", "下雨", "temperature", "温度", "forecast", "预报"])
        is_realtime_query = any(kw in query_lower for kw in ["latest", "最新", "news", "新闻", "current", "现在", "today", "今天", "recent", "最近"])
        
        for tool_name in tools_to_use:
            context = ""
            
            if tool_name == "weather":
                location = self.extract_location(query) or "Hong Kong"
                context = self.tools["weather"](location)
                if context:
                    contexts.append(f"[天气信息]\n{context}")
                    tools_used.append("weather")
                    # 天气查询是确定的，找到就停止
                    if is_weather_query:
                        break
            
            elif tool_name == "web_search":
                context = self.tools["web_search"](query, num_results=3)
                if context:
                    contexts.append(f"[网络搜索结果]\n{context}")
                    tools_used.append("web_search")
                    # 对于实时信息查询，如果网页搜索有结果就使用
                    if is_realtime_query:
                        break
                else:
                    # 即使没有搜索结果，也标记尝试了web_search
                    # 对于实时查询，如果没有搜索到结果，应该直接使用LLM回答（因为它可能知道）
                    if is_realtime_query:
                        tools_used.append("web_search_attempted")
                        # 对于实时查询，即使搜索无结果，也直接使用LLM（不尝试local_rag）
                        break
            
            elif tool_name == "local_rag":
                context = self.tools["local_rag"](query)
                if context:
                    contexts.append(f"[本地知识库]\n{context}")
                    tools_used.append("local_rag")
                    # 如果是确定的知识库查询，有结果就使用
                    if not is_weather_query and not is_realtime_query:
                        break
            
            # 如果已经收集到相关上下文，停止搜索
            if contexts and (is_weather_query or (is_realtime_query and "web_search" in tools_used)):
                break
        
        # 3. 构建Prompt并调用LLM
        if contexts:
            # 有工具结果，使用增强回答
            all_context = "\n\n".join(contexts)
            system_prompt = (
                "你是一个智能AI助手。请基于提供的上下文信息回答问题。"
                "如果上下文中包含相关信息，请优先使用这些信息。"
            )
            user_prompt = f"上下文信息：\n\n{all_context}\n\n问题：{query}\n\n请基于上下文回答上述问题。"
        elif "web_search_attempted" in tools_used:
            # 尝试了网页搜索但没有结果，对于实时查询直接用LLM回答
            system_prompt = (
                "你是一个专业的AI助手。用户询问的是实时信息或最新新闻。"
                "虽然网页搜索没有返回结果，但请基于你的知识尽可能回答问题。"
            )
            user_prompt = query
            tools_used = ["web_search_attempted", "direct_llm"]
        else:
            # 没有工具结果，直接回答
            system_prompt = "你是一个专业的AI助手，请直接回答问题。"
            user_prompt = query
            if not tools_used:
                tools_used = ["direct_llm"]
        
        # 4. 调用LLM（使用统一客户端，默认使用HKGAI）
        llm_result = unified_llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2048,
            temperature=0.7,
            model=model,  # 如果指定了Gemini模型，会自动使用Gemini
            provider="hkgai"  # Agent默认使用HKGAI
        )
        
        answer = llm_result.get("content", "无法生成答案")
        
        # 提取token使用信息
        tokens_info = None
        if "input_tokens" in llm_result:
            tokens_info = {
                "input": llm_result.get("input_tokens", 0),
                "output": llm_result.get("output_tokens", 0),
                "total": llm_result.get("total_tokens", 0)
            }
        
        return {
            "answer": answer,
            "tools_used": tools_used,
            "contexts_count": len(contexts),
            "has_context": len(contexts) > 0,
            "tokens": tokens_info,
            "model": llm_result.get("model")
        }


# 全局Agent实例
agent = RAGAgent()

