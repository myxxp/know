import httpx
import os
from typing import Dict, Any, Optional, List
from app.config import settings
from loguru import logger


class DifyClient:
    """Dify API客户端 - 按照官方API文档结构组织"""
    
    def __init__(self):
        self.logger = logger
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _call_api(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                       files: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调用Dify API的通用方法"""
        try:
            url = f"{settings.dify_base_url}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {settings.dify_api_key}",
            }
            
            if files:
                # 文件上传请求
                response = await self.client.request(method, url, data=data, files=files, headers=headers, params=params)
            else:
                # JSON请求
                headers["Content-Type"] = "application/json"
                response = await self.client.request(method, url, json=data, headers=headers, params=params)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Dify API调用失败: {e}")
            raise
    
    # ==================== Datasets API ====================
    
    async def create_dataset(self, name: str, description: str = "", 
                           permission: str = "only_me") -> Dict[str, Any]:
        """创建数据集"""
        data = {
            "name": name,
            "description": description,
            "permission": permission
        }
        return await self._call_api("POST", "datasets", data)
    
    async def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """获取数据集信息"""
        return await self._call_api("GET", f"datasets/{dataset_id}")
    
    async def list_datasets(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """获取数据集列表"""
        params = {"page": page, "limit": limit}
        return await self._call_api("GET", "datasets", params=params)
    
    async def update_dataset(self, dataset_id: str, name: Optional[str] = None, 
                           description: Optional[str] = None, 
                           permission: Optional[str] = None) -> Dict[str, Any]:
        """更新数据集"""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if permission is not None:
            data["permission"] = permission
        
        return await self._call_api("POST", f"datasets/{dataset_id}", data)
    
    async def delete_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """删除数据集"""
        return await self._call_api("DELETE", f"datasets/{dataset_id}")
    
    # ==================== Documents API ====================
    
    async def create_document_by_text(self, dataset_id: str, name: str, text: str, 
                                    metadata: Optional[Dict[str, Any]] = None,
                                    indexing_technique: str = "high_quality") -> Dict[str, Any]:
        """通过文本创建文档"""
        data = {
            "name": name,
            "text": text,
            "indexing_technique": indexing_technique,
            "metadata": metadata or {}
        }
        return await self._call_api("POST", f"datasets/{dataset_id}/documents", data)
    
    async def create_document_by_file(self, dataset_id: str, file_path: str, 
                                    name: Optional[str] = None,
                                    metadata: Optional[Dict[str, Any]] = None,
                                    indexing_technique: str = "high_quality") -> Dict[str, Any]:
        """通过文件创建文档"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        filename = name or os.path.basename(file_path)
        
        with open(file_path, 'rb') as f:
            files = {"file": (filename, f, "application/octet-stream")}
            data = {
                "indexing_technique": indexing_technique,
                "metadata": str(metadata or {})
            }
            return await self._call_api("POST", f"datasets/{dataset_id}/document/create_by_file", 
                                       data=data, files=files)
    
    async def get_document(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        """获取文档信息"""
        return await self._call_api("GET", f"datasets/{dataset_id}/documents/{document_id}")
    
    async def list_documents(self, dataset_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """获取文档列表"""
        params = {"page": page, "limit": limit}
        return await self._call_api("GET", f"datasets/{dataset_id}/documents", params=params)
    
    async def update_document(self, dataset_id: str, document_id: str, 
                            name: Optional[str] = None, text: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """更新文档"""
        data = {}
        if name is not None:
            data["name"] = name
        if text is not None:
            data["text"] = text
        if metadata is not None:
            data["metadata"] = metadata
        
        return await self._call_api("POST", f"datasets/{dataset_id}/documents/{document_id}", data)
    
    async def delete_document(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        """删除文档"""
        return await self._call_api("DELETE", f"datasets/{dataset_id}/documents/{document_id}")
    
    async def get_document_indexing_status(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        """获取文档索引状态"""
        return await self._call_api("GET", f"datasets/{dataset_id}/documents/{document_id}/indexing_status")
    
    async def enable_document(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        """启用文档"""
        return await self._call_api("POST", f"datasets/{dataset_id}/documents/{document_id}/enable")
    
    async def disable_document(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        """禁用文档"""
        return await self._call_api("POST", f"datasets/{dataset_id}/documents/{document_id}/disable")
    
    # ==================== Segments API ====================
    
    async def list_document_segments(self, dataset_id: str, document_id: str, 
                                   page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """获取文档段落列表"""
        params = {"page": page, "limit": limit}
        return await self._call_api("GET", f"datasets/{dataset_id}/documents/{document_id}/segments", params=params)
    
    async def update_document_segment(self, dataset_id: str, document_id: str, segment_id: str,
                                    content: str, answer: Optional[str] = None) -> Dict[str, Any]:
        """更新文档段落"""
        data = {
            "content": content,
            "answer": answer or ""
        }
        return await self._call_api("POST", f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}", data)
    
    async def delete_document_segment(self, dataset_id: str, document_id: str, segment_id: str) -> Dict[str, Any]:
        """删除文档段落"""
        return await self._call_api("DELETE", f"datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}")
    
    # ==================== Batch Operations ====================
    
    async def batch_create_documents(self, dataset_id: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量创建文档"""
        data = {"documents": documents}
        return await self._call_api("POST", f"datasets/{dataset_id}/documents/batch_create", data)
    
    async def batch_delete_documents(self, dataset_id: str, document_ids: List[str]) -> Dict[str, Any]:
        """批量删除文档"""
        data = {"document_ids": document_ids}
        return await self._call_api("POST", f"datasets/{dataset_id}/documents/batch_delete", data)
    
    # ==================== Retrieve API ====================
    
    async def retrieve(self, dataset_id: str, query: str, top_k: int = 4, 
                      score_threshold: float = 0.0, reranking_model: Optional[str] = None) -> Dict[str, Any]:
        """检索数据集"""
        data = {
            "query": query,
            "top_k": top_k,
            "score_threshold": score_threshold
        }
        if reranking_model:
            data["reranking_model"] = reranking_model
        
        return await self._call_api("POST", f"datasets/{dataset_id}/retrieve", data)
    
    # ==================== 兼容性方法（保持向后兼容） ====================
    
    async def create_knowledge_base(self, name: str, description: str = "") -> Dict[str, Any]:
        """创建知识库（兼容性方法）"""
        return await self.create_dataset(name, description)
    
    async def upload_document(self, dataset_id: str, file_path: str, 
                            name: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """上传文档（兼容性方法）"""
        if file_path and os.path.exists(file_path):
            return await self.create_document_by_file(dataset_id, file_path, name, metadata)
        else:
            return await self.create_document_by_text(dataset_id, name, text, metadata)
    
    async def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """获取知识库信息（兼容性方法）"""
        return await self.get_dataset(dataset_id)
    
    async def call_dify_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用Dify API（兼容性方法）"""
        return await self._call_api("POST", endpoint, data)
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
