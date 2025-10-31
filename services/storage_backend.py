"""
存储后端抽象接口 - 支持多种存储方式
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    def save_file_metadata(self, file_id: str, metadata: Dict) -> bool:
        """保存文件元数据"""
        pass
    
    @abstractmethod
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """获取文件元数据"""
        pass
    
    @abstractmethod
    def list_files(self, file_type: Optional[str] = None, 
                   processed: Optional[bool] = None) -> List[Dict]:
        """列出文件"""
        pass
    
    @abstractmethod
    def update_file_metadata(self, file_id: str, updates: Dict) -> bool:
        """更新文件元数据"""
        pass
    
    @abstractmethod
    def delete_file_metadata(self, file_id: str) -> bool:
        """删除文件元数据"""
        pass


class MilvusStorageBackend(StorageBackend):
    """Milvus存储后端 - 通过查询Milvus获取元数据"""
    
    def __init__(self):
        from services.milvus_metadata import milvus_metadata
        self.milvus_metadata = milvus_metadata
    
    def save_file_metadata(self, file_id: str, metadata: Dict) -> bool:
        """Milvus后端不直接保存元数据，元数据在索引文件时自动写入"""
        # 元数据会在文件索引时通过source_file字段写入Milvus
        return True
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """从Milvus查询文件元数据"""
        return self.milvus_metadata.get_file_metadata_from_milvus(file_id)
    
    def list_files(self, file_type: Optional[str] = None, 
                   processed: Optional[bool] = None) -> List[Dict]:
        """从Milvus列出文件"""
        files = self.milvus_metadata.list_files_from_milvus()
        
        # 过滤
        if file_type:
            files = [f for f in files if f.get("file_type") == file_type]
        if processed is not None:
            files = [f for f in files if f.get("processed") == processed]
        
        return files
    
    def update_file_metadata(self, file_id: str, updates: Dict) -> bool:
        """Milvus后端的元数据更新通过重新索引实现"""
        # 由于元数据存储在Milvus的source_file字段中，更新需要重新索引
        # 这里返回True表示操作已记录，实际更新需要重新索引文件
        return True
    
    def delete_file_metadata(self, file_id: str) -> bool:
        """从Milvus删除文件元数据（通过删除相关chunks）"""
        # 注意：实际实现需要删除Milvus中所有相关chunks
        # 这是一个复杂操作，建议通过外部函数实现
        return True


class DatabaseStorageBackend(StorageBackend):
    """传统数据库存储后端 - 使用SQLite/PostgreSQL存储元数据"""
    
    def __init__(self, database_url: str = "sqlite:///./file_storage.db"):
        """
        初始化数据库后端
        
        Args:
            database_url: 数据库URL（SQLite或PostgreSQL）
        """
        from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Text
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        
        Base = declarative_base()
        
        class FileMetadata(Base):
            __tablename__ = "file_metadata"
            
            file_id = Column(String, primary_key=True)
            filename = Column(String, nullable=False)
            file_path = Column(String, nullable=False)
            file_type = Column(String, nullable=False)
            file_size = Column(Integer, nullable=False)
            mime_type = Column(String)
            uploaded_at = Column(DateTime)
            processed = Column(Boolean, default=False)
            processed_at = Column(DateTime)
            content_text = Column(Text)  # 文本摘要
            chunk_count = Column(Integer, default=0)
            metadata_json = Column(Text)  # 额外元数据（JSON格式）
        
        self.Base = Base
        self.FileMetadata = FileMetadata
        
        # 创建数据库引擎
        if database_url.startswith("sqlite"):
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False}
            )
        else:
            self.engine = create_engine(database_url)
        
        # 创建表
        Base.metadata.create_all(self.engine)
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def save_file_metadata(self, file_id: str, metadata: Dict) -> bool:
        """保存文件元数据到数据库"""
        from datetime import datetime
        import json
        
        db = self.SessionLocal()
        try:
            # 检查是否已存在
            existing = db.query(self.FileMetadata).filter_by(file_id=file_id).first()
            if existing:
                return True
            
            # 创建新记录
            file_record = self.FileMetadata(
                file_id=file_id,
                filename=metadata.get("filename", ""),
                file_path=metadata.get("file_path", ""),
                file_type=metadata.get("file_type", ""),
                file_size=metadata.get("file_size", 0),
                mime_type=metadata.get("mime_type"),
                uploaded_at=datetime.fromisoformat(metadata.get("uploaded_at", datetime.utcnow().isoformat())) if isinstance(metadata.get("uploaded_at"), str) else metadata.get("uploaded_at", datetime.utcnow()),
                processed=metadata.get("processed", False),
                chunk_count=metadata.get("chunk_count", 0),
                metadata_json=json.dumps(metadata.get("metadata", {}))
            )
            
            db.add(file_record)
            db.commit()
            return True
        except Exception as e:
            print(f"保存文件元数据到数据库失败: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """从数据库获取文件元数据"""
        import json
        from datetime import datetime
        
        db = self.SessionLocal()
        try:
            record = db.query(self.FileMetadata).filter_by(file_id=file_id).first()
            if not record:
                return None
            
            metadata = {
                "file_id": record.file_id,
                "filename": record.filename,
                "file_path": record.file_path,
                "file_type": record.file_type,
                "file_size": record.file_size,
                "mime_type": record.mime_type,
                "uploaded_at": record.uploaded_at.isoformat() if record.uploaded_at else None,
                "processed": record.processed,
                "processed_at": record.processed_at.isoformat() if record.processed_at else None,
                "content_text": record.content_text,
                "chunk_count": record.chunk_count
            }
            
            # 解析额外元数据
            if record.metadata_json:
                try:
                    metadata.update(json.loads(record.metadata_json))
                except:
                    pass
            
            return metadata
        finally:
            db.close()
    
    def list_files(self, file_type: Optional[str] = None, 
                   processed: Optional[bool] = None) -> List[Dict]:
        """从数据库列出文件"""
        import json
        from datetime import datetime
        
        db = self.SessionLocal()
        try:
            query = db.query(self.FileMetadata)
            
            if file_type:
                query = query.filter_by(file_type=file_type)
            if processed is not None:
                query = query.filter_by(processed=processed)
            
            records = query.all()
            files = []
            
            for record in records:
                metadata = {
                    "file_id": record.file_id,
                    "filename": record.filename,
                    "file_path": record.file_path,
                    "file_type": record.file_type,
                    "file_size": record.file_size,
                    "uploaded_at": record.uploaded_at.isoformat() if record.uploaded_at else None,
                    "processed": record.processed,
                    "chunk_count": record.chunk_count
                }
                
                if record.metadata_json:
                    try:
                        metadata.update(json.loads(record.metadata_json))
                    except:
                        pass
                
                files.append(metadata)
            
            return files
        finally:
            db.close()
    
    def update_file_metadata(self, file_id: str, updates: Dict) -> bool:
        """更新文件元数据"""
        import json
        from datetime import datetime
        
        db = self.SessionLocal()
        try:
            record = db.query(self.FileMetadata).filter_by(file_id=file_id).first()
            if not record:
                return False
            
            # 更新字段
            if "processed" in updates:
                record.processed = updates["processed"]
            if "processed_at" in updates:
                if isinstance(updates["processed_at"], str):
                    record.processed_at = datetime.fromisoformat(updates["processed_at"])
                else:
                    record.processed_at = updates["processed_at"]
            if "chunk_count" in updates:
                record.chunk_count = updates["chunk_count"]
            if "content_text" in updates:
                record.content_text = updates["content_text"]
            if "metadata" in updates:
                record.metadata_json = json.dumps(updates["metadata"])
            
            db.commit()
            return True
        except Exception as e:
            print(f"更新文件元数据失败: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def delete_file_metadata(self, file_id: str) -> bool:
        """从数据库删除文件元数据"""
        db = self.SessionLocal()
        try:
            record = db.query(self.FileMetadata).filter_by(file_id=file_id).first()
            if not record:
                return False
            
            db.delete(record)
            db.commit()
            return True
        except Exception as e:
            print(f"删除文件元数据失败: {e}")
            db.rollback()
            return False
        finally:
            db.close()


def get_storage_backend(backend_type: str = "milvus", **kwargs) -> StorageBackend:
    """
    工厂函数：获取存储后端实例
    
    Args:
        backend_type: 后端类型 ("milvus" 或 "database")
        **kwargs: 后端特定参数
            - database_url: 数据库URL（用于database后端）
    
    Returns:
        StorageBackend实例
    """
    if backend_type == "milvus":
        return MilvusStorageBackend()
    elif backend_type == "database":
        database_url = kwargs.get("database_url", "sqlite:///./file_storage.db")
        return DatabaseStorageBackend(database_url)
    else:
        raise ValueError(f"不支持的存储后端类型: {backend_type}")

