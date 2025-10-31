# Services目录重构方案

> ⚠️ **注意**：本文档是重构前的计划文档，重构已完成。
> 
> 查看重构完成记录：[REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md)
> 
> 本文档保留作为参考，展示重构的规划过程。

## 当前问题分析

### 当前结构
```
services/
├── __init__.py (空)
├── agent.py
├── config.py / config.example.py
├── file_indexer.py
├── file_processor.py
├── file_storage.py
├── gemini_client.py
├── llm_client.py
├── logger.py
├── milvus_client.py
├── milvus_metadata.py
├── reranker.py
├── retriever.py
├── storage_backend.py
├── unified_llm_client.py
├── usage_monitor.py
└── tools/
    ├── finance_tool.py
    ├── local_rag_tool.py
    ├── transport_tool.py
    ├── weather_tool.py
    └── web_search_tool.py
```

### 存在的问题

1. **文件过多，缺乏分类**：18个文件都在根目录，难以快速定位
2. **职责不清晰**：相关功能分散在不同文件中
3. **导入路径复杂**：`from services.xxx import yyy` 过长
4. **命名不一致**：
   - `llm_client.py` vs `gemini_client.py` vs `unified_llm_client.py`
   - `storage_backend.py` vs `milvus_metadata.py` 关系不明确

## 重构方案

### 新结构设计

```
services/
├── __init__.py          # 统一导出主要接口
├── core/                # 核心基础设施
│   ├── __init__.py
│   ├── config.py        # 配置管理
│   └── logger.py        # 日志系统
├── llm/                 # LLM相关模块
│   ├── __init__.py
│   ├── base.py          # LLM客户端基类（可选）
│   ├── hkgai_client.py  # HKGAI客户端（从llm_client.py重命名）
│   ├── gemini_client.py # Gemini客户端
│   ├── unified_client.py # 统一客户端（从unified_llm_client.py重命名）
│   └── usage_monitor.py # 用量监控
├── vector/              # 向量数据库相关
│   ├── __init__.py
│   ├── milvus_client.py # Milvus客户端
│   ├── retriever.py     # RAG检索器
│   └── reranker.py    # 重排序器
├── storage/             # 存储相关
│   ├── __init__.py
│   ├── file_storage.py  # 文件存储管理
│   ├── file_processor.py # 文件处理器
│   ├── file_indexer.py  # 文件索引器
│   ├── backend.py       # 存储后端抽象（从storage_backend.py重命名）
│   └── milvus_metadata.py # Milvus元数据（可选，可合并到backend）
└── agent/               # Agent相关
    ├── __init__.py
    ├── agent.py         # Agent主逻辑
    └── tools/           # Agent工具
        ├── __init__.py
        ├── base.py      # 工具基类（可选）
        ├── local_rag.py
        ├── web_search.py
        ├── weather.py
        ├── finance.py
        └── transport.py
```

### 重构优势

1. **清晰的模块划分**：按功能分类，易于理解和维护
2. **更短的导入路径**：`from services.llm import unified_client`
3. **职责明确**：每个子目录有明确的职责
4. **易于扩展**：添加新功能时更容易找到位置

## 重构步骤

### 阶段1：创建新目录结构（保持向后兼容）

1. 创建新目录
2. 移动文件到新位置
3. 更新 `services/__init__.py` 提供向后兼容的导入
4. 更新所有导入语句

### 阶段2：统一导出接口

通过 `services/__init__.py` 提供统一入口：

```python
# services/__init__.py
from services.core.config import settings
from services.core.logger import logger
from services.llm.unified_client import unified_llm_client
from services.vector.retriever import retriever
from services.agent.agent import agent
from services.storage.file_storage import file_storage

__all__ = [
    "settings",
    "logger", 
    "unified_llm_client",
    "retriever",
    "agent",
    "file_storage",
    # ... 其他常用导出
]
```

### 阶段3：清理和优化

1. 删除旧文件（如果已移动）
2. 更新文档
3. 运行测试确保一切正常

## 实施建议

### 选项1：渐进式重构（推荐）

保持向后兼容，逐步迁移：
- 先创建新结构
- 在新位置添加文件（复制而非移动）
- 更新新代码使用新路径
- 逐步迁移旧代码
- 最后删除旧文件

### 选项2：一次性重构

一次性完成所有重构：
- 风险更高，但更彻底
- 需要全面测试
- 适合在功能稳定时进行

## 注意事项

1. **保持向后兼容**：确保现有代码不中断
2. **更新导入**：所有 `from services.xxx` 的导入都需要更新
3. **测试覆盖**：重构后全面测试所有功能
4. **文档更新**：更新README和相关文档

## 代码变更清单

### 需要更新的文件

1. `backend/api.py` - 更新所有导入
2. `backend/main.py` - 更新导入
3. `services/agent.py` - 更新工具导入
4. `scripts/ingest.py` - 更新导入
5. 所有服务文件之间的相互导入

### 预计影响的文件数量

- 直接导入服务模块：~10个文件
- 服务模块之间的导入：~15个文件
- 总计：~25个文件需要更新

## 重构后的导入示例

### 之前
```python
from services.unified_llm_client import unified_llm_client
from services.retriever import retriever
from services.file_storage import file_storage
from services.config import settings
from services.logger import logger
```

### 之后
```python
from services import (
    unified_llm_client,
    retriever,
    file_storage,
    settings,
    logger
)

# 或使用新路径
from services.llm import unified_client
from services.vector import retriever
from services.storage import file_storage
from services.core import settings, logger
```

