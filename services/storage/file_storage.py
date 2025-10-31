"""
文件存储管理系统 - 处理用户上传的文件
实际文件存储在文件系统，元数据可通过Milvus或传统数据库管理
"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from threading import Lock
from services.core.config import settings
from services.core.logger import logger
from services.storage.backend import get_storage_backend

# 使用可切换的存储后端


class FileStorageManager:
    """文件存储管理器 - 文件存储在文件系统，元数据使用可切换的后端"""
    
    def __init__(self):
        # 创建存储目录
        self.storage_dir = Path(settings.UPLOAD_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化存储后端（支持Milvus或传统数据库）
        self.backend = get_storage_backend(
            backend_type=settings.STORAGE_BACKEND,
            database_url=settings.DATABASE_URL
        )
        
        # 简单的文件索引JSON（仅用于快速查询文件路径，不存储详细元数据）
        # 使用项目根目录
        project_root = Path(__file__).parent.parent.parent
        self.index_file = project_root / "file_index.json"  # 轻量级索引，只存储file_id -> file_path映射
        self.lock = Lock()
        
        self._init_index()
    
    def _init_index(self):
        """初始化文件索引"""
        if not self.index_file.exists():
            self._save_index({})
    
    def _load_index(self) -> Dict:
        """加载文件索引（仅存储file_id -> file_path的映射）"""
        if not self.index_file.exists():
            return {}
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载文件索引失败: {e}")
            return {}
    
    def _save_index(self, index: Dict):
        """保存文件索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存文件索引失败: {e}")
    
    def _generate_file_id(self, file_content: bytes, filename: str) -> str:
        """生成文件唯一ID"""
        hash_obj = hashlib.sha256(file_content)
        hash_obj.update(filename.encode())
        return hash_obj.hexdigest()
    
    def _get_file_type(self, filename: str) -> str:
        """根据文件扩展名判断文件类型"""
        ext = Path(filename).suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
            return 'image'
        elif ext in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs']:
            return 'code'
        else:
            return 'text'
    
    def save_file(self, file_content: bytes, filename: str, mime_type: Optional[str] = None) -> Dict:
        """
        保存上传的文件
        
        Args:
            file_content: 文件内容（字节）
            filename: 原始文件名
            mime_type: MIME类型
            
        Returns:
            包含文件信息的字典
        """
        # 验证文件大小
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"文件大小超过限制 {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB")
        
        # 验证文件扩展名
        ext = Path(filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {ext}。支持的类型: {settings.ALLOWED_EXTENSIONS}")
        
        # 生成文件ID和存储路径
        file_id = self._generate_file_id(file_content, filename)
        file_type = self._get_file_type(filename)
        stored_filename = f"{file_id}{ext}"
        file_path = self.storage_dir / stored_filename
        
        # 检查文件是否已存在（线程安全）
        with self.lock:
            index = self._load_index()
            
            if file_id in index:
                existing = index[file_id]
                # 检查是否已处理（从存储后端查询）
                existing_meta = self.backend.get_file_metadata(file_id)
                processed = existing_meta.get("processed", False) if existing_meta else False
                
                return {
                    "file_id": file_id,
                    "filename": existing.get("filename"),
                    "file_type": existing.get("file_type"),
                    "already_exists": True,
                    "processed": processed
                }
            
            # 保存文件到磁盘
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # 保存到文件索引（只存储基本映射）
            index = self._load_index()
            index_info = {
                "filename": filename,
                "stored_filename": stored_filename,
                "file_path": str(file_path),
                "file_type": file_type,
                "file_size": len(file_content),
                "mime_type": mime_type,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            index[file_id] = index_info
            self._save_index(index)
            
            # 保存到存储后端
            self.backend.save_file_metadata(file_id, {
                "filename": filename,
                "file_path": str(file_path),
                "file_type": file_type,
                "file_size": len(file_content),
                "mime_type": mime_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "processed": False
            })
            
            return {
                "file_id": file_id,
                "filename": filename,
                "file_type": file_type,
                "file_size": len(file_content),
                "stored_path": str(file_path),
                "already_exists": False,
                "processed": False
            }
    
    def get_file(self, file_id: str) -> Optional[Dict]:
        """获取文件信息（从存储后端查询，补充索引信息）"""
        # 从存储后端查询元数据
        metadata = self.backend.get_file_metadata(file_id)
        
        if metadata:
            # 补充文件路径等信息（从索引）
            index = self._load_index()
            index_info = index.get(file_id, {})
            metadata.update({
                "file_path": index_info.get("file_path", metadata.get("file_path")),
                "file_size": index_info.get("file_size", metadata.get("file_size")),
                "uploaded_at": index_info.get("uploaded_at", metadata.get("uploaded_at"))
            })
            return metadata
        
        # 如果后端中没有，从索引查询（未处理的文件）
        index = self._load_index()
        file_info = index.get(file_id)
        if file_info:
            return {
                "file_id": file_id,
                "filename": file_info.get("filename"),
                "file_type": file_info.get("file_type"),
                "file_size": file_info.get("file_size"),
                "file_path": file_info.get("file_path"),
                "uploaded_at": file_info.get("uploaded_at"),
                "processed": False,
                "chunk_count": 0
            }
        
        return None
    
    def list_files(self, file_type: Optional[str] = None, processed: Optional[bool] = None) -> List[Dict]:
        """列出所有文件（从存储后端查询，补充索引信息）"""
        # 从存储后端查询文件列表
        files = self.backend.list_files(file_type=file_type, processed=processed)
        
        # 补充文件路径等信息（从索引）
        index = self._load_index()
        for file_info in files:
            file_id = file_info.get("file_id")
            index_info = index.get(file_id, {})
            file_info.update({
                "file_path": index_info.get("file_path", file_info.get("file_path")),
                "file_size": index_info.get("file_size", file_info.get("file_size")),
                "uploaded_at": index_info.get("uploaded_at", file_info.get("uploaded_at"))
            })
        
        # 如果是database后端，可能还需要包含未处理的文件（在索引中但不在数据库中）
        if settings.STORAGE_BACKEND == "database":
            index = self._load_index()
            backend_file_ids = {f.get("file_id") for f in files}
            
            for file_id, file_info in index.items():
                if file_id not in backend_file_ids:
                    # 检查过滤条件
                    if file_type and file_info.get("file_type") != file_type:
                        continue
                    if processed is not None:
                        continue  # 未处理的文件，如果processed过滤器为None则包含
                    
                    files.append({
                        "file_id": file_id,
                        "filename": file_info.get("filename"),
                        "file_type": file_info.get("file_type"),
                        "file_size": file_info.get("file_size"),
                        "file_path": file_info.get("file_path"),
                        "uploaded_at": file_info.get("uploaded_at"),
                        "processed": False,
                        "chunk_count": 0
                    })
        
        return files
    
    def mark_as_processed(self, file_id: str, content_text: Optional[str] = None, chunk_count: int = 0):
        """标记文件为已处理（更新存储后端）"""
        from datetime import datetime
        
        updates = {
            "processed": True,
            "processed_at": datetime.utcnow().isoformat(),
            "chunk_count": chunk_count
        }
        
        if content_text:
            # 只保存前10000字符作为摘要
            updates["content_text"] = content_text[:10000] if len(content_text) > 10000 else content_text
        
        return self.backend.update_file_metadata(file_id, updates)
    
    def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        with self.lock:
            index = self._load_index()
            if file_id not in index:
                return False
            
            file_record = index[file_id]
            
            # 删除文件
            file_path = file_record.get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"删除文件失败: {e}")
            
            # 删除索引
            del index[file_id]
            self._save_index(index)
            
            # 删除存储后端的元数据
            self.backend.delete_file_metadata(file_id)
            
            return True


# 全局文件存储管理器实例
file_storage = FileStorageManager()

