"""
对比HKGAI vs Gemini作为工作流规划器的效果
"""
import sys
import os
from typing import Dict, List
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.agent.workflow_llm_planner import WorkflowPlan, WorkflowStep
from services.llm.unified_client import unified_llm_client
from services.core.config import settings
from services.core.logger import logger


# 扩展的测试问题集
COMPREHENSIVE_TESTS = [
    # 简单查询
    {
        "id": 1,
        "query": "什么是人工智能？",
        "expected_workflow": False,
        "category": "知识问答"
    },
    {
        "id": 2,
        "query": "苹果公司的股票代码是什么？",
        "expected_workflow": False,
        "category": "简单事实查询"
    },
    # 金融对比
    {
        "id": 3,
        "query": "Compare the stock performance of Tesla and BYD in the last month",
        "expected_workflow": True,
        "category": "金融对比（英文）"
    },
    {
        "id": 4,
        "query": "分析微软、苹果和谷歌三家公司的股价对比",
        "expected_workflow": True,
        "category": "多目标金融对比（中文）"
    },
    # 跨领域
    {
        "id": 5,
        "query": "香港今天天气怎么样，适合去深圳旅游吗？交通需要多久？",
        "expected_workflow": True,
        "category": "跨领域综合"
    },
    # 复杂分析
    {
        "id": 6,
        "query": "What was the impact of the latest NVIDIA earnings report on their stock price?",
        "expected_workflow": True,
        "category": "项目公告示例"
    },
    # 时序对比
    {
        "id": 7,
        "query": "对比一下比特币和以太坊最近一周的价格走势",
        "expected_workflow": True,
        "category": "加密货币对比"
    },
    # 边界案例
    {
        "id": 8,
        "query": "Tell me about recent AI developments",
        "expected_workflow": False,  # 可能触发也可能不触发
        "category": "实时信息"
    },
]


class GeminiPlanner:
    """使用Gemini Flash作为规划器"""
    
    def __init__(self, tools: List[str]):
        self.available_tools = tools
        logger.info("初始化Gemini规划器（使用gemini-flash-exp）")
    
    def analyze_query(self, query: str) -> WorkflowPlan:
        """使用Gemini分析查询"""
        system_prompt = self._build_planner_prompt()
        user_prompt = f"""
请分析以下用户查询，判断是否需要多步骤工作流，并生成执行计划。

用户查询：{query}

请以JSON格式返回分析结果。
"""
        
        try:
            # 使用Gemini Flash
            llm_result = unified_llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1500,
                temperature=0.3,
                model="gemini-2.0-flash-exp",  # 使用flash版本
                provider="gemini"
            )
            
            if "error" in llm_result:
                logger.error(f"Gemini规划失败: {llm_result['error']}")
                return self._create_simple_plan(query)
            
            # 解析JSON
            plan_json = self._extract_json(llm_result.get("content", ""))
            if not plan_json:
                return self._create_simple_plan(query)
            
            return self._parse_plan_json(plan_json, query)
            
        except Exception as e:
            logger.error(f"Gemini工作流规划异常: {e}")
            return self._create_simple_plan(query)
    
    def _build_planner_prompt(self) -> str:
        """构建Gemini规划器的系统提示词"""
        tools_desc = "\n".join([f"- {t}" for t in self.available_tools])
        
        return f"""你是一个智能工作流规划器。

可用工具：
{tools_desc}

判断标准 - 需要工作流的情况：
- 涉及对比分析（如"比较A和B"）
- 需要多个数据源
- 包含多个子问题
- 需要时序分析

判断标准 - 不需要工作流的情况：
- 简单的单一查询
- 只需要一个工具
- 知识问答类型

返回JSON格式（只返回JSON，不要有其他文字）：
{{
    "requires_workflow": true/false,
    "workflow_type": "工作流类型",
    "reasoning": "推理过程",
    "confidence": 0.0-1.0,
    "steps": [
        {{
            "step_id": 1,
            "tool": "工具名称",
            "action": "动作描述",
            "query": "具体查询",
            "entities": {{}},
            "reason": "原因"
        }}
    ],
    "entities": {{}}
}}
"""
    
    def _extract_json(self, response: str):
        """从响应中提取JSON"""
        import re
        try:
            return json.loads(response)
        except:
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0])
                except:
                    pass
            
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(response[start:end+1])
                except:
                    pass
        return None
    
    def _parse_plan_json(self, plan_json: Dict, query: str) -> WorkflowPlan:
        """解析JSON为WorkflowPlan"""
        from services.agent.workflow_llm_planner import WorkflowPlan, WorkflowStep
        
        steps = []
        for s in plan_json.get("steps", []):
            step = WorkflowStep(
                step_id=s.get("step_id", len(steps) + 1),
                tool=s.get("tool", "local_rag"),
                action=s.get("action", ""),
                query=s.get("query", query),
                entities=s.get("entities", {}),
                reason=s.get("reason", "")
            )
            steps.append(step)
        
        return WorkflowPlan(
            workflow_type=plan_json.get("workflow_type", "simple"),
            requires_workflow=plan_json.get("requires_workflow", False),
            steps=steps,
            entities=plan_json.get("entities", {}),
            confidence=plan_json.get("confidence", 0.5),
            reasoning=plan_json.get("reasoning", "")
        )
    
    def _create_simple_plan(self, query: str) -> WorkflowPlan:
        """创建简单计划"""
        from services.agent.workflow_llm_planner import WorkflowPlan, WorkflowStep
        
        return WorkflowPlan(
            workflow_type="simple_query",
            requires_workflow=False,
            steps=[],
            entities={},
            confidence=0.3,
            reasoning="Gemini规划失败，fallback"
        )


def compare_planners(query_info: Dict, hkgai_plan: WorkflowPlan, gemini_plan: WorkflowPlan):
    """对比两个规划器的结果"""
    print("\n" + "="*120)
    print(f"📝 测试 #{query_info['id']}: {query_info['category']}")
    print("="*120)
    print(f"🔍 查询: {query_info['query']}")
    print(f"💭 预期: {'需要工作流' if query_info['expected_workflow'] else '不需要工作流'}")
    print("\n" + "-"*120)
    
    # HKGAI结果
    print("🟦 HKGAI规划:")
    print(f"   需要工作流: {hkgai_plan.requires_workflow}")
    print(f"   工作流类型: {hkgai_plan.workflow_type}")
    print(f"   置信度: {hkgai_plan.confidence:.2f}")
    print(f"   步骤数: {len(hkgai_plan.steps)}")
    print(f"   推理: {hkgai_plan.reasoning[:100]}...")
    
    # Gemini结果
    print("\n🟩 Gemini Flash规划:")
    print(f"   需要工作流: {gemini_plan.requires_workflow}")
    print(f"   工作流类型: {gemini_plan.workflow_type}")
    print(f"   置信度: {gemini_plan.confidence:.2f}")
    print(f"   步骤数: {len(gemini_plan.steps)}")
    print(f"   推理: {gemini_plan.reasoning[:100]}...")
    
    # 对比分析
    print("\n" + "-"*120)
    print("📊 对比分析:")
    
    # 判断准确性
    hkgai_correct = hkgai_plan.requires_workflow == query_info['expected_workflow']
    gemini_correct = gemini_plan.requires_workflow == query_info['expected_workflow']
    
    if hkgai_correct and gemini_correct:
        print("  ✅ 两者判断都正确")
    elif hkgai_correct:
        print("  🟦 HKGAI判断正确，Gemini判断错误")
    elif gemini_correct:
        print("  🟩 Gemini判断正确，HKGAI判断错误")
    else:
        print("  ❌ 两者判断都错误")
    
    # 对比置信度
    if abs(hkgai_plan.confidence - gemini_plan.confidence) < 0.1:
        print(f"  ⚖️  置信度相近 (差距: {abs(hkgai_plan.confidence - gemini_plan.confidence):.2f})")
    elif hkgai_plan.confidence > gemini_plan.confidence:
        print(f"  🟦 HKGAI置信度更高 (+{hkgai_plan.confidence - gemini_plan.confidence:.2f})")
    else:
        print(f"  🟩 Gemini置信度更高 (+{gemini_plan.confidence - hkgai_plan.confidence:.2f})")
    
    # 对比步骤数
    if hkgai_plan.requires_workflow and gemini_plan.requires_workflow:
        if len(hkgai_plan.steps) == len(gemini_plan.steps):
            print(f"  ⚖️  步骤数相同 ({len(hkgai_plan.steps)}步)")
        elif len(hkgai_plan.steps) > len(gemini_plan.steps):
            print(f"  🟦 HKGAI规划更详细 ({len(hkgai_plan.steps)} vs {len(gemini_plan.steps)}步)")
        else:
            print(f"  🟩 Gemini规划更详细 ({len(gemini_plan.steps)} vs {len(hkgai_plan.steps)}步)")
    
    print("="*120)
    
    return hkgai_correct, gemini_correct


def run_comparison():
    """运行对比测试"""
    logger.info("\n\n" + "🔬 HKGAI vs Gemini规划器对比测试".center(120, "="))
    
    tools = ["local_rag", "web_search", "weather", "finance", "transport"]
    
    # 初始化规划器
    from services.agent.workflow_llm_planner import get_llm_workflow_planner
    hkgai_planner = get_llm_workflow_planner(tools)
    gemini_planner = GeminiPlanner(tools)
    
    logger.info(f"📍 测试配置:")
    logger.info(f"   - HKGAI模型: {settings.HKGAI_MODEL_ID}")
    logger.info(f"   - Gemini模型: gemini-2.0-flash-exp")
    logger.info(f"   - 测试问题数: {len(COMPREHENSIVE_TESTS)}\n")
    
    hkgai_correct = 0
    gemini_correct = 0
    
    for query_info in COMPREHENSIVE_TESTS:
        try:
            logger.info(f"\n{'='*50} 测试 #{query_info['id']} {'='*50}")
            
            # HKGAI规划
            hkgai_plan = hkgai_planner.analyze_query(query_info['query'])
            
            # Gemini规划
            gemini_plan = gemini_planner.analyze_query(query_info['query'])
            
            # 对比结果
            h_correct, g_correct = compare_planners(query_info, hkgai_plan, gemini_plan)
            
            if h_correct:
                hkgai_correct += 1
            if g_correct:
                gemini_correct += 1
                
        except Exception as e:
            logger.error(f"测试 #{query_info['id']} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 总结
    print("\n\n" + "="*120)
    print("📊 对比总结")
    print("="*120)
    print(f"总测试数: {len(COMPREHENSIVE_TESTS)}")
    print(f"\n🟦 HKGAI准确率: {hkgai_correct}/{len(COMPREHENSIVE_TESTS)} ({hkgai_correct/len(COMPREHENSIVE_TESTS)*100:.1f}%)")
    print(f"🟩 Gemini准确率: {gemini_correct}/{len(COMPREHENSIVE_TESTS)} ({gemini_correct/len(COMPREHENSIVE_TESTS)*100:.1f}%)")
    
    if hkgai_correct > gemini_correct:
        print(f"\n🏆 胜者: HKGAI (+{hkgai_correct - gemini_correct})")
    elif gemini_correct > hkgai_correct:
        print(f"\n🏆 胜者: Gemini Flash (+{gemini_correct - hkgai_correct})")
    else:
        print("\n🤝 平局")
    
    print("\n💡 建议:")
    if hkgai_correct >= gemini_correct:
        print("  - HKGAI作为主规划器表现优秀，可以继续使用")
        print("  - Gemini Flash可以作为fallback选项")
    else:
        print("  - 考虑将Gemini Flash作为主规划器")
        print("  - HKGAI可以作为fallback选项")
    
    print("="*120 + "\n")


if __name__ == "__main__":
    run_comparison()

