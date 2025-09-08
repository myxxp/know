from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.model.database import KnowledgeItem
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
    
    