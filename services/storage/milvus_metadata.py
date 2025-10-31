"""
Milvus元数据管理 - 使用Milvus存储文件元数据
利用Milvus的查询能力来存储和检索文件元数据
"""
from typing import Optional, Dict, List
from services.vector.milvus_client import milvus_client
from services.core.config import settings
from services.core.logger import logger


class MilvusMetadataManager:
    """使用Milvus存储文件元数据的管理器"""
    
    def __init__(self):
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.metadata_collection = f"{self.collection_name}_metadata"  # 文件元数据专用collection
        self._ensure_metadata_collection()
    
    def _ensure_metadata_collection(self):
        """确保元数据collection存在"""
        if not milvus_client.connected:
            milvus_client.connect()
        
        from pymilvus import Collection, utility, CollectionSchema, FieldSchema, DataType
        
        # 检查是否存在专门的元数据collection
        # 如果没有，文件元数据将通过文件ID在main collection中查询
        # 这种方式更简单，直接利用现有collection
    
    def get_file_metadata_from_milvus(self, file_id: str) -> Optional[Dict]:
        """
        从Milvus中查询文件元数据（通过搜索该file_id的任意chunk）
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件元数据字典
        """
        if not milvus_client.connected:
            milvus_client.connect()
        
        try:
            from pymilvus import Collection
            
            collection = Collection(self.collection_name)
            collection.load()
            
            # 查询包含该file_id的文档（使用表达式查询）
            # 注意：需要确保source_file字段包含file_id信息
            expr = f'source_file like "%file_id:{file_id}%"'
            
            results = collection.query(
                expr=expr,
                output_fields=["source_file"],
                limit=1  # 只需要一个结果来提取元数据
            )
            
            if results:
                source_file = results[0].get("source_file", "")
                # 解析source_file字符串提取元数据
                # 格式: "filename||file_id:xxx||file_type:xxx"
                if "||file_id:" in source_file:
                    parts = source_file.split("||")
                    filename = parts[0]
                    file_id_from_source = None
                    file_type = None
                    
                    for part in parts[1:]:
                        if part.startswith("file_id:"):
                            file_id_from_source = part.replace("file_id:", "")
                        elif part.startswith("file_type:"):
                            file_type = part.replace("file_type:", "")
                    
                    # 统计该文件有多少chunks
                    all_results = collection.query(
                        expr=expr,
                        output_fields=["source_file"],
                        limit=10000  # 获取所有chunks
                    )
                    
                    return {
                        "file_id": file_id_from_source,
                        "filename": filename,
                        "file_type": file_type,
                        "chunk_count": len(all_results),
                        "processed": True  # 如果能在Milvus中找到，说明已处理
                    }
            
            return None
        except Exception as e:
            logger.error(f"从Milvus查询文件元数据失败: {e}")
            return None
    
    def list_files_from_milvus(self) -> List[Dict]:
        """
        从Milvus列出所有已索引的文件
        
        Returns:
            文件列表
        """
        if not milvus_client.connected:
            milvus_client.connect()
        
        try:
            from pymilvus import Collection
            
            collection = Collection(self.collection_name)
            collection.load()
            
            # 获取所有unique的source_file（包含file_id的）
            # 使用迭代器获取所有数据，然后去重
            results = collection.query(
                expr='source_file like "%||file_id:%"',
                output_fields=["source_file"],
                limit=10000
            )
            
            # 提取唯一的文件
            seen_files = {}
            for result in results:
                source_file = result.get("source_file", "")
                if "||file_id:" in source_file:
                    parts = source_file.split("||")
                    filename = parts[0]
                    file_id = None
                    file_type = None
                    
                    for part in parts[1:]:
                        if part.startswith("file_id:"):
                            file_id = part.replace("file_id:", "")
                        elif part.startswith("file_type:"):
                            file_type = part.replace("file_type:", "")
                    
                    if file_id and file_id not in seen_files:
                        # 统计chunks
                        expr = f'source_file like "%file_id:{file_id}%"'
                        chunks = collection.query(expr=expr, limit=10000)
                        
                        seen_files[file_id] = {
                            "file_id": file_id,
                            "filename": filename,
                            "file_type": file_type,
                            "chunk_count": len(chunks),
                            "processed": True
                        }
            
            return list(seen_files.values())
        except Exception as e:
            logger.error(f"从Milvus列出文件失败: {e}")
            return []


# 全局元数据管理器实例
milvus_metadata = MilvusMetadataManager()

