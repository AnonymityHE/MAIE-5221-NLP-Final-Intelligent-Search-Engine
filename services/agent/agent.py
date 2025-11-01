"""
智能Agent - 根据问题类型自动选择和使用合适的工具
支持：本地RAG、网页搜索、天气、金融、交通查询
新增：动态工作流支持（多步骤查询）
"""
from typing import Dict, List, Optional
from services.llm.unified_client import unified_llm_client
from services.agent.tools.local_rag_tool import get_local_knowledge_context
from services.agent.tools.web_search_tool import get_web_search_context
from services.agent.tools.weather_tool import get_weather_context
from services.agent.tools.finance_tool import get_finance_context
from services.agent.tools.transport_tool import get_transport_context
from services.agent.workflow import WorkflowEngine, get_workflow_engine
from services.core.logger import logger
import re

# 尝试导入LangGraph版本（如果可用）
try:
    from services.agent.workflow_langgraph import (
        LangGraphWorkflowEngine, 
        get_langgraph_workflow_engine, 
        LANGGRAPH_AVAILABLE as LG_AVAILABLE
    )
    LANGGRAPH_AVAILABLE = LG_AVAILABLE
    get_langgraph_workflow_engine = get_langgraph_workflow_engine
except ImportError:
    LANGGRAPH_AVAILABLE = False
    LangGraphWorkflowEngine = None
    get_langgraph_workflow_engine = None


class RAGAgent:
    """RAG Agent - 根据问题类型智能选择工具（支持多种工具）"""
    
    def __init__(self):
        self.tools = {
            "local_rag": get_local_knowledge_context,
            "web_search": get_web_search_context,
            "weather": get_weather_context,
            "finance": get_finance_context,
            "transport": get_transport_context
        }
        # 初始化工作流引擎（优先使用LangGraph，如果可用）
        if LANGGRAPH_AVAILABLE:
            try:
                self.workflow_engine = get_langgraph_workflow_engine(self.tools)
                logger.info("使用LangGraph工作流引擎")
            except Exception as e:
                logger.warning(f"LangGraph工作流引擎初始化失败，使用自定义引擎: {e}")
                self.workflow_engine = get_workflow_engine(self.tools)
        else:
            self.workflow_engine = get_workflow_engine(self.tools)
            logger.info("使用自定义工作流引擎（LangGraph未安装）")
    
    def detect_question_type(self, query: str) -> List[str]:
        """
        检测问题类型，返回应该使用的工具列表（按优先级排序）
        
        Args:
            query: 用户问题
            
        Returns:
            工具名称列表
        """
        query_lower = query.lower()
        tools = []
        
        # 检测金融查询
        if any(kw in query_lower for kw in ["stock", "股票", "price", "股价", "crypto", "加密货币", "bitcoin", "btc", "ethereum", "eth"]):
            tools.append("finance")
        
        # 检测交通查询
        if any(kw in query_lower for kw in ["travel", "旅行", "route", "路线", "time", "时间", "how long", "多久", "distance", "距离"]):
            tools.append("transport")
        
        # 检测天气查询
        if any(kw in query_lower for kw in ["weather", "天气", "rain", "下雨", "temperature", "温度", "forecast", "预报", "cloud", "云"]):
            tools.append("weather")
        
        # 检测实时/新闻查询（需要网页搜索）
        if any(kw in query_lower for kw in ["latest", "最新", "news", "新闻", "current", "现在", "today", "今天", "recent", "最近", "recently"]):
            tools.append("web_search")
        
        # 默认使用本地RAG（如果还没有工具）
        if not tools:
            tools.append("local_rag")
        else:
            # 如果已经有其他工具，将local_rag作为备选
            tools.append("local_rag")
        
        return tools
    
    def extract_location(self, query: str) -> Optional[str]:
        """从查询中提取地点信息"""
        query_lower = query.lower()
        
        # 常见地点映射
        common_locations = {
            "hong kong": "Hong Kong",
            "香港": "Hong Kong",
            "beijing": "Beijing",
            "北京": "Beijing",
            "shanghai": "Shanghai",
            "上海": "Shanghai",
            "taipei": "Taipei",
            "台北": "Taipei",
            "tokyo": "Tokyo",
            "东京": "Tokyo",
            "new york": "New York",
            "london": "London",
            "london": "London"
        }
        
        for key, value in common_locations.items():
            if key in query_lower:
                return value
        
        return None
    
    def execute(self, query: str, model: Optional[str] = None) -> Dict:
        """
        执行Agent推理，选择合适的工具并获取答案
        支持动态工作流（多步骤查询）
        
        Args:
            query: 用户问题
            model: 可选的模型名称
            
        Returns:
            包含答案、使用的工具和上下文的字典
        """
        # 0. 检测是否需要工作流（多步骤查询）
        workflow_type = self.workflow_engine.detect_workflow_type(query)
        if workflow_type:
            logger.info(f"检测到需要工作流处理: {workflow_type}")
            return self._execute_workflow(query, model, workflow_type)
        
        # 1. 检测问题类型，决定使用哪些工具（原有逻辑）
        tools_to_use = self.detect_question_type(query)
        
        # 2. 按优先级收集上下文
        contexts = []
        tools_used = []
        
        # 对于特定类型的问题，只使用对应的工具（不fallback）
        query_lower = query.lower()
        is_weather_query = any(kw in query_lower for kw in ["weather", "天气", "rain", "下雨", "temperature", "温度", "forecast", "预报"])
        is_finance_query = any(kw in query_lower for kw in ["stock", "股票", "price", "股价", "crypto", "加密货币", "bitcoin", "btc"])
        is_transport_query = any(kw in query_lower for kw in ["travel", "旅行", "route", "路线", "time", "时间", "how long", "多久"])
        is_realtime_query = any(kw in query_lower for kw in ["latest", "最新", "news", "新闻", "current", "现在", "today", "今天", "recent", "最近"])
        
        for tool_name in tools_to_use:
            context = ""
            
            if tool_name == "finance":
                context = self.tools["finance"](query, num_results=3)
                if context:
                    contexts.append(f"[金融信息]\n{context}")
                    tools_used.append("finance")
                    logger.info("使用金融工具获取信息")
                    if is_finance_query:
                        break
            
            elif tool_name == "transport":
                context = self.tools["transport"](query, num_results=3)
                if context:
                    contexts.append(f"[交通信息]\n{context}")
                    tools_used.append("transport")
                    logger.info("使用交通工具获取信息")
                    if is_transport_query:
                        break
            
            elif tool_name == "weather":
                location = self.extract_location(query) or "Hong Kong"
                context = self.tools["weather"](location)
                if context:
                    contexts.append(f"[天气信息]\n{context}")
                    tools_used.append("weather")
                    logger.info(f"使用天气工具获取 {location} 的天气信息")
                    # 天气查询是确定的，找到就停止
                    if is_weather_query:
                        break
            
            elif tool_name == "web_search":
                context = self.tools["web_search"](query, num_results=3)
                if context:
                    contexts.append(f"[网络搜索结果]\n{context}")
                    tools_used.append("web_search")
                    logger.info("使用网页搜索工具获取信息")
                    # 对于实时信息查询，如果网页搜索有结果就使用
                    if is_realtime_query:
                        break
                else:
                    # 即使没有搜索结果，也标记尝试了web_search
                    # 对于实时查询，如果没有搜索到结果，应该直接使用LLM回答（因为它可能知道）
                    if is_realtime_query:
                        tools_used.append("web_search_attempted")
                        logger.info("网页搜索无结果，但对实时查询将使用LLM回答")
                        # 对于实时查询，即使搜索无结果，也直接使用LLM（不尝试local_rag）
                        break
            
            elif tool_name == "local_rag":
                context = self.tools["local_rag"](query)
                if context:
                    contexts.append(f"[本地知识库]\n{context}")
                    tools_used.append("local_rag")
                    logger.info("使用本地RAG工具获取信息")
                    # 如果是确定的知识库查询，有结果就使用
                    if not is_weather_query and not is_realtime_query and not is_finance_query and not is_transport_query:
                        break
            
            # 如果已经收集到相关上下文，停止搜索
            if contexts and (is_weather_query or is_finance_query or is_transport_query or (is_realtime_query and "web_search" in tools_used)):
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
    
    def _execute_workflow(self, query: str, model: Optional[str], workflow_type: str) -> Dict:
        """
        执行工作流（多步骤查询）
        
        Args:
            query: 用户问题
            model: 可选的模型名称
            workflow_type: 工作流类型
            
        Returns:
            包含答案、使用的工具和上下文的字典
        """
        # 1. 检查工作流引擎类型并执行
        if isinstance(self.workflow_engine, LangGraphWorkflowEngine):
            # 使用LangGraph工作流
            workflow_state = self.workflow_engine.execute_workflow(query, workflow_type)
            workflow_context = self.workflow_engine.synthesize_workflow_results(workflow_state)
            tools_used = [f"workflow:{step}" for step in workflow_state.get("steps_completed", [])]
            steps_completed = len(workflow_state.get("steps_completed", []))
        else:
            # 使用自定义工作流
            workflow_steps = self.workflow_engine.build_workflow(query, workflow_type)
            
            if not workflow_steps:
                logger.warning("工作流构建失败，回退到普通工具调用")
                return self._execute_normal(query, model)
            
            # 执行工作流
            workflow_state = self.workflow_engine.execute_workflow(query, workflow_steps)
            
            # 综合工作流结果
            workflow_context = self.workflow_engine.synthesize_workflow_results(workflow_state)
            
            # 构建工具使用列表
            tools_used = [f"workflow:{step.name}" for step in workflow_state.steps if step.status.value == "completed"]
            steps_completed = sum(1 for s in workflow_state.steps if s.status.value == "completed")
        
        # 4. 构建Prompt并调用LLM生成最终答案
        
        if workflow_context:
            system_prompt = (
                "你是一个专业的AI助手。用户提出了一个复杂的问题，我已经通过多个步骤收集了相关信息。"
                "请基于以下工作流执行结果，综合分析并回答用户的问题。"
            )
            user_prompt = f"原始问题：{query}\n\n工作流执行结果：\n\n{workflow_context}\n\n请基于以上信息综合回答原始问题。"
            logger.info("使用工作流结果构建Prompt")
        else:
            # 工作流执行失败，回退到普通LLM回答
            system_prompt = "你是一个专业的AI助手，请直接回答问题。"
            user_prompt = query
            tools_used = ["workflow_failed"]
        
        # 5. 调用LLM生成答案
        llm_result = unified_llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2048,
            temperature=0.7,
            model=model,
            provider="hkgai"
        )
        
        answer = llm_result.get("content", "无法生成答案")
        if "error" in llm_result:
            logger.error(f"工作流模式下LLM调用失败: {llm_result['error']}")
            answer = f"工作流执行完成，但LLM生成答案失败: {llm_result['error']}"
        
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
            "contexts_count": steps_completed if isinstance(self.workflow_engine, LangGraphWorkflowEngine) else len(workflow_state.steps),
            "has_context": len(workflow_context) > 0,
            "tokens": tokens_info,
            "model": llm_result.get("model"),
            "workflow_type": workflow_type,
            "workflow_steps_completed": steps_completed
        }
    
    def _execute_normal(self, query: str, model: Optional[str]) -> Dict:
        """普通执行（原有的execute逻辑，用于非工作流查询）"""
        # 这个方法是为了避免循环调用，但实际上应该使用execute方法
        # 这里直接调用execute的逻辑（但不检测工作流）
        tools_to_use = self.detect_question_type(query)
        
        # 按优先级收集上下文
        contexts = []
        tools_used = []
        
        query_lower = query.lower()
        is_weather_query = any(kw in query_lower for kw in ["weather", "天气", "rain", "下雨", "temperature", "温度", "forecast", "预报"])
        is_finance_query = any(kw in query_lower for kw in ["stock", "股票", "price", "股价", "crypto", "加密货币", "bitcoin", "btc"])
        is_transport_query = any(kw in query_lower for kw in ["travel", "旅行", "route", "路线", "time", "时间", "how long", "多久"])
        is_realtime_query = any(kw in query_lower for kw in ["latest", "最新", "news", "新闻", "current", "现在", "today", "今天", "recent", "最近"])
        
        for tool_name in tools_to_use:
            context = ""
            
            if tool_name == "finance":
                context = self.tools["finance"](query, num_results=3)
                if context:
                    contexts.append(f"[金融信息]\n{context}")
                    tools_used.append("finance")
                    if is_finance_query:
                        break
            
            elif tool_name == "transport":
                context = self.tools["transport"](query, num_results=3)
                if context:
                    contexts.append(f"[交通信息]\n{context}")
                    tools_used.append("transport")
                    if is_transport_query:
                        break
            
            elif tool_name == "weather":
                location = self.extract_location(query) or "Hong Kong"
                context = self.tools["weather"](location)
                if context:
                    contexts.append(f"[天气信息]\n{context}")
                    tools_used.append("weather")
                    if is_weather_query:
                        break
            
            elif tool_name == "web_search":
                context = self.tools["web_search"](query, num_results=3)
                if context:
                    contexts.append(f"[网络搜索结果]\n{context}")
                    tools_used.append("web_search")
                    if is_realtime_query:
                        break
                else:
                    if is_realtime_query:
                        tools_used.append("web_search_attempted")
                        break
            
            elif tool_name == "local_rag":
                context = self.tools["local_rag"](query)
                if context:
                    contexts.append(f"[本地知识库]\n{context}")
                    tools_used.append("local_rag")
                    if not is_weather_query and not is_realtime_query and not is_finance_query and not is_transport_query:
                        break
            
            if contexts and (is_weather_query or is_finance_query or is_transport_query or (is_realtime_query and "web_search" in tools_used)):
                break
        
        # 构建Prompt并调用LLM
        if contexts:
            all_context = "\n\n".join(contexts)
            system_prompt = (
                "你是一个智能AI助手。请基于提供的上下文信息回答问题。"
                "如果上下文中包含相关信息，请优先使用这些信息。"
            )
            user_prompt = f"上下文信息：\n\n{all_context}\n\n问题：{query}\n\n请基于上下文回答上述问题。"
        elif "web_search_attempted" in tools_used:
            system_prompt = (
                "你是一个专业的AI助手。用户询问的是实时信息或最新新闻。"
                "虽然网页搜索没有返回结果，但请基于你的知识尽可能回答问题。"
            )
            user_prompt = query
            tools_used = ["web_search_attempted", "direct_llm"]
        else:
            system_prompt = "你是一个专业的AI助手，请直接回答问题。"
            user_prompt = query
            if not tools_used:
                tools_used = ["direct_llm"]
        
        # 调用LLM
        llm_result = unified_llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2048,
            temperature=0.7,
            model=model,
            provider="hkgai"
        )
        
        answer = llm_result.get("content", "无法生成答案")
        
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
