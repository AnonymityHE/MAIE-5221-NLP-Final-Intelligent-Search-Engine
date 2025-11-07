# 故障排查指南

## 📋 目录
1. [Docker和Milvus问题](#docker和milvus问题)
2. [知识库索引问题](#知识库索引问题)
3. [流式语音交互问题](#流式语音交互问题)
4. [依赖和兼容性问题](#依赖和兼容性问题)
5. [API和服务问题](#api和服务问题)

---

## 🐳 Docker和Milvus问题

### 1. Docker Desktop 卡死

**症状**：Docker Desktop应用无响应，无法启动容器

**解决方案**：
```bash
# 强制退出Docker进程
killall Docker
killall com.docker.backend
killall com.docker.supervisor

# 然后重新启动Docker Desktop
```

### 2. Cannot connect to Docker daemon

**症状**：`Cannot connect to the Docker daemon at unix:///Users/anonymity/.docker/run/docker.sock`

**解决方案**：
1. 确保Docker Desktop正在运行
2. 等待Docker完全启动（状态栏显示"running"）
3. 检查Docker Desktop是否有错误提示

### 3. Milvus连接超时

**症状**：`Fail connecting to server on localhost:19530. Timeout`

**解决方案**：
```bash
# 检查Milvus容器是否运行
docker compose ps

# 查看Milvus日志
docker compose logs milvus-standalone

# 重启Milvus
docker compose restart

# 或完全重启
docker compose down
docker compose up -d
```

### 4. Docker Desktop启动慢

**可能原因**：
- 系统资源不足
- Docker Desktop首次启动
- 需要下载镜像

**解决方案**：
- 等待更长时间（首次启动可能需要5-10分钟）
- 检查系统资源使用情况
- 确保有足够的磁盘空间

### 验证Docker状态

```bash
# 检查Docker是否运行
docker ps

# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker compose version
```

### 重启Milvus

```bash
# 停止所有容器
docker compose down

# 启动所有容器
docker compose up -d

# 查看容器状态
docker compose ps

# 查看日志
docker compose logs
```

---

## 📚 知识库索引问题

### 1. 索引脚本失败

**症状**：运行 `index_fictional_kb.py` 时出错

**解决方案**：
1. **检查Milvus服务**：
   ```bash
   docker compose ps
   # 确保三个容器都在运行：milvus-standalone, milvus-etcd, milvus-minio
   ```

2. **等待Milvus完全启动**：
   ```bash
   # 启动后等待10-15秒
   sleep 15
   docker compose ps
   ```

3. **检查连接**：
   ```bash
   python -c "from services.vector.milvus_client import milvus_client; print('✅ 连接成功' if milvus_client.connect() else '❌ 连接失败')"
   ```

### 2. Channel Not Found错误

**症状**：`MilvusException: channel not found`

**原因**：Milvus集合状态异常

**解决方案**：
1. **删除并重建集合**（脚本会自动处理）：
   ```bash
   python scripts/utils/index_fictional_kb.py
   # 脚本会自动删除旧集合并重新创建
   ```

2. **手动重置集合**：
   ```python
   from pymilvus import utility
   from services.vector.milvus_client import milvus_client
   
   if utility.has_collection(milvus_client.collection_name):
       utility.drop_collection(milvus_client.collection_name)
   
   milvus_client.create_collection_if_not_exists(dimension=384)
   ```

3. **重启Milvus服务**：
   ```bash
   docker compose restart
   sleep 10
   ```

### 3. 索引数据量显示为0

**症状**：索引完成后，查询时显示数据量为0

**解决方案**：
1. **等待数据持久化**：Milvus会自动flush，等待5-10秒
2. **手动flush**（如果脚本失败）：
   ```python
   from pymilvus import Collection
   collection = Collection("knowledge_base")
   collection.flush()
   ```
3. **检查集合统计**：
   ```bash
   python -c "from services.vector.milvus_client import milvus_client; stats = milvus_client.get_collection_stats(); print(stats)"
   ```

### 4. 文档格式不支持

**症状**：某些文档无法索引

**解决方案**：
- **支持的格式**：PDF, TXT, MD, DOCX
- **检查文档**：确保文档没有损坏
- **查看错误日志**：检查具体的错误信息

---

## 🎤 流式语音交互问题

### 1. 流式STT未启用

**症状**：看不到实时转录

**检查**：
```bash
# 查看后端日志
# 应该看到：✅ 流式STT已启用
```

**解决方案**：
1. **检查配置**：
   ```bash
   # .env文件
   ENABLE_STREAMING_STT=true
   ```

2. **检查依赖**：
   ```bash
   pip install faster-whisper
   # 或（Mac用户）
   pip install lightning-whisper-mlx
   ```

3. **重启服务**：
   ```bash
   # 停止服务（Ctrl+C）
   # 重新启动
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 2. 流式TTS未启用

**症状**：没有实时语音播放

**检查**：
```bash
# 查看后端日志
# 应该看到：✅ 流式TTS已启用
```

**解决方案**：
1. **检查配置**：
   ```bash
   # .env文件
   ENABLE_STREAMING_TTS=true
   TTS_TYPE=parler  # 或 melo 或 edge
   ```

2. **检查依赖**：
   ```bash
   pip install parler-tts
   # 或
   pip install git+https://github.com/myshell-ai/MeloTTS.git
   ```

3. **检查前端**：确保浏览器支持Web Audio API

### 3. MLX优化未生效

**症状**：Mac用户但未使用MLX优化

**检查**：
```bash
# 查看后端日志
# 应该看到：✅ Lightning Whisper MLX加载成功
```

**解决方案**：
1. **检查配置**：
   ```bash
   # .env文件
   USE_MLX=true
   ```

2. **检查依赖**：
   ```bash
   pip install mlx lightning-whisper-mlx
   ```

3. **检查系统**：确保是Mac系统（MLX仅支持Mac）

### 4. 音频播放问题

**症状**：前端无法播放音频

**解决方案**：
1. **检查浏览器控制台**：查看是否有JavaScript错误
2. **检查WebSocket连接**：确保WebSocket已连接
3. **检查音频格式**：确保浏览器支持WAV格式
4. **尝试其他浏览器**：Chrome/Firefox/Safari

---

## 🔧 依赖和兼容性问题

### 1. Transformers版本冲突

**症状**：`ImportError: cannot import name 'is_torch_npu_available' from 'transformers'`

**解决方案**：
```bash
# 升级transformers版本
pip install transformers==4.46.1

# 系统已添加兼容性补丁（在services/__init__.py中）
```

### 2. MeloTTS安装失败

**症状**：`ERROR: Could not find a version that satisfies the requirement melo-tts`

**原因**：MeloTTS不是标准pip包

**解决方案**：
```bash
# 从GitHub安装
pip install git+https://github.com/myshell-ai/MeloTTS.git
```

### 3. MLX在非Mac系统上安装失败

**症状**：非Mac系统尝试安装MLX

**解决方案**：
- 在非Mac系统上不要启用 `USE_MLX=true`
- 系统会自动降级到标准实现

### 4. 依赖冲突

**症状**：多个包版本冲突

**解决方案**：
```bash
# 创建新的conda环境
conda create -n ise python=3.10
conda activate ise
pip install -r requirements.txt
```

---

## 🔌 API和服务问题

### 1. API密钥无效

**症状**：LLM API调用失败

**解决方案**：
- 检查密钥是否正确复制（前后空格）
- 检查API配额是否用完
- 验证API端点URL是否正确

### 2. 服务启动失败

**症状**：`uvicorn` 启动失败

**解决方案**：
```bash
# 检查端口是否被占用
lsof -i :8000

# 如果被占用，杀死进程
lsof -t -i :8000 | xargs kill -9

# 重新启动
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. WebSocket连接失败

**症状**：前端无法连接WebSocket

**解决方案**：
1. **检查服务是否运行**：`curl http://localhost:8000/api/health`
2. **检查WebSocket端点**：`ws://localhost:8000/api/voice/ws`
3. **检查防火墙**：确保端口8000未被阻止
4. **查看后端日志**：检查是否有错误信息

### 4. 查询无结果

**症状**：RAG查询返回空结果

**解决方案**：
1. **检查知识库是否已索引**：
   ```bash
   python -c "from services.vector.milvus_client import milvus_client; stats = milvus_client.get_collection_stats(); print(f'数据量: {stats[\"num_entities\"]}')"
   ```

2. **检查查询文本**：确保查询文本有意义
3. **检查相似度阈值**：可能需要调整相似度阈值
4. **重新索引**：如果数据量为0，重新运行索引脚本

---

## 📊 性能问题

### 1. 内存占用过高

**症状**：系统内存不足

**解决方案**：
- **使用Faster Whisper**：比标准Whisper占用更少内存（降低95%）
- **使用较小的模型**：`WHISPER_MODEL_SIZE=base` 或 `tiny`
- **使用Edge TTS**：无需加载模型，内存占用为0
- **启用MLX优化**（Mac用户）：使用量化模型降低内存

### 2. 响应速度慢

**症状**：查询响应时间过长

**解决方案**：
- **启用流式处理**：降低延迟
- **使用缓存**：查询结果会被缓存
- **优化模型大小**：使用较小的模型
- **检查网络**：API调用可能受网络影响

---

## 🔍 调试技巧

### 查看日志

```bash
# 查看应用日志
tail -f logs/rag_system.log

# 查看Docker日志
docker compose logs -f

# 查看Milvus日志
docker compose logs milvus-standalone
```

### 测试连接

```bash
# 测试Milvus连接
python -c "from services.vector.milvus_client import milvus_client; print('✅' if milvus_client.connect() else '❌')"

# 测试API健康
curl http://localhost:8000/api/health

# 测试RAG查询
curl -X POST "http://localhost:8000/api/rag_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

### 检查配置

```bash
# 查看所有配置
python -c "from services.core.config import settings; import json; print(json.dumps({k:v for k,v in vars(settings).items() if not k.startswith('_')}, indent=2, default=str))"
```

---

## 📞 获取更多帮助

- 查看完整文档：`docs/README.md`
- 用户指南：`docs/USER_GUIDE.md`
- 安装指南：`docs/SETUP_GUIDE.md`
- 项目信息：`docs/PROJECT_INFO.md`

