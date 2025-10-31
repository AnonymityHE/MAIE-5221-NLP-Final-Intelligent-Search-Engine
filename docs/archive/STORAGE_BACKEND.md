# 存储后端说明

系统支持两种文件元数据存储后端，可以在配置中切换。

## 两种存储后端

### 1. Milvus后端（默认）

**配置**：
```python
STORAGE_BACKEND = "milvus"
```

**工作原理**：
- 文件元数据通过查询Milvus的`source_file`字段获取
- 文件索引到Milvus时，元数据自动写入`source_file`字段
- 格式：`"filename||file_id:xxx||file_type:xxx"`

**优势**：
- 无需额外数据库服务
- 所有数据（向量、文本、元数据）统一管理
- 适合小到中等规模应用

**劣势**：
- 元数据查询依赖Milvus查询
- 不支持复杂的SQL过滤和聚合操作

### 2. 传统数据库后端

**配置**：
```python
STORAGE_BACKEND = "database"
DATABASE_URL = "sqlite:///./file_storage.db"  # SQLite
# 或
DATABASE_URL = "postgresql://user:password@localhost/dbname"  # PostgreSQL
```

**工作原理**：
- 文件元数据存储在独立的数据库表中
- 表结构：`file_metadata`
- 支持的数据库：SQLite（默认）、PostgreSQL

**优势**：
- 支持标准SQL查询
- 支持复杂过滤和聚合
- 更好的并发性能（PostgreSQL）
- 适合大规模数据管理
- 可以轻松扩展和迁移

**劣势**：
- 需要额外的数据库服务（如果使用PostgreSQL）
- 需要额外的存储空间

## 切换存储后端

在 `services/config.py` 中修改：

```python
# 使用Milvus后端（默认）
STORAGE_BACKEND = "milvus"

# 或使用传统数据库后端
STORAGE_BACKEND = "database"
DATABASE_URL = "sqlite:///./file_storage.db"  # SQLite
# DATABASE_URL = "postgresql://user:password@localhost/dbname"  # PostgreSQL
```

## 数据库表结构（database后端）

如果使用`database`后端，会自动创建以下表：

```sql
CREATE TABLE file_metadata (
    file_id VARCHAR PRIMARY KEY,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR,
    uploaded_at DATETIME,
    processed BOOLEAN DEFAULT FALSE,
    processed_at DATETIME,
    content_text TEXT,
    chunk_count INTEGER DEFAULT 0,
    metadata_json TEXT  -- 额外元数据（JSON格式）
);
```

## 使用建议

- **开发/测试环境**：使用`milvus`后端（简单，无需额外数据库）
- **生产环境（小规模）**：使用`milvus`后端或SQLite
- **生产环境（大规模）**：使用PostgreSQL后端，获得更好的性能和扩展性

## API兼容性

无论使用哪种后端，API接口完全相同，无需修改业务代码。所有操作通过`StorageBackend`抽象接口统一管理。

