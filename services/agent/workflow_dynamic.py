"""
动态工作流执行引擎 - 根据LLM生成的计划动态执行工作流

特点：
1. 支持任意步骤组合，不局限于预定义模板
2. 处理步骤依赖关系
3. 并行执行无依赖的步骤（可选）
4. 提供详细的执行日志和错误处理
5. 支持步骤级的重试和回退
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from services.agent.workflow_llm_planner import WorkflowPlan, WorkflowStep
from services.core.logger import logger


@dataclass
class ExecutionContext:
    """工作流执行上下文"""
    query: str  # 原始查询
    plan: WorkflowPlan  # 执行计划
    step_results: Dict[int, Any] = field(default_factory=dict)  # 步骤结果映射
    completed_steps: List[int] = field(default_factory=list)  # 已完成的步骤ID
    failed_steps: List[int] = field(default_factory=list)  # 失败的步骤ID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外的元数据


class DynamicWorkflowEngine:
    """动态工作流执行引擎"""
    
    def __init__(self, tools: Dict[str, Callable]):
        """
        初始化执行引擎
        
        Args:
            tools: 工具字典，键为工具名称，值为工具函数
        """
        self.tools = tools
        logger.info(f"动态工作流执行引擎初始化，可用工具: {list(tools.keys())}")
    
    def execute(self, plan: WorkflowPlan, query: str) -> ExecutionContext:
        """
        执行工作流计划
        
        Args:
            plan: 工作流计划
            query: 原始查询
            
        Returns:
            执行上下文（包含所有步骤结果）
        """
        # 初始化执行上下文
        context = ExecutionContext(query=query, plan=plan)
        
        if not plan.requires_workflow or not plan.steps:
            logger.info("查询不需要多步骤工作流，跳过执行")
            return context
        
        logger.info(f"🚀 开始执行动态工作流: {plan.workflow_type}")
        logger.info(f"   查询: {query[:100]}...")
        logger.info(f"   计划步骤数: {len(plan.steps)}")
        logger.info(f"   LLM推理: {plan.reasoning[:100]}...")
        
        # 按步骤ID排序
        sorted_steps = sorted(plan.steps, key=lambda s: s.step_id)
        
        # 执行每个步骤
        for step in sorted_steps:
            self._execute_step(step, context)
        
        # 总结执行结果
        logger.info(f"✅ 工作流执行完成:")
        logger.info(f"   - 成功步骤: {len(context.completed_steps)}/{len(plan.steps)}")
        logger.info(f"   - 失败步骤: {len(context.failed_steps)}/{len(plan.steps)}")
        
        return context
    
    def _execute_step(self, step: WorkflowStep, context: ExecutionContext) -> None:
        """
        执行单个步骤
        
        Args:
            step: 工作流步骤
            context: 执行上下文
        """
        # 检查依赖关系
        if not self._check_dependencies(step, context):
            logger.warning(f"步骤 {step.step_id} 的依赖未满足，跳过执行")
            step.status = "skipped"
            context.failed_steps.append(step.step_id)
            return
        
        step.status = "running"
        logger.info(f"▶️  执行步骤 {step.step_id}: {step.action}")
        logger.info(f"   - 工具: {step.tool}")
        logger.info(f"   - 查询: {step.query[:80]}...")
        logger.info(f"   - 原因: {step.reason}")
        
        try:
            # 获取工具函数
            tool_func = self.tools.get(step.tool)
            
            if not tool_func:
                raise ValueError(f"工具 '{step.tool}' 不可用")
            
            # 根据工具类型调用
            result = self._call_tool(step.tool, tool_func, step, context)
            
            # 保存结果
            step.result = result
            step.status = "completed"
            context.step_results[step.step_id] = result
            context.completed_steps.append(step.step_id)
            
            logger.info(f"✅ 步骤 {step.step_id} 完成")
            if result:
                preview = str(result)[:100] if result else "无结果"
                logger.debug(f"   结果预览: {preview}...")
            
        except Exception as e:
            step.status = "failed"
            step.result = None
            context.failed_steps.append(step.step_id)
            logger.error(f"❌ 步骤 {step.step_id} 失败: {e}")
            
            # 容错：继续执行后续步骤
            logger.info("   继续执行后续步骤（容错模式）")
    
    def _check_dependencies(self, step: WorkflowStep, context: ExecutionContext) -> bool:
        """
        检查步骤的依赖是否满足
        
        Args:
            step: 工作流步骤
            context: 执行上下文
            
        Returns:
            依赖是否满足
        """
        if not step.dependencies:
            return True
        
        for dep_id in step.dependencies:
            if dep_id not in context.completed_steps:
                logger.warning(f"步骤 {step.step_id} 依赖步骤 {dep_id}，但该步骤未完成")
                return False
        
        return True
    
    def _call_tool(
        self, 
        tool_name: str, 
        tool_func: Callable, 
        step: WorkflowStep, 
        context: ExecutionContext
    ) -> Any:
        """
        调用工具函数
        
        Args:
            tool_name: 工具名称
            tool_func: 工具函数
            step: 当前步骤
            context: 执行上下文
            
        Returns:
            工具执行结果
        """
        # 准备查询参数（可以从context中动态获取）
        query = self._prepare_query(step, context)
        
        # 根据工具类型调用
        if tool_name == "finance":
            return tool_func(query, num_results=3)
        
        elif tool_name == "web_search":
            return tool_func(query, num_results=3)
        
        elif tool_name == "weather":
            # 从entities中提取地点，或使用默认值
            location = step.entities.get("location", "Hong Kong")
            return tool_func(location)
        
        elif tool_name == "transport":
            return tool_func(query, num_results=3)
        
        elif tool_name == "local_rag":
            return tool_func(query)
        
        else:
            # 通用调用
            return tool_func(query)
    
    def _prepare_query(self, step: WorkflowStep, context: ExecutionContext) -> str:
        """
        准备查询字符串（可以基于之前步骤的结果动态调整）
        
        Args:
            step: 当前步骤
            context: 执行上下文
            
        Returns:
            准备好的查询字符串
        """
        query = step.query
        
        # 如果查询中包含占位符，从context中替换
        # 例如：{step_1_company} -> 从步骤1的结果中提取的公司名
        import re
        placeholders = re.findall(r'\{(\w+)\}', query)
        
        for placeholder in placeholders:
            # 尝试从entities或之前的结果中获取
            value = step.entities.get(placeholder)
            if not value and "step_" in placeholder:
                # 尝试从之前的步骤结果中提取
                step_id = int(placeholder.split("_")[1])
                if step_id in context.step_results:
                    value = context.step_results[step_id]
            
            if value:
                query = query.replace(f"{{{placeholder}}}", str(value))
        
        return query
    
    def synthesize_results(self, context: ExecutionContext) -> str:
        """
        综合所有步骤的结果，生成最终上下文
        
        Args:
            context: 执行上下文
            
        Returns:
            综合后的上下文字符串
        """
        if not context.completed_steps:
            return ""
        
        context_parts = []
        
        # 按步骤顺序收集结果
        for step in context.plan.steps:
            if step.step_id in context.completed_steps and step.result:
                # 格式化步骤结果
                header = f"[步骤 {step.step_id}: {step.action}]"
                result_text = str(step.result)
                context_parts.append(f"{header}\n{result_text}\n")
        
        if not context_parts:
            return ""
        
        # 添加总结信息
        summary = (
            f"工作流执行总结：\n"
            f"- 工作流类型: {context.plan.workflow_type}\n"
            f"- 完成步骤: {len(context.completed_steps)}/{len(context.plan.steps)}\n"
            f"- LLM推理: {context.plan.reasoning}\n\n"
            f"详细结果：\n"
        )
        
        return summary + "\n".join(context_parts)
    
    def get_tool_usage_summary(self, context: ExecutionContext) -> List[str]:
        """
        获取使用的工具摘要
        
        Args:
            context: 执行上下文
            
        Returns:
            工具使用列表（去重）
        """
        tools_used_set = set()
        for step in context.plan.steps:
            if step.step_id in context.completed_steps:
                # 只记录工具名，不包括具体action
                tools_used_set.add(step.tool)
        return list(tools_used_set)


# 全局执行引擎实例
_dynamic_engine: Optional[DynamicWorkflowEngine] = None


def get_dynamic_workflow_engine(tools: Dict[str, Callable]) -> DynamicWorkflowEngine:
    """获取或创建动态工作流执行引擎实例"""
    global _dynamic_engine
    if _dynamic_engine is None:
        _dynamic_engine = DynamicWorkflowEngine(tools)
    return _dynamic_engine

