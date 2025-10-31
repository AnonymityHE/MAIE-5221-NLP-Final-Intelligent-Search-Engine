"""
文件索引服务 - 将上传的文件向量化并添加到Milvus
"""
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.file_storage import file_storage
from services.file_processor import file_processor
from services.milvus_client import milvus_client
from services.config import settings
import json


class FileIndexer:
    """文件索引器 - 处理上传文件并索引到Milvus"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )
    
    def index_file(self, file_id: str) -> Dict:
        """
        处理并索引上传的文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            索引结果信息
        """
        # 1. 处理文件，提取文本
        print(f"开始处理文件: {file_id}")
        processed_result = file_processor.process_file(file_id)
        text = processed_result.get("text", "")
        metadata = processed_result.get("metadata", {})
        
        if not text.strip():
            return {
                "success": False,
                "message": "文件未包含可提取的文本内容",
                "chunks_indexed": 0
            }
        
        # 2. 切分文本
        chunks = self.text_splitter.split_text(text)
        
        if not chunks:
            return {
                "success": False,
                "message": "文本切分后为空",
                "chunks_indexed": 0
            }
        
        # 3. 获取文件信息
        file_info = file_storage.get_file(file_id)
        if not file_info:
            return {
                "success": False,
                "message": "文件信息不存在",
                "chunks_indexed": 0
            }
        
        # 4. 生成向量并插入Milvus
        data_to_insert = []
        for idx, chunk in enumerate(chunks):
            # 生成向量
            vector = milvus_client.get_embedding(chunk)
            
            # 准备数据
            # 将file_id和file_type信息添加到source_file中，便于识别和过滤
            source_file_str = f"{file_info['filename']}||file_id:{file_id}||file_type:{file_info['file_type']}"
            
            data_to_insert.append({
                "text": chunk,
                "vector": vector,
                "source_file": source_file_str,
                "file_id": file_id,  # 保留用于后续过滤
                "file_type": file_info['file_type']
            })
        
        # 批量插入
        try:
            milvus_client.insert_data(data_to_insert)
            
            # 标记文件为已处理
            file_storage.mark_as_processed(
                file_id,
                content_text=text[:10000],  # 只保存前10000字符作为摘要
                chunk_count=len(chunks)
            )
            
            return {
                "success": True,
                "message": "文件索引成功",
                "file_id": file_id,
                "filename": file_info['filename'],
                "chunks_indexed": len(chunks),
                "metadata": metadata
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"索引失败: {str(e)}",
                "chunks_indexed": 0
            }
    
    def search_uploaded_files(self, query: str, top_k: int = None, file_ids: List[str] = None) -> List[Dict]:
        """
        在上传的文件中搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            file_ids: 可选的特定文件ID列表
            
        Returns:
            搜索结果列表
        """
        top_k = top_k or settings.TOP_K
        
        # 搜索所有文档
        results = milvus_client.search(query, top_k=top_k * 2)  # 搜索更多结果以便过滤
        
        # 过滤出上传的文件
        uploaded_results = []
        for result in results:
            source_file = result.get('source_file', '')
            # 检查source_file是否包含file_id标记（格式：filename||file_id:xxx||file_type:xxx）
            if '||file_id:' in source_file:
                # 提取file_id
                parts = source_file.split('||')
                file_id = None
                for part in parts:
                    if part.startswith('file_id:'):
                        file_id = part.replace('file_id:', '')
                        break
                
                # 如果指定了file_ids，只返回匹配的文件
                if file_ids and file_id not in file_ids:
                    continue
                
                # 验证文件是否存在
                file_info = file_storage.get_file(file_id)
                if file_info:
                    # 恢复原始文件名
                    original_filename = source_file.split('||')[0]
                    result['source_file'] = original_filename
                    result['file_id'] = file_id
                    uploaded_results.append(result)
                    if len(uploaded_results) >= top_k:
                        break
        
        return uploaded_results[:top_k]


# 全局文件索引器实例
file_indexer = FileIndexer()

