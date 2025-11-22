# 知识库Q&A测试结果

测试日期: 2025-11-17
总问题数: 9
成功: 9
失败: 0

---

## 问题 1: 系统使用

**问题**: 如何使用粤语进行语音输入？

**答案**: [见测试输出]

**响应时间**: 11.67秒

**使用工具**: local_rag

**检索上下文**: 1个

**答案质量**: 良好

---

## 问题 2: 技术架构

**问题**: 系统采用了什么样的工作流架构？LLM在其中起什么作用？

**答案**: [见测试输出]

**响应时间**: 13.42秒

**使用工具**: workflow:local_rag:检索工作流架构信息, workflow:local_rag:检索LLM在系统中的角色

**检索上下文**: 2个

**答案质量**: 良好

---

## 问题 3: 功能查询

**问题**: What tools are available in this system and what can they do?

**答案**: [见测试输出]

**响应时间**: 9.30秒

**使用工具**: local_rag

**检索上下文**: 1个

**答案质量**: 一般

---

## 问题 4: 技术细节

**问题**: What is reranking and why is it important in RAG systems?

**答案**: [见测试输出]

**响应时间**: 18.72秒

**使用工具**: llm_workflow_failed

**检索上下文**: 3个

**答案质量**: 良好

---

## 问题 5: 多语言支持

**问题**: 这个系统支持哪些语言？分别在哪些方面支持？

**答案**: [见测试输出]

**响应时间**: 13.93秒

**使用工具**: workflow:local_rag:检索系统支持的语言列表, workflow:local_rag:检索每种语言的支持详情

**检索上下文**: 2个

**答案质量**: 优秀

---

## 问题 6: API对比

**问题**: What's the difference between HKGAI and Gemini APIs? When does the system use each one?

**答案**: [见测试输出]

**响应时间**: 17.63秒

**使用工具**: workflow:local_rag:Retrieve information about HKGAI API, workflow:local_rag:Retrieve information about Gemini API, workflow:web_search:Search for additional information about HKGAI API

**检索上下文**: 3个

**答案质量**: 一般

---

## 问题 7: 知识库管理

**问题**: 我想添加新文档到知识库，有什么方法？

**答案**: [见测试输出]

**响应时间**: 12.74秒

**使用工具**: local_rag

**检索上下文**: 1个

**答案质量**: 一般

---

## 问题 8: RAG优化

**问题**: RAG系统中的chunking策略有哪些最佳实践？

**答案**: [见测试输出]

**响应时间**: 16.44秒

**使用工具**: workflow:local_rag:检索本地知识库, workflow:web_search:搜索互联网

**检索上下文**: 2个

**答案质量**: 一般

---

## 问题 9: 故障排查

**问题**: 如果Milvus连接失败应该怎么办？

**答案**: [见测试输出]

**响应时间**: 15.70秒

**使用工具**: local_rag

**检索上下文**: 1个

**答案质量**: 良好

---

