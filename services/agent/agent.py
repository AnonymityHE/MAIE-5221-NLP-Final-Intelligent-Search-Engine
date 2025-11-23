"""
智能Agent - 根据问题类型自动选择和使用合适的工具
支持：本地RAG、网页搜索、天气、金融、交通查询
新增：动态工作流支持（多步骤查询）
- LLM驱动的智能工作流规划（优先）
- 基于规则的工作流模板（Fallback）
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

# 导入LLM驱动的工作流模块
try:
    from services.agent.workflow_llm_planner import get_llm_workflow_planner
    from services.agent.workflow_dynamic import get_dynamic_workflow_engine
    LLM_WORKFLOW_AVAILABLE = True
except ImportError:
    logger.warning("LLM工作流模块导入失败，将使用基于规则的工作流")
    LLM_WORKFLOW_AVAILABLE = False
    get_llm_workflow_planner = None
    get_dynamic_workflow_engine = None


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
        
        # 初始化LLM驱动的工作流系统（优先）
        self.llm_planner = None
        self.dynamic_engine = None
        if LLM_WORKFLOW_AVAILABLE:
            try:
                tool_names = list(self.tools.keys())
                self.llm_planner = get_llm_workflow_planner(tool_names)
                self.dynamic_engine = get_dynamic_workflow_engine(self.tools)
                logger.info("✨ 使用LLM驱动的智能工作流系统")
            except Exception as e:
                logger.warning(f"LLM工作流系统初始化失败: {e}")
                self.llm_planner = None
                self.dynamic_engine = None
        
        # 初始化基于规则的工作流引擎（作为fallback）
        if LANGGRAPH_AVAILABLE:
            try:
                self.workflow_engine = get_langgraph_workflow_engine(self.tools)
                logger.info("📋 LangGraph工作流引擎已就绪（作为fallback）")
            except Exception as e:
                logger.warning(f"LangGraph工作流引擎初始化失败，使用自定义引擎: {e}")
                self.workflow_engine = get_workflow_engine(self.tools)
        else:
            self.workflow_engine = get_workflow_engine(self.tools)
            logger.info("📋 自定义工作流引擎已就绪（作为fallback）")
    
    def detect_question_type(self, query: str) -> List[str]:
        """
        检测问题类型，返回应该使用的工具列表（按优先级排序）
        
        Args:
            query: 用户问题
            
        Returns:
            工具名称列表（如果返回空列表，表示直接调用LLM不使用任何工具）
        """
        query_lower = query.lower()
        tools = []
        
        # 🌐 翻译/语言学习问题 - 直接用LLM，不需要任何工具
        translation_keywords = [
            "怎么说", "怎么读", "发音", "翻译", "用粤语", "用普通话", "用英文",
            "how to say", "how do you say", "pronounce", "pronunciation", 
            "translation", "translate", "in cantonese", "in english", "in chinese"
        ]
        if any(keyword in query_lower for keyword in translation_keywords):
            logger.info("🌐 检测到翻译/语言学习问题，直接调用LLM（不使用RAG）")
            return []  # 空列表表示不使用任何工具
        
        # 检测历史时间关键词（昨天、上周、上月等）
        # 历史查询通常需要web_search，因为实时工具可能不支持历史数据
        historical_keywords = ["yesterday", "昨天", "last week", "上周", "last month", "上月", "past", "过去", "以前", "之前"]
        is_historical_query = any(kw in query_lower for kw in historical_keywords)
        
        # 检测金融查询
        if any(kw in query_lower for kw in ["stock", "股票", "price", "股价", "crypto", "加密货币", "bitcoin", "btc", "ethereum", "eth"]):
            tools.append("finance")
        
        # 检测交通查询
        if any(kw in query_lower for kw in ["travel", "旅行", "route", "路线", "time", "时间", "how long", "多久", "distance", "距离"]):
            tools.append("transport")
        
        # 检测天气查询
        # 注意：如果是历史天气查询，应该使用web_search而不是weather工具
        if any(kw in query_lower for kw in ["weather", "天气", "rain", "下雨", "temperature", "温度", "forecast", "预报", "cloud", "云", "怎麼樣", "怎么样"]):
            if is_historical_query:
                # 历史天气查询：使用web_search（weather工具只支持当前天气）
                tools.append("web_search")
                logger.info("检测到历史天气查询，使用web_search工具")
            else:
                # 当前天气查询：使用weather工具
                tools.append("weather")
        
        # 检测实时/新闻查询（需要网页搜索）
        # 注意：如果已经有weather/finance/transport工具且不是历史查询，不要添加web_search
        if not tools and any(kw in query_lower for kw in ["latest", "最新", "news", "新闻", "current", "现在", "today", "今天", "recent", "最近", "recently"]):
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
        
        工作流执行优先级：
        1. LLM驱动的智能工作流（优先）
        2. 基于规则的工作流模板（fallback）
        3. 单工具直接调用（简单查询）
        
        Args:
            query: 用户问题
            model: 可选的模型名称
            
        Returns:
            包含答案、使用的工具和上下文的字典
        """
        # 0. 尝试LLM驱动的工作流规划（优先）
        if self.llm_planner and self.dynamic_engine:
            try:
                logger.info("🧠 尝试LLM驱动的工作流规划...")
                plan = self.llm_planner.analyze_query(query)
                
                # 检查是否需要工作流且置信度足够
                if plan.requires_workflow and plan.confidence >= 0.4:
                    logger.info(f"✅ LLM规划成功 (置信度: {plan.confidence:.2f}), 使用动态工作流")
                    return self._execute_llm_workflow(query, model, plan)
                else:
                    logger.info(f"ℹ️  LLM认为不需要工作流 (置信度: {plan.confidence:.2f}), 尝试规则引擎")
            except Exception as e:
                logger.warning(f"⚠️  LLM工作流规划失败: {e}, 回退到规则引擎")
        
        # 1. 回退到基于规则的工作流检测
        workflow_type = self.workflow_engine.detect_workflow_type(query)
        if workflow_type:
            logger.info(f"📋 规则引擎检测到工作流: {workflow_type}")
            return self._execute_rule_based_workflow(query, model, workflow_type)
        
        # 1. 检测问题类型，决定使用哪些工具（原有逻辑）
        tools_to_use = self.detect_question_type(query)
        
        # 如果返回空列表，表示直接调用LLM（如翻译问题）
        if not tools_to_use:
            logger.info("⚡ 直接调用LLM，不使用任何工具")
            llm_result = unified_llm_client.chat(
                system_prompt="你是一个专业的AI助手，擅长语言翻译和教学。请直接、简洁地回答用户的问题。",
                user_prompt=query,
                max_tokens=2048,
                temperature=0.7,
                model=model,
                provider="hkgai"
            )
            
            answer = llm_result.get("content", "无法生成答案")
            if "error" in llm_result:
                logger.error(f"❌ LLM调用失败: {llm_result['error']}")
                answer = f"抱歉，我无法回答这个问题。"
            
            tokens_info = None
            if "input_tokens" in llm_result:
                tokens_info = {
                    "input": llm_result.get("input_tokens", 0),
                    "output": llm_result.get("output_tokens", 0),
                    "total": llm_result.get("total_tokens", 0)
                }
            
            return {
                "answer": answer,
                "tools_used": ["direct_llm"],
                "contexts_count": 0,
                "has_context": False,
                "tokens": tokens_info,
                "model": llm_result.get("model")
            }
        
        # 2. 按优先级收集上下文
        contexts = []
        tools_used = []
        
        # 对于特定类型的问题，只使用对应的工具（不fallback）
        query_lower = query.lower()
        
        # 检测历史时间关键词
        historical_keywords = ["yesterday", "昨天", "last week", "上周", "last month", "上月", "past", "过去", "以前", "之前"]
        is_historical_query = any(kw in query_lower for kw in historical_keywords)
        
        is_weather_query = any(kw in query_lower for kw in ["weather", "天气", "rain", "下雨", "temperature", "温度", "forecast", "预报", "怎麼樣", "怎么样"])
        is_finance_query = any(kw in query_lower for kw in ["stock", "股票", "price", "股价", "crypto", "加密货币", "bitcoin", "btc"])
        is_transport_query = any(kw in query_lower for kw in ["travel", "旅行", "route", "路线", "time", "时间", "how long", "多久"])
        
        # 实时查询：只有在没有特定工具（weather/finance/transport）时才使用web_search
        # 但是历史天气查询应该使用web_search，所以需要特殊处理
        is_realtime_query = not (is_weather_query or is_finance_query or is_transport_query) and any(kw in query_lower for kw in ["latest", "最新", "news", "新闻", "current", "现在", "today", "今天", "recent", "最近"])
        
        # 如果天气查询是历史查询，应该使用web_search而不是weather工具
        if is_weather_query and is_historical_query:
            logger.info("检测到历史天气查询，优先使用web_search工具")
        
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
                # 如果是历史天气查询，跳过weather工具，应该使用web_search
                if is_historical_query:
                    logger.info("历史天气查询跳过weather工具，将使用web_search")
                    continue
                
                location = self.extract_location(query) or "Hong Kong"
                context = self.tools["weather"](location)
                if context:
                    contexts.append(f"[天气信息]\n{context}")
                    tools_used.append("weather")
                    logger.info(f"使用天气工具获取 {location} 的天气信息")
                    # 天气查询是确定的，找到就停止
                    if is_weather_query:
                        break
                else:
                    # 如果weather工具失败，对于历史查询应该fallback到web_search
                    if is_historical_query:
                        logger.info("weather工具失败，历史天气查询fallback到web_search")
                        # 不break，继续尝试web_search
                        continue
            
            elif tool_name == "web_search":
                context = self.tools["web_search"](query, num_results=3)
                if context:
                    contexts.append(f"[网络搜索结果]\n{context}")
                    tools_used.append("web_search")
                    logger.info("使用网页搜索工具获取信息")
                    # 对于实时信息查询或历史天气查询，如果网页搜索有结果就使用
                    if is_realtime_query or (is_weather_query and is_historical_query):
                        break
                else:
                    # 即使没有搜索结果，也标记尝试了web_search
                    # 对于实时查询或历史天气查询，如果没有搜索到结果，应该直接使用LLM回答
                    if is_realtime_query or (is_weather_query and is_historical_query):
                        tools_used.append("web_search_attempted")
                        logger.info("网页搜索无结果，但对实时查询/历史天气查询将使用LLM回答")
                        # 对于实时查询或历史天气查询，即使搜索无结果，也直接使用LLM（不尝试local_rag）
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
            # 尝试了网页搜索但没有结果，对于实时查询或历史天气查询直接用LLM回答
            if is_weather_query and is_historical_query:
                system_prompt = (
                    "你是一个专业的AI助手。用户询问的是历史天气信息。"
                    "虽然网页搜索没有返回结果，但请基于你的知识尽可能回答问题。"
                    "如果无法提供准确的历史天气数据，请诚实说明。"
                )
            else:
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
        logger.info(f"🤖 准备调用LLM（HKGAI），查询: '{query[:50]}...'")
        llm_result = unified_llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2048,
            temperature=0.7,
            model=model,  # 如果指定了Gemini模型，会自动使用Gemini
            provider="hkgai"  # Agent默认使用HKGAI
        )
        
        if "error" in llm_result:
            logger.error(f"❌ LLM调用失败: {llm_result['error']}")
            answer = f"LLM调用失败: {llm_result['error']}"
        else:
            answer = llm_result.get("content", "无法生成答案")
            logger.info(f"✅ LLM返回答案，长度: {len(answer)} 字符")
            logger.debug(f"答案预览: {answer[:100]}...")
        
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
    
    def _execute_llm_workflow(self, query: str, model: Optional[str], plan) -> Dict:
        """
        执行LLM驱动的动态工作流
        
        Args:
            query: 用户问题
            model: 可选的模型名称
            plan: LLM生成的工作流计划
            
        Returns:
            包含答案、使用的工具和上下文的字典
        """
        logger.info(f"🚀 开始执行LLM驱动的工作流: {plan.workflow_type}")
        
        # 1. 使用动态执行引擎执行计划
        execution_context = self.dynamic_engine.execute(plan, query)
        
        # 2. 综合执行结果
        workflow_context = self.dynamic_engine.synthesize_results(execution_context)
        
        # 3. 获取工具使用摘要
        tools_used = self.dynamic_engine.get_tool_usage_summary(execution_context)
        
        # 4. 构建Prompt并调用LLM生成最终答案
        if workflow_context:
            # 检测是否是翻译/语言学习类问题
            is_translation_query = any(keyword in query for keyword in [
                "怎么说", "怎么读", "发音", "翻译", "用粤语", "用普通话", "用英文",
                "how to say", "pronounce", "translation", "in Cantonese", "in English"
            ])
            
            if is_translation_query:
                system_prompt = (
                    "你是一个专业的语言学习助手。用户想知道某个词或句子在另一种语言中怎么说。\n"
                    "请直接给出目标语言的说法，不要介绍系统功能或偏离主题。\n\n"
                    "**回答格式**：\n"
                    "1. 先直接给出目标语言的说法（如：粤语：唔该唔好靠近车门）\n"
                    "2. 如果知道，可以简单补充发音或用法说明\n\n"
                    "**注意**：如果检索到的上下文与翻译无关（如系统功能介绍），请忽略它们，专注于回答翻译问题。"
                )
            else:
                system_prompt = (
                    "你是一个专业的AI助手。我已经通过智能工作流系统执行了多个步骤来收集信息。"
                    "请基于以下工作流执行结果，综合分析并回答用户的问题。"
                    "注意：结果可能来自不同的数据源（网页搜索、金融API、天气API等），请整合这些信息给出全面的答案。"
                )
            
            user_prompt = f"原始问题：{query}\n\n{workflow_context}\n\n请基于以上信息综合回答原始问题。"
            logger.info("使用LLM工作流结果构建Prompt")
        else:
            # 工作流执行失败，回退到普通LLM回答
            system_prompt = "你是一个专业的AI助手，请直接回答问题。"
            user_prompt = query
            tools_used = ["llm_workflow_failed"]
            logger.warning("LLM工作流执行无结果，回退到直接回答")
        
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
            logger.error(f"LLM工作流模式下LLM调用失败: {llm_result['error']}")
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
            "contexts_count": len(execution_context.completed_steps),
            "has_context": len(workflow_context) > 0,
            "tokens": tokens_info,
            "model": llm_result.get("model"),
            "workflow_type": plan.workflow_type,
            "workflow_engine": "llm_driven",
            "workflow_confidence": plan.confidence,
            "workflow_steps_completed": len(execution_context.completed_steps)
        }
    
    def _execute_rule_based_workflow(self, query: str, model: Optional[str], workflow_type: str) -> Dict:
        """
        执行基于规则的工作流（原有逻辑，作为fallback）
        
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
            "workflow_engine": "rule_based",  # 标记为基于规则的工作流
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
