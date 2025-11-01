"""
动态工作流引擎 - 支持多步骤查询和工具链执行

实现项目要求：Dynamic Workflow Automation
示例："What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?"
需要：获取财报 → 获取NVIDIA股价 → 获取AMD股价 → 综合分析

注意：此文件包含自定义工作流实现。如果要使用LangGraph，请使用 workflow_langgraph.py
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from services.core.logger import logger

# 尝试导入LangGraph版本（如果可用）
try:
    from services.agent.workflow_langgraph import LangGraphWorkflowEngine, get_langgraph_workflow_engine, LANGGRAPH_AVAILABLE
except ImportError:
    LANGGRAPH_AVAILABLE = False
    LangGraphWorkflowEngine = None
    get_langgraph_workflow_engine = None


class WorkflowStepStatus(Enum):
    """工作流步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤定义"""
    name: str  # 步骤名称
    tool_name: str  # 要使用的工具名称
    tool_func: Callable  # 工具函数
    condition: Optional[Callable] = None  # 执行条件（可选）
    input_extractor: Optional[Callable] = None  # 从上下文提取输入的函数
    result_processor: Optional[Callable] = None  # 处理结果的函数
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class WorkflowState:
    """工作流状态"""
    query: str  # 原始查询
    steps: List[WorkflowStep]  # 步骤列表
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文数据
    current_step_index: int = 0  # 当前步骤索引
    completed: bool = False
    final_answer: Optional[str] = None


class WorkflowEngine:
    """动态工作流引擎"""
    
    def __init__(self, tools: Dict[str, Callable]):
        """
        初始化工作流引擎
        
        Args:
            tools: 工具字典，键为工具名称，值为工具函数
        """
        self.tools = tools
        self.workflow_templates = self._init_workflow_templates()
    
    def _init_workflow_templates(self) -> Dict[str, List[Dict]]:
        """初始化预定义的工作流模板"""
        return {
            "finance_comparison": [
                {
                    "name": "search_earnings",
                    "tool_name": "web_search",
                    "description": "搜索财报信息"
                },
                {
                    "name": "get_stock_price_1",
                    "tool_name": "finance",
                    "description": "获取第一个公司股价"
                },
                {
                    "name": "get_stock_price_2",
                    "tool_name": "finance",
                    "description": "获取第二个公司股价"
                },
                {
                    "name": "synthesize",
                    "tool_name": "local_rag",
                    "description": "综合分析和对比"
                }
            ]
        }
    
    def detect_workflow_type(self, query: str) -> Optional[str]:
        """
        检测查询需要的工作流类型
        
        Args:
            query: 用户查询
            
        Returns:
            工作流类型名称，如果不需要工作流则返回None
        """
        query_lower = query.lower()
        
        # 检测金融对比查询（如NVIDIA vs AMD）
        finance_comparison_keywords = [
            "compare", "对比", "vs", "versus", "difference", "差异",
            "impact", "影响", "earnings", "财报", "stock price", "股价"
        ]
        
        if any(kw in query_lower for kw in finance_comparison_keywords):
            # 检查是否涉及多个股票/公司
            # 简单检测：包含多个股票代码或公司名
            company_keywords = ["nvidia", "amd", "apple", "microsoft", "google", "tesla"]
            company_count = sum(1 for company in company_keywords if company in query_lower)
            
            if company_count >= 2 or ("compare" in query_lower and "stock" in query_lower):
                return "finance_comparison"
        
        # 可以添加更多工作流类型检测
        
        return None
    
    def build_workflow(self, query: str, workflow_type: Optional[str] = None) -> List[WorkflowStep]:
        """
        根据查询构建工作流步骤
        
        Args:
            query: 用户查询
            workflow_type: 工作流类型（如果为None则自动检测）
            
        Returns:
            工作流步骤列表
        """
        if workflow_type is None:
            workflow_type = self.detect_workflow_type(query)
        
        if workflow_type is None:
            # 不需要多步骤工作流，返回空列表
            return []
        
        steps = []
        
        if workflow_type == "finance_comparison":
            # 金融对比工作流
            # Step 1: 搜索财报
            steps.append(WorkflowStep(
                name="search_earnings",
                tool_name="web_search",
                tool_func=self.tools.get("web_search"),
                input_extractor=lambda q, ctx: q  # 使用原始查询
            ))
            
            # Step 2: 提取第一个公司名并获取股价
            def extract_first_company(query: str, context: Dict) -> str:
                # 简单提取：查找第一个公司名
                companies = ["nvidia", "amd", "apple", "microsoft", "google", "tesla", "amazon"]
                query_lower = query.lower()
                for company in companies:
                    if company in query_lower:
                        return f"{company} stock price"
                return query
            
            steps.append(WorkflowStep(
                name="get_first_stock_price",
                tool_name="finance",
                tool_func=self.tools.get("finance"),
                input_extractor=extract_first_company
            ))
            
            # Step 3: 提取第二个公司名并获取股价
            def extract_second_company(query: str, context: Dict) -> str:
                # 提取第二个公司名（排除第一个）
                companies = ["nvidia", "amd", "apple", "microsoft", "google", "tesla", "amazon"]
                query_lower = query.lower()
                found_companies = [c for c in companies if c in query_lower]
                if len(found_companies) >= 2:
                    return f"{found_companies[1]} stock price"
                # 如果只有一个，尝试从查询中提取对比对象
                if "vs" in query_lower or "compare" in query_lower:
                    # 尝试提取对比对象
                    pass
                return query
            
            steps.append(WorkflowStep(
                name="get_second_stock_price",
                tool_name="finance",
                tool_func=self.tools.get("finance"),
                input_extractor=extract_second_company
            ))
        
        return steps
    
    def execute_workflow(self, query: str, workflow_steps: List[WorkflowStep]) -> WorkflowState:
        """
        执行工作流
        
        Args:
            query: 原始查询
            workflow_steps: 工作流步骤列表
            
        Returns:
            工作流执行状态
        """
        state = WorkflowState(query=query, steps=workflow_steps)
        
        logger.info(f"开始执行工作流，共 {len(workflow_steps)} 个步骤")
        
        for i, step in enumerate(workflow_steps):
            state.current_step_index = i
            step.status = WorkflowStepStatus.RUNNING
            
            logger.info(f"执行步骤 {i+1}/{len(workflow_steps)}: {step.name} ({step.tool_name})")
            
            try:
                # 检查执行条件
                if step.condition and not step.condition(query, state.context):
                    step.status = WorkflowStepStatus.SKIPPED
                    logger.info(f"步骤 {step.name} 跳过（条件不满足）")
                    continue
                
                # 提取输入
                if step.input_extractor:
                    step_input = step.input_extractor(query, state.context)
                else:
                    step_input = query
                
                # 执行工具
                if step.tool_name == "finance":
                    result = step.tool_func(step_input, num_results=3)
                elif step.tool_name == "web_search":
                    result = step.tool_func(step_input, num_results=3)
                elif step.tool_name == "local_rag":
                    result = step.tool_func(step_input)
                else:
                    result = step.tool_func(step_input)
                
                # 处理结果
                if step.result_processor:
                    processed_result = step.result_processor(result, state.context)
                else:
                    processed_result = result
                
                step.result = processed_result
                step.status = WorkflowStepStatus.COMPLETED
                
                # 将结果添加到上下文
                state.context[f"{step.name}_result"] = processed_result
                state.context[f"step_{i}_result"] = processed_result
                
                logger.info(f"步骤 {step.name} 完成")
                
            except Exception as e:
                step.status = WorkflowStepStatus.FAILED
                step.error = str(e)
                logger.error(f"步骤 {step.name} 失败: {e}")
                # 继续执行后续步骤（容错）
                continue
        
        state.completed = True
        logger.info("工作流执行完成")
        
        return state
    
    def synthesize_workflow_results(self, state: WorkflowState) -> str:
        """
        综合工作流结果，生成最终上下文
        
        Args:
            state: 工作流状态
            
        Returns:
            综合后的上下文字符串
        """
        context_parts = []
        
        for step in state.steps:
            if step.status == WorkflowStepStatus.COMPLETED and step.result:
                context_parts.append(f"[{step.name}]\n{step.result}\n")
        
        return "\n\n".join(context_parts)


# 全局工作流引擎实例（将在Agent中初始化）
workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine(tools: Dict[str, Callable]) -> WorkflowEngine:
    """获取或创建工作流引擎实例"""
    global workflow_engine
    if workflow_engine is None:
        workflow_engine = WorkflowEngine(tools)
    return workflow_engine

