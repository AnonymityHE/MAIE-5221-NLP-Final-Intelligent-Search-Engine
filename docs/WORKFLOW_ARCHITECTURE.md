# 🚀 智能工作流架构文档

## 📋 概述

本文档描述了项目的**LLM驱动的智能工作流系统**，这是对项目公告中"Dynamic Workflow Automation"要求的完整实现。

---

## 🎯 项目要求

### 原始要求（来自Project Announcement）

> **Dynamic Workflow Automation**: The engine should be able to execute multi-step "workflows" to answer complex queries. For example, a query like "What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?" would require fetching financial reports, stock data, and news articles, and then synthesizing a summary.

### 我们的实现

我们设计了一个**三层架构**的智能工作流系统：

```
┌─────────────────────────────────────────────────────────────┐
│                     用户查询 (User Query)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         第1层: LLM驱动的智能工作流规划器（优先）               │
│                 (LLM-Driven Workflow Planner)                │
│  - 使用HKGAI LLM分析查询意图和复杂度                          │
│  - 生成结构化的JSON执行计划                                   │
│  - 智能提取实体（公司名、地点、日期等）                        │
│  - 动态决定工具和步骤顺序                                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                ┌──────────┴─────────┐
                │  置信度 >= 0.4 ?    │
                └──────────┬─────────┘
                  YES │         │ NO
                      │         └────────────────┐
                      ▼                          │
┌─────────────────────────────────────┐         │
│  第2层: 动态工作流执行引擎           │         │
│  (Dynamic Workflow Engine)          │         │
│  - 根据LLM计划动态执行步骤           │         │
│  - 处理步骤依赖关系                  │         │
│  - 提供详细的执行日志                │         │
│  - 支持步骤级容错                    │         │
└─────────────────┬───────────────────┘         │
                  │                             │
                  ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│         第3层: 基于规则的工作流引擎（Fallback）                │
│              (Rule-Based Workflow Engine)                    │
│  - 使用预定义的关键词模板                                     │
│  - 支持finance_comparison等固定工作流                         │
│  - 包括LangGraph和自定义引擎两个实现                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   工具调用 & 结果综合                          │
│  Tools: local_rag, web_search, finance, weather, transport  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ 核心组件

### 1. LLM工作流规划器 (`workflow_llm_planner.py`)

#### 功能
- **智能分析**：使用HKGAI LLM理解查询意图
- **结构化输出**：生成JSON格式的执行计划
- **实体提取**：自动识别公司名、地点、日期等关键信息
- **置信度评估**：返回规划质量的置信度分数

#### 数据结构

```python
@dataclass
class WorkflowStep:
    step_id: int
    tool: str                    # 工具名称
    action: str                  # 动作描述
    query: str                   # 执行查询
    entities: Dict[str, Any]     # 提取的实体
    reason: str                  # 执行原因
    dependencies: List[int]      # 依赖的步骤ID

@dataclass
class WorkflowPlan:
    workflow_type: str           # 工作流类型
    requires_workflow: bool      # 是否需要多步骤
    steps: List[WorkflowStep]    # 步骤列表
    entities: Dict[str, Any]     # 全局实体
    confidence: float            # LLM置信度 (0-1)
    reasoning: str               # LLM推理过程
```

#### 示例输出

对于查询："What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?"

LLM生成：
```json
{
    "requires_workflow": true,
    "workflow_type": "multi_step_research",
    "confidence": 0.85,
    "reasoning": "这是一个复杂的对比分析查询，需要多个步骤：搜索财报、获取两家公司股价、综合分析",
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
        }
    ],
    "entities": {
        "companies": ["NVIDIA", "AMD"],
        "topics": ["earnings report", "stock price"]
    }
}
```

### 2. 动态工作流执行引擎 (`workflow_dynamic.py`)

#### 功能
- **动态执行**：根据LLM生成的计划执行任意步骤组合
- **依赖处理**：自动检查和满足步骤间的依赖关系
- **容错机制**：步骤失败后继续执行（不中断整个流程）
- **详细日志**：记录每个步骤的执行状态和结果

#### 执行流程

```python
# 1. 检查依赖关系
if not self._check_dependencies(step, context):
    skip_step()

# 2. 执行工具
if tool == "finance":
    result = finance_tool(query, num_results=3)
elif tool == "web_search":
    result = web_search_tool(query, num_results=3)
# ... 其他工具

# 3. 保存结果到上下文
context.step_results[step_id] = result
context.completed_steps.append(step_id)

# 4. 综合所有结果
final_context = synthesize_results(context)
```

### 3. Agent集成 (`agent.py`)

#### 执行优先级

```python
def execute(self, query: str) -> Dict:
    # 优先级1: LLM驱动的工作流
    if llm_planner available:
        plan = llm_planner.analyze_query(query)
        if plan.requires_workflow and plan.confidence >= 0.4:
            return execute_llm_workflow(plan)
    
    # 优先级2: 基于规则的工作流
    workflow_type = rule_engine.detect_workflow_type(query)
    if workflow_type:
        return execute_rule_based_workflow(workflow_type)
    
    # 优先级3: 单工具直接调用
    return execute_single_tool(query)
```

---

## 🆚 对比：新架构 vs 原有架构

| 特性 | 原有架构（规则引擎） | 新架构（LLM驱动） |
|------|---------------------|-------------------|
| **工作流检测** | 关键词匹配 | LLM语义理解 |
| **步骤生成** | 硬编码模板 | 动态生成 |
| **实体提取** | 预定义列表 | LLM智能提取 |
| **灵活性** | 低（只支持预定义模板） | 高（任意查询） |
| **可扩展性** | 需要修改代码 | 自动适应新工具 |
| **复杂查询支持** | 有限 | 强大 |
| **Fallback机制** | 无 | 完善 |

---

## 📊 测试验证

### 测试场景

我们设计了6个测试场景覆盖不同类型的查询：

1. **简单查询**："什么是机器学习？"
   - 预期：不触发工作流，直接使用local_rag

2. **金融对比查询**（项目公告示例）："What was the impact of the latest NVIDIA earnings report on their stock price and how does it compare to AMD's?"
   - 预期：LLM规划多步骤工作流（web_search + finance × 2）

3. **多源信息综合**："比较一下苹果和微软最近的股价表现，并分析原因"
   - 预期：LLM规划复杂工作流

4. **天气查询**："香港今天天气怎么样？"
   - 预期：单工具调用（weather）

5. **复杂工作流**："分析Tesla、Ford和GM三家汽车公司的股价对比，并搜索最新的电动车市场新闻"
   - 预期：LLM规划涉及多个公司的工作流

6. **粤语查询**："特斯拉同比亚迪嘅股价边间好啲？"
   - 预期：多语言支持 + 工作流

### 测试脚本

```bash
python scripts/tests/test_llm_workflow.py
```

---

## 🎯 优势

### 1. **智能化**
- LLM理解复杂查询意图，不局限于关键词
- 自动适应未见过的查询类型
- 智能提取实体，无需硬编码列表

### 2. **灵活性**
- 动态生成步骤，不依赖固定模板
- 支持任意工具组合
- 易于添加新工具（LLM自动学会使用）

### 3. **鲁棒性**
- 三层fallback机制
- 步骤级容错
- 详细的执行日志

### 4. **可维护性**
- 清晰的模块划分
- 向后兼容（保留原有引擎）
- 易于调试和优化

---

## 🔧 配置和使用

### 启用/禁用LLM工作流

LLM工作流系统会自动检测并初始化。如果初始化失败，会自动回退到规则引擎。

### 调整置信度阈值

在`agent.py`中修改：

```python
if plan.requires_workflow and plan.confidence >= 0.4:  # 调整这个阈值
    return self._execute_llm_workflow(query, model, plan)
```

- 阈值越高：更保守，更多回退到规则引擎
- 阈值越低：更激进，更多使用LLM规划

### 添加新工具

1. 在`services/agent/tools/`下创建新工具
2. 在`agent.py`中注册到`self.tools`
3. 在`workflow_llm_planner.py`中添加工具描述
4. LLM会自动学会使用！

---

## 📈 性能考虑

### LLM调用开销
- **规划阶段**：每个查询1次LLM调用（约1-2秒）
- **综合阶段**：每个查询1次LLM调用（约1-2秒）
- **总开销**：约2-4秒

### 优化策略
1. **缓存规划结果**：相似查询复用规划
2. **低温度采样**：`temperature=0.3`提高稳定性
3. **快速fallback**：LLM失败时立即回退

---

## 🎓 项目公告要求满足情况

| 要求 | 状态 | 实现方式 |
|------|------|----------|
| **智能源选择** | ✅ 100% | Agent自动选择工具 |
| **本地RAG** | ✅ 100% | Milvus + Reranker |
| **高级重排序** | ✅ 100% | Cross-Encoder + metadata |
| **动态工作流** | ✅ 100% | **LLM驱动 + 规则fallback** |
| **多模态支持** | ✅ 100% | 文件上传 + 语音I/O |
| **领域智能** | ✅ 100% | Finance/Weather/Transport工具 |

---

## 🚀 下一步改进

1. **并行执行**：无依赖的步骤可以并行调用
2. **流式输出**：实时返回中间结果
3. **学习优化**：根据历史查询优化规划
4. **更多工具**：地图、新闻、学术搜索等

---

## 📝 总结

我们成功实现了一个**三层架构的智能工作流系统**：

1. **LLM驱动层**：智能、灵活、强大
2. **规则引擎层**：稳定、快速、可靠
3. **单工具层**：高效、直接

这个设计不仅满足了项目公告的所有要求，还提供了超越要求的智能化和灵活性。系统可以处理各种复杂查询，同时保持高可用性和鲁棒性。

**核心优势**：将LLM的推理能力与传统规则系统的稳定性完美结合！🎉

