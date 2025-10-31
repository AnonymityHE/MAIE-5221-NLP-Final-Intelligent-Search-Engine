"""
Reranker模块 - 使用交叉编码器进行二次排序，提升检索结果相关性
"""
from typing import List, Dict
from services.core.logger import logger

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    logger.warning("sentence-transformers未安装CrossEncoder，Reranker功能将被禁用")


class Reranker:
    """交叉编码器重排序器"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        初始化Reranker
        
        Args:
            model_name: 交叉编码器模型名称
                - cross-encoder/ms-marco-MiniLM-L-6-v2 (推荐，速度快)
                - cross-encoder/ms-marco-MiniLM-L-12-v2 (更准确但更慢)
        """
        self.model = None
        self.model_name = model_name
        
        if CROSS_ENCODER_AVAILABLE:
            try:
                logger.info(f"正在加载Reranker模型: {model_name}")
                self.model = CrossEncoder(model_name)
                logger.info("Reranker模型加载完成")
            except Exception as e:
                logger.error(f"加载Reranker模型失败: {e}")
                self.model = None
        else:
            logger.warning("Reranker功能未启用，因为sentence-transformers未正确安装")
    
    def rerank(self, query: str, documents: List[Dict], top_k: int = None) -> List[Dict]:
        """
        对检索结果进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表，每个文档包含 'text', 'source_file', 'score' 等字段
            top_k: 返回top_k个最相关的结果，如果为None则返回所有
            
        Returns:
            重排序后的文档列表
        """
        if not self.model:
            logger.warning("Reranker模型未加载，返回原始排序结果")
            return documents[:top_k] if top_k else documents
        
        if not documents:
            return []
        
        try:
            # 准备输入对 (query, document_text)
            pairs = [(query, doc.get('text', '')) for doc in documents]
            
            # 使用交叉编码器计算相关性分数（分数越高越相关）
            scores = self.model.predict(pairs)
            
            # 将分数添加到文档中并排序
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
                # 保留原始向量检索分数，用于对比
                doc['original_score'] = doc.get('score', 0.0)
            
            # 按重排序分数降序排序（分数越高越相关）
            reranked = sorted(documents, key=lambda x: x.get('rerank_score', 0), reverse=True)
            
            # 返回top_k个结果
            if top_k:
                reranked = reranked[:top_k]
            
            logger.info(f"Reranker重排序完成: {len(documents)} -> {len(reranked)} 个文档")
            return reranked
            
        except Exception as e:
            logger.error(f"Reranker重排序失败: {e}，返回原始排序结果")
            return documents[:top_k] if top_k else documents
    
    def is_available(self) -> bool:
        """检查Reranker是否可用"""
        return self.model is not None


# 全局Reranker实例
reranker = Reranker()

