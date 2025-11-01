"""
基于LangGraph的动态工作流引擎 - 支持多步骤查询和工具链执行

实现项目要求：Dynamic Workflow Automation
使用LangGraph实现状态机和工作流编排
示例："What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?"
需要：获取财报 → 获取NVIDIA股价 → 获取AMD股价 → 综合分析
"""
from typing import Dict, List, Optional, Any, Callable, TypedDict, Annotated
from services.core.logger import logger

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None


class WorkflowState(TypedDict):
    """工作流状态（LangGraph兼容）"""
    query: str  # 原始查询
    context: Dict[str, Any]  # 上下文数据
    steps_completed: List[str]  # 已完成的步骤
    current_step: Optional[str]  # 当前步骤
    final_answer: Optional[str]  # 最终答案
    error: Optional[str]  # 错误信息


class LangGraphWorkflowEngine:
    """基于LangGraph的动态工作流引擎"""
    
    def __init__(self, tools: Dict[str, Callable]):
        """
        初始化工作流引擎
        
        Args:
            tools: 工具字典，键为工具名称，值为工具函数
        """
        self.tools = tools
        self.graph = None
        
        if LANGGRAPH_AVAILABLE:
            self._build_graph()
        else:
            logger.warning("LangGraph不可用，请安装: pip install langgraph")
    
    def _build_graph(self):
        """构建LangGraph工作流图"""
        if not LANGGRAPH_AVAILABLE:
            return
        
        # 创建状态图
        workflow = StateGraph(WorkflowState)
        
        # 添加节点
        workflow.add_node("detect_workflow", self._detect_workflow_node)
        workflow.add_node("search_earnings", self._search_earnings_node)
        workflow.add_node("get_first_stock", self._get_first_stock_node)
        workflow.add_node("get_second_stock", self._get_second_stock_node)
        workflow.add_node("synthesize", self._synthesize_node)
        
        # 设置入口点
        workflow.set_entry_point("detect_workflow")
        
        # 添加条件边（根据工作流类型路由）
        workflow.add_conditional_edges(
            "detect_workflow",
            self._route_after_detect,
            {
                "finance_comparison": "search_earnings",
                "skip": END
            }
        )
        
        # 添加顺序边
        workflow.add_edge("search_earnings", "get_first_stock")
        workflow.add_edge("get_first_stock", "get_second_stock")
        workflow.add_edge("get_second_stock", "synthesize")
        workflow.add_edge("synthesize", END)
        
        # 编译图
        self.graph = workflow.compile()
        logger.info("LangGraph工作流图构建完成")
    
    def _detect_workflow_node(self, state: WorkflowState) -> WorkflowState:
        """检测工作流类型节点"""
        query = state["query"]
        query_lower = query.lower()
        
        # 检测金融对比查询
        finance_keywords = [
            "compare", "对比", "vs", "versus", "difference", "差异",
            "impact", "影响", "earnings", "财报", "stock price", "股价"
        ]
        
        if any(kw in query_lower for kw in finance_keywords):
            company_keywords = ["nvidia", "amd", "apple", "microsoft", "google", "tesla"]
            company_count = sum(1 for company in company_keywords if company in query_lower)
            
            if company_count >= 2 or ("compare" in query_lower and "stock" in query_lower):
                state["context"]["workflow_type"] = "finance_comparison"
                logger.info("检测到金融对比工作流")
            else:
                state["context"]["workflow_type"] = None
        else:
            state["context"]["workflow_type"] = None
        
        state["current_step"] = "detect_workflow"
        state["steps_completed"].append("detect_workflow")
        
        return state
    
    def _route_after_detect(self, state: WorkflowState) -> str:
        """根据检测结果路由"""
        workflow_type = state["context"].get("workflow_type")
        if workflow_type == "finance_comparison":
            return "finance_comparison"
        return "skip"
    
    def _search_earnings_node(self, state: WorkflowState) -> WorkflowState:
        """搜索财报节点"""
        query = state["query"]
        
        logger.info("执行步骤: 搜索财报信息")
        
        try:
            web_search_tool = self.tools.get("web_search")
            if web_search_tool:
                result = web_search_tool(query, num_results=3)
                state["context"]["earnings_search_result"] = result
                state["steps_completed"].append("search_earnings")
            else:
                state["error"] = "web_search工具不可用"
        except Exception as e:
            logger.error(f"搜索财报失败: {e}")
            state["error"] = str(e)
        
        state["current_step"] = "search_earnings"
        return state
    
    def _get_first_stock_node(self, state: WorkflowState) -> WorkflowState:
        """获取第一个公司股价节点"""
        query = state["query"]
        query_lower = query.lower()
        
        # 提取第一个公司名
        companies = ["nvidia", "amd", "apple", "microsoft", "google", "tesla", "amazon"]
        first_company = None
        for company in companies:
            if company in query_lower:
                first_company = company
                break
        
        if first_company:
            logger.info(f"执行步骤: 获取 {first_company} 股价")
            
            try:
                finance_tool = self.tools.get("finance")
                if finance_tool:
                    stock_query = f"{first_company} stock price"
                    result = finance_tool(stock_query, num_results=3)
                    state["context"]["first_stock_result"] = result
                    state["context"]["first_company"] = first_company
                    state["steps_completed"].append("get_first_stock")
                else:
                    state["error"] = "finance工具不可用"
            except Exception as e:
                logger.error(f"获取第一个股价失败: {e}")
                state["error"] = str(e)
        
        state["current_step"] = "get_first_stock"
        return state
    
    def _get_second_stock_node(self, state: WorkflowState) -> WorkflowState:
        """获取第二个公司股价节点"""
        query = state["query"]
        query_lower = query.lower()
        
        # 提取第二个公司名（排除第一个）
        companies = ["nvidia", "amd", "apple", "microsoft", "google", "tesla", "amazon"]
        first_company = state["context"].get("first_company", "").lower()
        found_companies = [c for c in companies if c in query_lower]
        
        # 移除第一个公司
        if first_company and first_company in found_companies:
            found_companies.remove(first_company)
        
        second_company = found_companies[0] if found_companies else None
        
        if second_company:
            logger.info(f"执行步骤: 获取 {second_company} 股价")
            
            try:
                finance_tool = self.tools.get("finance")
                if finance_tool:
                    stock_query = f"{second_company} stock price"
                    result = finance_tool(stock_query, num_results=3)
                    state["context"]["second_stock_result"] = result
                    state["context"]["second_company"] = second_company
                    state["steps_completed"].append("get_second_stock")
                else:
                    state["error"] = "finance工具不可用"
            except Exception as e:
                logger.error(f"获取第二个股价失败: {e}")
                state["error"] = str(e)
        
        state["current_step"] = "get_second_stock"
        return state
    
    def _synthesize_node(self, state: WorkflowState) -> WorkflowState:
        """综合分析节点"""
        logger.info("执行步骤: 综合分析结果")
        
        # 收集所有步骤的结果
        earnings_result = state["context"].get("earnings_search_result", "")
        first_stock = state["context"].get("first_stock_result", "")
        second_stock = state["context"].get("second_stock_result", "")
        
        # 构建综合上下文
        synthesis_context = f"""
财报搜索结果:
{earnings_result}

{state["context"].get("first_company", "").upper()}股价:
{first_stock}

{state["context"].get("second_company", "").upper()}股价:
{second_stock}
"""
        
        state["context"]["synthesis"] = synthesis_context
        state["steps_completed"].append("synthesize")
        state["current_step"] = "synthesize"
        
        return state
    
    def detect_workflow_type(self, query: str) -> Optional[str]:
        """检测工作流类型（保持向后兼容）"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        query_lower = query.lower()
        finance_keywords = [
            "compare", "对比", "vs", "versus", "difference", "差异",
            "impact", "影响", "earnings", "财报", "stock price", "股价"
        ]
        
        if any(kw in query_lower for kw in finance_keywords):
            company_keywords = ["nvidia", "amd", "apple", "microsoft", "google", "tesla"]
            company_count = sum(1 for company in company_keywords if company in query_lower)
            
            if company_count >= 2 or ("compare" in query_lower and "stock" in query_lower):
                return "finance_comparison"
        
        return None
    
    def execute_workflow(self, query: str, workflow_type: Optional[str] = None) -> WorkflowState:
        """
        执行工作流
        
        Args:
            query: 原始查询
            workflow_type: 工作流类型（可选，会自动检测）
            
        Returns:
            工作流执行状态
        """
        if not LANGGRAPH_AVAILABLE or not self.graph:
            logger.warning("LangGraph不可用，工作流执行失败")
            return WorkflowState(
                query=query,
                context={},
                steps_completed=[],
                current_step=None,
                final_answer=None,
                error="LangGraph未安装"
            )
        
        # 初始化状态
        initial_state: WorkflowState = {
            "query": query,
            "context": {},
            "steps_completed": [],
            "current_step": None,
            "final_answer": None,
            "error": None
        }
        
        # 执行图
        try:
            logger.info(f"开始执行LangGraph工作流: {query}")
            final_state = self.graph.invoke(initial_state)
            logger.info(f"工作流执行完成，完成步骤: {final_state['steps_completed']}")
            return final_state
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            initial_state["error"] = str(e)
            return initial_state
    
    def synthesize_workflow_results(self, state: WorkflowState) -> str:
        """综合工作流结果，生成最终上下文"""
        synthesis = state.get("context", {}).get("synthesis", "")
        
        if synthesis:
            return synthesis
        
        # 如果没有综合结果，手动构建
        context_parts = []
        
        if "earnings_search_result" in state.get("context", {}):
            context_parts.append(f"[财报搜索]\n{state['context']['earnings_search_result']}")
        
        if "first_stock_result" in state.get("context", {}):
            company = state.get("context", {}).get("first_company", "公司1")
            context_parts.append(f"[{company.upper()}股价]\n{state['context']['first_stock_result']}")
        
        if "second_stock_result" in state.get("context", {}):
            company = state.get("context", {}).get("second_company", "公司2")
            context_parts.append(f"[{company.upper()}股价]\n{state['context']['second_stock_result']}")
        
        return "\n\n".join(context_parts) if context_parts else ""


# 全局LangGraph工作流引擎实例
langgraph_workflow_engine: Optional[LangGraphWorkflowEngine] = None


def get_langgraph_workflow_engine(tools: Dict[str, Callable]) -> LangGraphWorkflowEngine:
    """获取或创建LangGraph工作流引擎实例"""
    global langgraph_workflow_engine
    if langgraph_workflow_engine is None:
        langgraph_workflow_engine = LangGraphWorkflowEngine(tools)
    return langgraph_workflow_engine

