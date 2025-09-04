import asyncio
import os
import json
from typing import Dict, Any, Optional, List
from app.services.database_service import DatabaseService
from app.services.dify_client import DifyClient
from app.services.external_api_client import ExternalAPIClient
from loguru import logger


class KnowledgeBuilder:
    """知识库构建器 - 核心业务逻辑"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.dify_client = DifyClient()
        self.external_api_client = ExternalAPIClient()
        self.logger = logger
    
    async def build_knowledge_base_sync(
        self,
        report_id: Optional[str] = None,
        query_conditions: Optional[Dict[str, Any]] = None,
        dataset_name: str = "",
        description: str = "",
        include_pdfs: bool = True,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        同步构建知识库
        
        完整的知识库构建流程：
        1. 查询数据库获取报告引用资料
        2. 从API获取补充数据
        3. 下载PDF文件（如果需要）
        4. 创建Dify知识库
        5. 上传数据到知识库
        """
        try:
            self.logger.info(f"开始构建知识库: {dataset_name}")
            
            # 步骤1: 查询数据库获取报告引用资料
            reference_data = await self._query_reference_data(report_id, query_conditions)
            self.logger.info(f"查询到 {len(reference_data)} 条引用资料")
            
            if not reference_data:
                return {
                    "success": False,
                    "message": "未找到相关引用资料",
                    "total_items": 0,
                    "processed_items": 0,
                    "failed_items": 0
                }
            
            # 步骤2: 从API获取补充数据
            enriched_data = await self._enrich_data_with_api(reference_data)
            self.logger.info(f"数据增强完成，共 {len(enriched_data)} 条数据")
            
            # 步骤3: 下载PDF文件（如果需要）
            if include_pdfs:
                await self._download_pdfs(enriched_data)
                self.logger.info("PDF文件下载完成")
            
            # 步骤4: 创建Dify知识库
            dataset_result = await self.dify_client.create_knowledge_base(dataset_name, description)
            dataset_id = dataset_result.get("id")
            
            if not dataset_id:
                raise Exception("创建Dify知识库失败")
            
            self.logger.info(f"Dify知识库创建成功: {dataset_id}")
            
            # 步骤5: 批量上传数据到知识库
            upload_result = await self._upload_to_dify(dataset_id, enriched_data, batch_size)
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "message": "知识库构建完成",
                "total_items": len(enriched_data),
                "processed_items": upload_result["processed"],
                "failed_items": upload_result["failed"]
            }
            
        except Exception as e:
            self.logger.error(f"知识库构建失败: {e}")
            return {
                "success": False,
                "message": f"知识库构建失败: {str(e)}",
                "total_items": 0,
                "processed_items": 0,
                "failed_items": 0
            }
        finally:
            await self.dify_client.close()
            await self.external_api_client.close()
    
    async def build_knowledge_base_async(
        self,
        report_id: Optional[str] = None,
        query_conditions: Optional[Dict[str, Any]] = None,
        dataset_name: str = "",
        description: str = "",
        include_pdfs: bool = True,
        batch_size: int = 50,
        task_id: str = ""
    ):
        """异步构建知识库（后台任务）"""
        try:
            result = await self.build_knowledge_base_sync(
                report_id, query_conditions, dataset_name, 
                description, include_pdfs, batch_size
            )
            
            # 这里可以将结果存储到Redis或数据库，供状态查询使用
            self.logger.info(f"异步任务 {task_id} 完成: {result}")
            
        except Exception as e:
            self.logger.error(f"异步任务 {task_id} 失败: {e}")
    
    async def _query_reference_data(
        self, 
        report_id: Optional[str], 
        query_conditions: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """查询报告引用资料"""
        try:
            # 构建查询SQL
            if report_id:
                # 根据报告ID查询
                query = """
                SELECT * FROM report_references 
                WHERE report_id = :report_id
                ORDER BY created_at DESC
                """
                params = {"report_id": report_id}
            elif query_conditions:
                # 根据查询条件构建动态SQL
                where_conditions = []
                params = {}
                
                for key, value in query_conditions.items():
                    if key == "date_range":
                        where_conditions.append("created_at BETWEEN :start_date AND :end_date")
                        params["start_date"] = value.get("start_date")
                        params["end_date"] = value.get("end_date")
                    elif key == "keywords":
                        where_conditions.append("(title LIKE :keywords OR content LIKE :keywords)")
                        params["keywords"] = f"%{value}%"
                    else:
                        where_conditions.append(f"{key} = :{key}")
                        params[key] = value
                
                query = f"""
                SELECT * FROM report_references 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY created_at DESC
                LIMIT 1000
                """
            else:
                # 默认查询最近的引用资料
                query = """
                SELECT * FROM report_references 
                ORDER BY created_at DESC 
                LIMIT 100
                """
                params = {}
            
            return self.db_service.query_data(query, params)
            
        except Exception as e:
            self.logger.error(f"查询引用资料失败: {e}")
            return []
    
    async def _enrich_data_with_api(self, reference_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """通过API增强数据"""
        enriched_data = []
        
        for item in reference_data:
            try:
                # 这里可以根据具体需求调用不同的API来增强数据
                # 例如：获取更多元数据、验证链接、获取摘要等
                
                enriched_item = item.copy()
                
                # 示例：如果有关联的API链接，获取更多信息
                if item.get("api_url"):
                    try:
                        api_data = await self.external_api_client.query_api_data(item["api_url"])
                        enriched_item["api_metadata"] = json.dumps(api_data)
                    except Exception as e:
                        self.logger.warning(f"API数据获取失败 {item['api_url']}: {e}")
                
                # 示例：生成内容摘要
                if item.get("content"):
                    enriched_item["summary"] = self._generate_summary(item["content"])
                
                enriched_data.append(enriched_item)
                
            except Exception as e:
                self.logger.error(f"数据增强失败: {e}")
                enriched_data.append(item)  # 保留原始数据
        
        return enriched_data
    
    async def _download_pdfs(self, data: List[Dict[str, Any]]):
        """下载PDF文件"""
        pdf_dir = "downloads/pdfs"
        os.makedirs(pdf_dir, exist_ok=True)
        
        for item in data:
            pdf_url = item.get("pdf_url")
            if pdf_url:
                try:
                    filename = f"{item.get('id', 'unknown')}_{item.get('title', 'document')}.pdf"
                    filepath = os.path.join(pdf_dir, filename)
                    
                    success = await self.external_api_client.download_pdf(pdf_url, filepath)
                    if success:
                        item["local_pdf_path"] = filepath
                        self.logger.info(f"PDF下载成功: {filepath}")
                    
                except Exception as e:
                    self.logger.error(f"PDF下载失败 {pdf_url}: {e}")
    
    async def _upload_to_dify(self, dataset_id: str, data: List[Dict[str, Any]], batch_size: int) -> Dict[str, int]:
        """批量上传数据到Dify知识库"""
        processed = 0
        failed = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            for item in batch:
                try:
                    # 准备上传数据
                    name = item.get("title", f"Document_{item.get('id', 'unknown')}")
                    content = self._prepare_content(item)
                    metadata = self._prepare_metadata(item)
                    
                    await self.dify_client.upload_document(
                        dataset_id=dataset_id,
                        file_path=item.get("local_pdf_path", ""),
                        name=name,
                        text=content,
                        metadata=metadata
                    )
                    
                    processed += 1
                    self.logger.info(f"文档上传成功: {name}")
                    
                except Exception as e:
                    failed += 1
                    self.logger.error(f"文档上传失败: {e}")
            
            # 批次间稍作延迟，避免API限制
            if i + batch_size < len(data):
                await asyncio.sleep(1)
        
        return {"processed": processed, "failed": failed}
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """生成内容摘要"""
        if len(content) <= max_length:
            return content
        
        # 简单的摘要生成：取前max_length个字符
        summary = content[:max_length]
        if content[max_length:max_length+1] != " ":
            # 找到最后一个空格，避免截断单词
            last_space = summary.rfind(" ")
            if last_space > max_length * 0.8:  # 如果最后一个空格不太远
                summary = summary[:last_space]
        
        return summary + "..."
    
    def _prepare_content(self, item: Dict[str, Any]) -> str:
        """准备上传内容"""
        content_parts = []
        
        if item.get("title"):
            content_parts.append(f"标题: {item['title']}")
        
        if item.get("content"):
            content_parts.append(f"内容: {item['content']}")
        
        if item.get("summary"):
            content_parts.append(f"摘要: {item['summary']}")
        
        if item.get("api_metadata"):
            try:
                api_meta = json.loads(item["api_metadata"])
                content_parts.append(f"API数据: {json.dumps(api_meta, ensure_ascii=False)}")
            except:
                pass
        
        return "\n\n".join(content_parts)
    
    def _prepare_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """准备元数据"""
        metadata = {
            "source_type": "report_reference",
            "source_id": item.get("id"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at")
        }
        
        # 添加其他有用的元数据
        if item.get("author"):
            metadata["author"] = item["author"]
        if item.get("category"):
            metadata["category"] = item["category"]
        if item.get("tags"):
            metadata["tags"] = item["tags"]
        if item.get("local_pdf_path"):
            metadata["has_pdf"] = True
        
        return metadata
