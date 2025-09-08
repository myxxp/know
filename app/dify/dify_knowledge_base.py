from typing import Optional, List, Dict, Any
import json
import os
from typing import Dict, Any
from app.dify.dify_client import DifyHttpClient  # 底层 HTTP 客户端


class DifyKnowledgeBase:
    """中间层封装 Dify 知识库相关接口"""

    def __init__(self, client: DifyHttpClient):
        self.client = client

    async def list_datasets(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取知识库列表（Datasets）

        Args:
            page: 页码
            limit: 每页条数

        Returns:
            API 返回的字典数据
        """
        params = {
            "page": page,
            "limit": limit
        }
        return await self.client.get("v1/datasets", params=params)

    async def create_dataset(self, name: str, permission: str = "only_me",
                    indexing_technique: str = "high_quality",

                    ) -> Dict[str, Any]:
        """
        创建空知识库 dataset
        Args:
        name: 知识库名称
        permission: 权限 (默认 only_me)，可选值：only_me, anyone, team
        indexing_technique: 索引技术 (默认 high_quality)，可选值：high_quality, economy

        Returns:
        dict: 创建成功返回的 dataset 信息
        """
        payload = {
        "name": name,
        "permission": permission,
        "indexing_technique": indexing_technique
        }

        return await self.client.post("/v1/datasets", json=payload)

    async def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        获取知识库 dataset 信息
        Args:
            dataset_id: 知识库ID
        Returns:
            dict: 知识库信息
        """

        return await self.client.get(f"/v1/datasets/{dataset_id}")


    async def update_dataset(self, dataset_id: str, data: dict) -> dict:
        """
        更新指定知识库 dataset（部分字段）

        Args:
            dataset_id: 知识库 ID
            data: 要更新的字段字典（将按 PATCH 方式提交）

        Returns:
            更新后的知识库信息
        """
        endpoint = f"/v1/datasets/{dataset_id}"
        return await self.client.request("PATCH", endpoint, json=data)


    async def create_document_by_file(
        self,
        dataset_id: str,
        file_path: str,
        indexing_technique: str = "high_quality",
        process_mode: str = "automatic",
        pre_processing_rules: Optional[List[Dict[str, Any]]] = None,
        separator: str = "###",
        max_tokens: int = 500,
    ) -> dict:
        """
        通过文件创建文档至知识库 dataset   （支持自动或自定义处理规则）

        Args:
            dataset_id: 知识库 ID
            file_path: 本地文件路径
            indexing_technique: 向量构建方式，如 "high_quality"
            process_mode: 分段模式："automatic" | "custom"
            pre_processing_rules: 自定义预处理规则（custom 模式时生效）
            separator: 自定义分段符（custom 模式时生效）
            max_tokens: 最大 token 数（custom 模式时生效）

        Returns:
            创建的文档信息
        """

        # 构建 process_rule
        if process_mode == "automatic":
            process_rule = {
                "mode": "automatic",
                "rules": {}
            }
        elif process_mode == "custom":
            process_rule = {
                "mode": "custom",
                "rules": {
                    "pre_processing_rules": pre_processing_rules or [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": True}
                    ],
                    "segmentation": {
                        "separator": separator,
                        "max_tokens": max_tokens
                    }
                }
            }
        else:
            raise ValueError(f"不支持的 process_mode：{process_mode}")

        data = {
            "indexing_technique": indexing_technique,
            "process_rule": process_rule
        }

        # 构造文件上传字段
        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f, "application/octet-stream"),
                "data": (None, json.dumps(data), "text/plain")
            }

            endpoint = f"/v1/datasets/{dataset_id}/document/create-by-file"
            return await self.client.post(endpoint, files=files)

    async def get_indexing_status(
        self, dataset_id: str, batch: str
    ) -> dict:
        """
        查询文档批量上传后的索引状态（如是否处理完毕）

        Args:
            dataset_id: 知识库 ID
            batch: 批次 ID（由文档上传 API 返回）

        Returns:
            索引状态信息
        """
        endpoint = f"/v1/datasets/{dataset_id}/documents/{batch}/indexing-status"
        return await self.client.get(endpoint)

    async def get_document_indexing_status(self, dataset_id: str, document_id: str) -> dict:
        """
        获取文档索引状态
        """
        endpoint = f"/v1/datasets/{dataset_id}/documents/{document_id}/indexing-status"
        return await self.client.get(endpoint)

    async def update_document_by_file(
        self,
        dataset_id: str,
        document_id: str,
        file_path: str,
        name: Optional[str] = None,
        indexing_technique: str = "high_quality",
        process_mode: str = "custom",
        pre_processing_rules: Optional[List[Dict[str, Any]]] = None,
        separator: str = "###",
        max_tokens: int = 500,
    ) -> dict:
        """
        更新文档内容（通过文件上传）

        Args:
            dataset_id: 知识库 ID
            document_id: 文档 ID
            file_path: 本地文件路径
            name: 文档名称（可选）
            indexing_technique: 向量构建方式，如 "high_quality"
            process_mode: 分段模式，如 "custom" 或 "automatic"
            pre_processing_rules: 预处理规则列表（仅 custom 模式下有效）
            separator: 分段符（仅 custom 模式下有效）
            max_tokens: 每段最大 token 数（仅 custom 模式下有效）

        Returns:
            更新后的文档信息
        """

        # 构建清洗与分段规则
        if process_mode == "automatic":
            process_rule = {
                "mode": "automatic",
                "rules": {}
            }
        elif process_mode == "custom":
            process_rule = {
                "mode": "custom",
                "rules": {
                    "pre_processing_rules": pre_processing_rules or [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": True}
                    ],
                    "segmentation": {
                        "separator": separator,
                        "max_tokens": max_tokens
                    }
                }
            }
        else:
            raise ValueError(f"不支持的 process_mode：{process_mode}")

        # 构建数据体
        data = {
            "indexing_technique": indexing_technique,
            "process_rule": process_rule
        }

        if name:
            data["name"] = name

        # 构建上传文件体
        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f, "application/octet-stream"),
                "data": (None, json.dumps(data), "text/plain")
            }

            endpoint = f"/v1/datasets/{dataset_id}/documents/{document_id}/update-by-file"
            return await self.client.post(endpoint, files=files)

    async def list_documents_by_dataset_id(self, dataset_id: str, limit: int = 20) -> dict:
        """
        获取知识库下的所有文档 （自动分页）
        """
        all_docs = []
        page = 1
        while True:
            endpoint = f"/v1/datasets/{dataset_id}/documents"
            params = {"page": page, "limit": limit}
            response = await self.client.get(endpoint, params=params)
            data = response.get("data", [])
            all_docs.extend(data)

            # has_more 判断是否还有更多页
            if not response.get("has_more", False):
                break
            page += 1
        return all_docs

    async def get_document_by_id(self, dataset_id: str, document_id: str) -> dict:
        """
        获取知识库下的指定文档
        """
        endpoint = f"/v1/datasets/{dataset_id}/documents/{document_id}"
        return await self.client.get(endpoint)

    async def add_dataset_metadata(self, dataset_id: str, metadata: dict):
        """
        添加知识库元数据（批量添加多个知识库元数据）
        Args:
            dataset_id: 知识库 ID
            metadata: 元数据
        Returns:
            JSON 响应
        """

        endpoint = f"/v1/datasets/{dataset_id}/metadata"
        return await self.client.post(endpoint, json=metadata)

    async def list_dataset_metadata(self, dataset_id: str) -> dict:
        """
        获取知识库元数据
        """
        endpoint = f"/v1/datasets/{dataset_id}/metadata"
        return await self.client.get(endpoint)
    
    async def add_document_metadata(
        self,
        dataset_id: str,
        metadata: list[dict]
    ) -> dict:
        """
        为知识库中文档批量添加元数据

        Args:
            dataset_id: 知识库 ID
            metadata: 一个包含多个文档及其元数据的列表
                      结构如：
                      [
                          {
                              "document_id": "abc123",
                              "metadata_list": [
                                  {"id": "field_id", "name": "字段名称", "value": "值"},
                                  ...
                              ]
                          },
                          ...
                      ]

        Returns:
            API 返回结果
        """
        endpoint = f"/v1/datasets/{dataset_id}/documents/metadata"
        data = {"operation_data": metadata}
        return await self.client.post(endpoint, json=data)

    










