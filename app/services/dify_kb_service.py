"""
Dify 知识库服务

"""

import os
from loguru import logger
from app.dify.dify_knowledge_base import DifyKnowledgeBase
from app.utils.utils import save_doc_id

class DifyKnowledgeBaseService:

    def __init__(self, dify: DifyKnowledgeBase):
        self.dify = dify
        self.logger = logger

    async def get_dataset_id_by_name(self, name: str) -> str:
        """
        根据名称获取知识库 ID
        """
        datasets = await self.dify.list_datasets()
        for dataset in datasets:
            if dataset["name"] == name:
                return dataset["id"]
        return None

    async def create_dataset_metadata(self, dataset_id: str, metadata: dict):
        """
        创建知识库元数据
        
        Args:
            dataset_id: 知识库 ID
            metadata: 元数据
        """
        result = []
        try:
            for k, _ in metadata.items():
                _metadata = {"type": "string", "name": k} if k != "published_time" else {"type":"time","name":k}
                res = await self.dify.add_dataset_metadata(dataset_id, _metadata)
                result.append(res)
            return result
        except Exception as e:
            self.logger.error(f"创建知识库元数据失败: {e}")
            raise

    async def create_document_by_file_save_doc_id(self, dataset_id: str, file_path: str):
        """
        创建文档并保存文档 ID
        """
        file_name = os.path.basename(file_path)
        res = await self.dify.create_document_by_file(dataset_id, file_path)
        save_doc_id(file_name, res.get("document", {}).get("id"))
        return res

    
             
        
        
        