from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.services.knowledge_builder import KnowledgeBuilder
from loguru import logger

router = APIRouter()


# 知识库构建请求模型
class KnowledgeBuildRequest(BaseModel):
    """知识库构建请求参数"""
    report_id: Optional[str] = None  # 报告ID
    query_conditions: Optional[Dict[str, Any]] = None  # 查询条件
    dataset_name: str  # 知识库名称
    description: Optional[str] = ""  # 知识库描述
    include_pdfs: bool = True  # 是否包含PDF文件
    batch_size: int = 50  # 批处理大小


class KnowledgeBuildResponse(BaseModel):
    """知识库构建响应"""
    success: bool
    dataset_id: Optional[str] = None
    message: str
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    task_id: Optional[str] = None


@router.get("/")
async def root():
    """根路径"""
    return {"message": "知识库构建服务API", "version": "1.0.0"}


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@router.post("/build", response_model=KnowledgeBuildResponse)
async def build_knowledge_base(
    request: KnowledgeBuildRequest,
    background_tasks: BackgroundTasks
):
    """
    构建知识库 - 主要API接口
    
    根据提供的参数自动完成：
    1. 从MySQL数据库查询报告引用资料
    2. 从API获取补充数据
    3. 下载相关PDF文件
    4. 调用Dify API构建知识库
    """
    try:
        builder = KnowledgeBuilder()
        
        # 生成任务ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # 异步执行知识库构建任务
        background_tasks.add_task(
            builder.build_knowledge_base_async,
            request.report_id,
            request.query_conditions,
            request.dataset_name,
            request.description,
            request.include_pdfs,
            request.batch_size,
            task_id
        )
        
        return KnowledgeBuildResponse(
            success=True,
            message="知识库构建任务已启动",
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"启动知识库构建任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build/sync", response_model=KnowledgeBuildResponse)
async def build_knowledge_base_sync(request: KnowledgeBuildRequest):
    """
    构建知识库 - 同步版本
    
    同步执行知识库构建，返回完整结果
    """
    try:
        builder = KnowledgeBuilder()
        result = await builder.build_knowledge_base_sync(
            report_id=request.report_id,
            query_conditions=request.query_conditions,
            dataset_name=request.dataset_name,
            description=request.description,
            include_pdfs=request.include_pdfs,
            batch_size=request.batch_size
        )
        
        return KnowledgeBuildResponse(**result)
        
    except Exception as e:
        logger.error(f"知识库构建失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        # 这里可以实现任务状态查询逻辑
        # 可以使用Redis或数据库存储任务状态
        return {
            "task_id": task_id,
            "status": "processing",  # pending, processing, completed, failed
            "progress": 0,
            "message": "任务正在处理中"
        }
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
