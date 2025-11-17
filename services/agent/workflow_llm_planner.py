"""
LLM驱动的工作流规划器 - 使用LLM智能分析查询并生成执行计划

实现思路：
1. 使用LLM分析用户查询，理解意图和复杂度
2. 生成结构化的执行计划（JSON格式）
3. 提取查询中的实体（公司名、地点、日期等）
4. 动态决定需要调用哪些工具和步骤顺序

示例：
查询："What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?"

LLM生成的计划：
{
    "workflow_type": "multi_step_research",
    "requires_workflow": true,
    "steps": [
        {
            "step_id": 1,
            "tool": "web_search",
            "action": "搜索NVIDIA最新财报",
            "query": "NVIDIA latest earnings report 2024",
            "reason": "需要获取最新的财报信息"
        },
        {
            "step_id": 2,
            "tool": "finance",
            "action": "获取NVIDIA股价",
            "query": "NVIDIA stock price",
            "entities": {"company": "NVIDIA", "symbol": "NVDA"},
            "reason": "需要获取财报后的股价变化"
        },
        {
            "step_id": 3,
            "tool": "finance",
            "action": "获取AMD股价",
            "query": "AMD stock price",
            "entities": {"company": "AMD", "symbol": "AMD"},
            "reason": "需要对比AMD的股价表现"
        },
        {
            "step_id": 4,
            "tool": "synthesize",
            "action": "综合分析结果",
            "reason": "整合所有信息生成对比分析"
        }
    ],
    "entities": {
        "companies": ["NVIDIA", "AMD"],
        "topics": ["earnings report", "stock price"]
    }
}
"""
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from services.llm.unified_client import unified_llm_client
from services.core.logger import logger


@dataclass
class WorkflowStep:
    """工作流步骤定义"""
    step_id: int
    tool: str  # 工具名称：web_search, finance, weather, transport, local_rag
    action: str  # 动作描述
    query: str  # 执行查询
    entities: Dict[str, Any] = field(default_factory=dict)  # 提取的实体
    reason: str = ""  # 执行原因
    dependencies: List[int] = field(default_factory=list)  # 依赖的步骤ID
    result: Optional[Any] = None  # 执行结果
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class WorkflowPlan:
    """工作流执行计划"""
    workflow_type: str  # 工作流类型
    requires_workflow: bool  # 是否需要多步骤工作流
    steps: List[WorkflowStep]  # 步骤列表
    entities: Dict[str, Any] = field(default_factory=dict)  # 全局提取的实体
    confidence: float = 0.0  # LLM规划的置信度
    reasoning: str = ""  # LLM的推理过程


class LLMWorkflowPlanner:
    """LLM驱动的工作流规划器"""
    
    def __init__(self, available_tools: List[str]):
        """
        初始化规划器
        
        Args:
            available_tools: 可用的工具列表
        """
        self.available_tools = available_tools
        logger.info(f"LLM工作流规划器初始化，可用工具: {', '.join(available_tools)}")
    
    def analyze_query(self, query: str) -> WorkflowPlan:
        """
        使用LLM分析查询并生成工作流计划
        
        Args:
            query: 用户查询
            
        Returns:
            工作流计划
        """
        logger.info(f"🧠 LLM开始分析查询: '{query[:100]}...'")
        
        # 构建LLM提示词
        system_prompt = self._build_planner_prompt()
        user_prompt = f"""
请分析以下用户查询，判断是否需要多步骤工作流，并生成执行计划。

用户查询：{query}

请以JSON格式返回分析结果。
"""
        
        try:
            # 调用LLM进行规划
            llm_result = unified_llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1500,
                temperature=0.3,  # 低温度以获得更稳定的规划结果
                provider="hkgai"  # 使用HKGAI进行规划
            )
            
            if "error" in llm_result:
                logger.error(f"LLM规划失败: {llm_result['error']}")
                return self._create_simple_plan(query)
            
            # 解析LLM返回的JSON
            plan_json = self._extract_json_from_response(llm_result.get("content", ""))
            
            if not plan_json:
                logger.warning("无法从LLM响应中提取JSON，使用简单规划")
                return self._create_simple_plan(query)
            
            # 构建WorkflowPlan对象
            workflow_plan = self._parse_plan_json(plan_json, query)
            
            logger.info(f"✅ LLM规划完成: 工作流类型={workflow_plan.workflow_type}, "
                       f"需要工作流={workflow_plan.requires_workflow}, "
                       f"步骤数={len(workflow_plan.steps)}")
            
            return workflow_plan
            
        except Exception as e:
            logger.error(f"LLM工作流规划异常: {e}")
            return self._create_simple_plan(query)
    
    def _build_planner_prompt(self) -> str:
        """构建LLM规划器的系统提示词"""
        tools_description = self._get_tools_description()
        
        return f"""你是一个智能工作流规划器，负责分析用户查询并生成执行计划。

可用工具：
{tools_description}

你的任务：
1. 分析用户查询的复杂度和意图
2. 判断是否需要多步骤工作流（单一工具可以解决的查询不需要工作流）
3. 如果需要工作流，生成结构化的执行计划
4. 从查询中提取关键实体（公司名、地点、日期、股票代码等）

判断标准 - 需要工作流的情况：
- 查询涉及对比分析（如"比较A和B"）
- 查询需要多个数据源（如"财报对股价的影响"）
- 查询包含多个子问题
- 查询需要时序分析或历史对比

判断标准 - 不需要工作流的情况：
- 简单的单一查询（如"今天天气怎么样"）
- 只需要一个工具就能回答
- 查询是知识问答类型

返回JSON格式：
{{
    "requires_workflow": true/false,
    "workflow_type": "工作流类型（如multi_step_research, comparison_analysis, time_series等）",
    "reasoning": "你的推理过程",
    "confidence": 0.0-1.0的置信度,
    "steps": [
        {{
            "step_id": 1,
            "tool": "工具名称",
            "action": "动作描述",
            "query": "具体的查询字符串",
            "entities": {{"提取的实体"}},
            "reason": "为什么需要这一步",
            "dependencies": [依赖的步骤ID列表]
        }}
    ],
    "entities": {{
        "提取的全局实体"
    }}
}}

重要：
- 如果requires_workflow为false，steps数组可以为空或只包含一个步骤
- 步骤顺序要合理，考虑依赖关系
- query字段要具体可执行，不要太模糊
- 优先使用专业工具（finance、weather、transport）而非web_search
- 只返回JSON，不要有其他文字
"""
    
    def _get_tools_description(self) -> str:
        """获取工具描述"""
        descriptions = {
            "local_rag": "本地知识库检索 - 从已索引的文档中检索信息",
            "web_search": "网页搜索 - 搜索互联网获取最新信息",
            "finance": "金融工具 - 获取股票、加密货币价格和金融数据",
            "weather": "天气工具 - 获取当前天气和预报信息",
            "transport": "交通工具 - 查询旅行时间、路线和物流信息"
        }
        
        result = []
        for tool in self.available_tools:
            if tool in descriptions:
                result.append(f"- {tool}: {descriptions[tool]}")
        
        return "\n".join(result)
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """从LLM响应中提取JSON"""
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取JSON代码块
            import re
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    pass
            
            # 尝试查找第一个{到最后一个}
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                try:
                    return json.loads(response[start_idx:end_idx+1])
                except json.JSONDecodeError:
                    pass
            
            return None
    
    def _parse_plan_json(self, plan_json: Dict, original_query: str) -> WorkflowPlan:
        """将JSON转换为WorkflowPlan对象"""
        requires_workflow = plan_json.get("requires_workflow", False)
        workflow_type = plan_json.get("workflow_type", "simple_query")
        reasoning = plan_json.get("reasoning", "")
        confidence = plan_json.get("confidence", 0.5)
        entities = plan_json.get("entities", {})
        
        steps = []
        for step_data in plan_json.get("steps", []):
            step = WorkflowStep(
                step_id=step_data.get("step_id", len(steps) + 1),
                tool=step_data.get("tool", "local_rag"),
                action=step_data.get("action", ""),
                query=step_data.get("query", original_query),
                entities=step_data.get("entities", {}),
                reason=step_data.get("reason", ""),
                dependencies=step_data.get("dependencies", [])
            )
            steps.append(step)
        
        return WorkflowPlan(
            workflow_type=workflow_type,
            requires_workflow=requires_workflow,
            steps=steps,
            entities=entities,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _create_simple_plan(self, query: str) -> WorkflowPlan:
        """创建简单的单步骤计划（LLM规划失败时的fallback）"""
        logger.info("创建简单的fallback计划")
        return WorkflowPlan(
            workflow_type="simple_query",
            requires_workflow=False,
            steps=[
                WorkflowStep(
                    step_id=1,
                    tool="local_rag",
                    action="直接回答",
                    query=query,
                    reason="LLM规划失败，使用简单查询模式"
                )
            ],
            entities={},
            confidence=0.3,
            reasoning="LLM规划失败，回退到简单模式"
        )
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """
        使用LLM从查询中提取实体
        
        Args:
            query: 用户查询
            
        Returns:
            提取的实体字典
        """
        system_prompt = """你是一个实体提取专家。从用户查询中提取关键实体。

需要提取的实体类型：
- companies: 公司名称列表
- stock_symbols: 股票代码列表
- locations: 地点列表
- dates: 日期/时间表达
- topics: 主题/关键词列表
- numbers: 数字和度量

返回JSON格式：
{
    "companies": [...],
    "stock_symbols": [...],
    "locations": [...],
    "dates": [...],
    "topics": [...],
    "numbers": [...]
}

只返回JSON，不要有其他文字。"""
        
        user_prompt = f"请从以下查询中提取实体：\n\n{query}"
        
        try:
            llm_result = unified_llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=500,
                temperature=0.1,
                provider="hkgai"
            )
            
            if "error" not in llm_result:
                entities_json = self._extract_json_from_response(llm_result.get("content", ""))
                if entities_json:
                    return entities_json
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
        
        return {}


# 全局规划器实例
_llm_planner: Optional[LLMWorkflowPlanner] = None


def get_llm_workflow_planner(tools: List[str]) -> LLMWorkflowPlanner:
    """获取或创建LLM工作流规划器实例"""
    global _llm_planner
    if _llm_planner is None:
        _llm_planner = LLMWorkflowPlanner(tools)
    return _llm_planner

