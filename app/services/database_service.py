from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.model.datebase import KnowledgeItem
from app.core.database import get_db_session
from loguru import logger


class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        self.logger = logger
    
    def query_data(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行自定义SQL查询"""
        try:
            with get_db_session() as db:
                result = db.execute(text(query), params or {})
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            self.logger.error(f"数据库查询失败: {e}")
            raise
    
    def get_knowledge_items(self, limit: int = 100, offset: int = 0, 
                           is_processed: Optional[bool] = None) -> List[KnowledgeItem]:
        """获取知识库项目"""
        try:
            with get_db_session() as db:
                query = db.query(KnowledgeItem)
                if is_processed is not None:
                    query = query.filter(KnowledgeItem.is_processed == is_processed)
                return query.offset(offset).limit(limit).all()
        except Exception as e:
            self.logger.error(f"获取知识库项目失败: {e}")
            raise
    
    def create_knowledge_item(self, title: str, content: str, source_type: str,
                            source_id: Optional[str] = None, file_path: Optional[str] = None,
                            metadata: Optional[str] = None) -> KnowledgeItem:
        """创建知识库项目"""
        try:
            with get_db_session() as db:
                item = KnowledgeItem(
                    title=title,
                    content=content,
                    source_type=source_type,
                    source_id=source_id,
                    file_path=file_path,
                    metadata=metadata
                )
                db.add(item)
                db.flush()
                db.refresh(item)
                return item
        except Exception as e:
            self.logger.error(f"创建知识库项目失败: {e}")
            raise
    
    def update_knowledge_item(self, item_id: int, **kwargs) -> Optional[KnowledgeItem]:
        """更新知识库项目"""
        try:
            with get_db_session() as db:
                item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
                if item:
                    for key, value in kwargs.items():
                        if hasattr(item, key):
                            setattr(item, key, value)
                    db.flush()
                    db.refresh(item)
                return item
        except Exception as e:
            self.logger.error(f"更新知识库项目失败: {e}")
            raise
    
    def mark_as_processed(self, item_id: int) -> bool:
        """标记项目为已处理"""
        try:
            with get_db_session() as db:
                item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
                if item:
                    item.is_processed = True
                    db.flush()
                    return True
                return False
        except Exception as e:
            self.logger.error(f"标记项目为已处理失败: {e}")
            raise
