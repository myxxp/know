from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class KnowledgeItem(Base):
    """知识库项目模型"""
    __tablename__ = "knowledge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="标题")
    content = Column(Text, comment="内容")
    source_type = Column(String(50), nullable=False, comment="数据源类型")
    source_id = Column(String(100), comment="数据源ID")
    file_path = Column(String(500), comment="文件路径")
    metadata = Column(Text, comment="元数据JSON")
    is_processed = Column(Boolean, default=False, comment="是否已处理")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<KnowledgeItem(id={self.id}, title='{self.title}')>"
