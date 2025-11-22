#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片历史记录管理
维护会话级别的图片上下文，支持多轮对话
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from services.core import logger


class ImageHistoryManager:
    """
    图片历史记录管理器
    
    功能：
    1. 维护会话级别的图片历史
    2. 支持图片去重（基于哈希）
    3. 自动清理过期会话
    4. 持久化存储（可选）
    """
    
    def __init__(self, storage_dir: Optional[str] = None, max_images_per_session: int = 20):
        """
        初始化历史管理器
        
        Args:
            storage_dir: 存储目录（None则仅内存存储）
            max_images_per_session: 每个会话最多保存的图片数
        """
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self.max_images_per_session = max_images_per_session
        
        # 内存存储：{session_id: [ImageHistoryItem, ...]}
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        
        # 图片哈希索引：{hash: image_id}（用于去重）
        self.hash_index: Dict[str, str] = {}
        
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"图片历史存储目录: {self.storage_dir}")
        else:
            logger.info("图片历史仅内存存储")
    
    def create_session(self) -> str:
        """
        创建新会话
        
        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        logger.info(f"创建新会话: {session_id}")
        return session_id
    
    def add_image(
        self,
        session_id: str,
        image_data: str,
        image_hash: str,
        mime_type: str = "image/jpeg",
        description: Optional[str] = None,
        ocr_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加图片到会话历史
        
        Args:
            session_id: 会话ID
            image_data: Base64编码的图片数据
            image_hash: 图片哈希
            mime_type: MIME类型
            description: 图片描述
            ocr_text: OCR识别的文本
            
        Returns:
            图片历史项
        """
        # 检查会话是否存在
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # 检查是否重复（基于哈希）
        if image_hash in self.hash_index:
            existing_image_id = self.hash_index[image_hash]
            logger.info(f"图片已存在（哈希匹配）: {existing_image_id}")
            
            # 更新使用计数
            for item in self.sessions[session_id]:
                if item["image_id"] == existing_image_id:
                    item["query_count"] += 1
                    return item
        
        # 创建新图片项
        image_id = str(uuid.uuid4())
        image_item = {
            "image_id": image_id,
            "session_id": session_id,
            "image_data": image_data,  # 可选：如果太大可以不存储
            "image_hash": image_hash,
            "mime_type": mime_type,
            "description": description,
            "ocr_text": ocr_text,
            "created_at": datetime.now().isoformat(),
            "query_count": 1
        }
        
        # 添加到会话
        self.sessions[session_id].append(image_item)
        
        # 更新哈希索引
        self.hash_index[image_hash] = image_id
        
        # 限制会话图片数量
        if len(self.sessions[session_id]) > self.max_images_per_session:
            removed = self.sessions[session_id].pop(0)
            logger.info(f"会话图片数量超限，移除最旧的图片: {removed['image_id']}")
        
        logger.info(f"添加图片到会话 {session_id}: {image_id}")
        
        # 持久化
        if self.storage_dir:
            self._save_session(session_id)
        
        return image_item
    
    def get_session_images(
        self,
        session_id: str,
        include_data: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取会话的所有图片
        
        Args:
            session_id: 会话ID
            include_data: 是否包含图片数据（Base64）
            
        Returns:
            图片列表
        """
        if session_id not in self.sessions:
            logger.warning(f"会话不存在: {session_id}")
            return []
        
        images = self.sessions[session_id]
        
        if not include_data:
            # 移除图片数据以减少传输
            images = [
                {k: v for k, v in img.items() if k != 'image_data'}
                for img in images
            ]
        
        return images
    
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取图片
        
        Args:
            image_id: 图片ID
            
        Returns:
            图片项或None
        """
        for session_images in self.sessions.values():
            for image in session_images:
                if image["image_id"] == image_id:
                    return image
        return None
    
    def update_image_description(self, image_id: str, description: str) -> bool:
        """
        更新图片描述
        
        Args:
            image_id: 图片ID
            description: 新描述
            
        Returns:
            是否成功
        """
        for session_id, session_images in self.sessions.items():
            for image in session_images:
                if image["image_id"] == image_id:
                    image["description"] = description
                    
                    if self.storage_dir:
                        self._save_session(session_id)
                    
                    logger.info(f"更新图片描述: {image_id}")
                    return True
        return False
    
    def delete_image(self, image_id: str) -> bool:
        """
        删除图片
        
        Args:
            image_id: 图片ID
            
        Returns:
            是否成功
        """
        for session_id, session_images in self.sessions.items():
            for i, image in enumerate(session_images):
                if image["image_id"] == image_id:
                    # 移除图片
                    removed = session_images.pop(i)
                    
                    # 移除哈希索引
                    if removed["image_hash"] in self.hash_index:
                        del self.hash_index[removed["image_hash"]]
                    
                    if self.storage_dir:
                        self._save_session(session_id)
                    
                    logger.info(f"删除图片: {image_id}")
                    return True
        return False
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        if session_id in self.sessions:
            # 清除哈希索引
            for image in self.sessions[session_id]:
                if image["image_hash"] in self.hash_index:
                    del self.hash_index[image["image_hash"]]
            
            del self.sessions[session_id]
            
            # 删除持久化文件
            if self.storage_dir:
                session_file = self.storage_dir / f"{session_id}.json"
                if session_file.exists():
                    session_file.unlink()
            
            logger.info(f"清空会话: {session_id}")
            return True
        return False
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            统计信息
        """
        if session_id not in self.sessions:
            return {"error": "会话不存在"}
        
        images = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "total_images": len(images),
            "total_queries": sum(img["query_count"] for img in images),
            "oldest_image": images[0]["created_at"] if images else None,
            "newest_image": images[-1]["created_at"] if images else None,
            "has_ocr": sum(1 for img in images if img.get("ocr_text"))
        }
    
    def _save_session(self, session_id: str):
        """持久化会话数据"""
        if not self.storage_dir:
            return
        
        try:
            session_file = self.storage_dir / f"{session_id}.json"
            
            # 移除图片数据以减少文件大小
            session_data = [
                {k: v for k, v in img.items() if k != 'image_data'}
                for img in self.sessions[session_id]
            ]
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"会话已保存: {session_file}")
            
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
    
    def _load_session(self, session_id: str) -> bool:
        """从磁盘加载会话"""
        if not self.storage_dir:
            return False
        
        try:
            session_file = self.storage_dir / f"{session_id}.json"
            
            if not session_file.exists():
                return False
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.sessions[session_id] = session_data
            
            # 重建哈希索引
            for image in session_data:
                self.hash_index[image["image_hash"]] = image["image_id"]
            
            logger.info(f"会话已加载: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"加载会话失败: {e}")
            return False


# 全局单例
_image_history = None

def get_image_history() -> ImageHistoryManager:
    """获取图片历史管理器单例"""
    global _image_history
    if _image_history is None:
        # 使用项目下的data/image_history目录
        from pathlib import Path
        storage_dir = Path(__file__).parent.parent.parent / "data" / "image_history"
        _image_history = ImageHistoryManager(storage_dir=str(storage_dir))
    return _image_history

