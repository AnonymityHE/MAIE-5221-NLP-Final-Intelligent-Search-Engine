"""
Milvus客户端 - 封装Milvus连接和操作
"""
from pymilvus import connections, Collection, utility
from typing import List, Dict, Optional
from services.core.config import settings
from services.core.logger import logger
from sentence_transformers import SentenceTransformer


class MilvusClient:
    """Milvus客户端封装类"""
    
    def __init__(self):
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.connected = False
        # 加载embedding模型（延迟加载）
        self._embedding_model = None
        
    def connect(self) -> bool:
        """连接到Milvus服务器"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"连接Milvus失败: {e}")
            return False
    
    def disconnect(self):
        """断开Milvus连接"""
        if self.connected:
            connections.disconnect("default")
            self.connected = False
    
    def create_collection_if_not_exists(self, dimension: int = 384):
        """
        如果集合不存在则创建集合
        
        Args:
            dimension: 向量维度
        """
        if not self.connected:
            self.connect()
        
        # 检查集合是否存在
        if utility.has_collection(self.collection_name):
            logger.info(f"集合 {self.collection_name} 已存在")
            return
        
        # 定义集合schema
        from pymilvus import CollectionSchema, FieldSchema, DataType
        
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="source_file", dtype=DataType.VARCHAR, max_length=500),
        ]
        
        schema = CollectionSchema(fields, "知识库集合")
        
        # 创建集合
        collection = Collection(self.collection_name, schema)
        
        # 创建索引
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(
            field_name="vector",
            index_params=index_params
        )
        
        logger.info(f"集合 {self.collection_name} 创建成功")
    
    def insert(self, texts: List[str], vectors: List[List[float]], 
               source_files: List[str]) -> bool:
        """
        批量插入数据到Milvus
        
        Args:
            texts: 文本列表
            vectors: 向量列表
            source_files: 源文件列表
            
        Returns:
            是否插入成功
        """
        if not self.connected:
            self.connect()
        
        try:
            collection = Collection(self.collection_name)
            collection.load()
            
            data = [
                texts,
                vectors,
                source_files
            ]
            
            collection.insert(data)
            collection.flush()
            logger.info(f"成功插入 {len(texts)} 条数据")
            return True
        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            return False
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        向量搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回最相似的k个结果
            
        Returns:
            搜索结果列表，每个结果包含text、source_file和score
        """
        if not self.connected:
            self.connect()
        
        try:
            collection = Collection(self.collection_name)
            collection.load()
            
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                output_fields=["text", "source_file"]
            )
            
            # 格式化结果
            formatted_results = []
            for hits in results:
                for hit in hits:
                    formatted_results.append({
                        "text": hit.entity.get("text"),
                        "source_file": hit.entity.get("source_file"),
                        "score": hit.score
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表
        """
        if self._embedding_model is None:
            logger.info(f"正在加载embedding模型: {settings.EMBEDDING_MODEL}")
            self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        vector = self._embedding_model.encode([text])[0].tolist()
        return vector
    
    def insert_data(self, data_list: List[Dict]):
        """
        插入数据到Milvus（支持灵活的字段）
        
        Args:
            data_list: 数据列表，每个元素包含vector和其他字段
        """
        if not self.connected:
            self.connect()
        
        try:
            collection = Collection(self.collection_name)
            collection.load()
            
            # 提取字段
            texts = [item.get("text", "") for item in data_list]
            vectors = [item.get("vector", []) for item in data_list]
            source_files = [item.get("source_file", "unknown") for item in data_list]
            file_ids = [item.get("file_id", "") for item in data_list]
            file_types = [item.get("file_type", "") for item in data_list]
            
            # 检查集合schema是否需要更新（添加file_id和file_type字段）
            # 注意：如果schema已更改，需要重新创建collection
            # 这里使用简单的插入方法，file_id和file_type作为source_file的一部分
            
            # 构建数据（兼容现有schema）
            data = [
                texts,
                vectors,
                source_files
            ]
            
            collection.insert(data)
            collection.flush()
            logger.info(f"成功插入 {len(texts)} 条数据")
        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        搜索（支持文本查询和向量查询）
        
        Args:
            query: 查询文本或向量
            top_k: 返回数量
        """
        # 如果query是文本，先转换为向量
        if isinstance(query, str):
            query_vector = self.get_embedding(query)
        else:
            query_vector = query
        
        return self.search_vectors(query_vector, top_k)
    
    def search_vectors(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        向量搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回最相似的k个结果
            
        Returns:
            搜索结果列表
        """
        if not self.connected:
            self.connect()
        
        try:
            collection = Collection(self.collection_name)
            collection.load()
            
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                output_fields=["text", "source_file"]
            )
            
            # 格式化结果
            formatted_results = []
            for hits in results:
                for hit in hits:
                    formatted_results.append({
                        "text": hit.entity.get("text"),
                        "source_file": hit.entity.get("source_file"),
                        "score": hit.score
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_collection_stats(self) -> Optional[Dict]:
        """获取集合统计信息"""
        if not self.connected:
            self.connect()
        
        try:
            collection = Collection(self.collection_name)
            collection.load()
            num_entities = collection.num_entities
            return {
                "collection_name": self.collection_name,
                "num_entities": num_entities
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return None


# 全局Milvus客户端实例
milvus_client = MilvusClient()

