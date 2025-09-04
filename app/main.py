from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.database import init_db
from app.core.logger import logger
from app.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="知识库构建服务",
    description="围绕报告引用资料构建自动化数据抓取和知识库构建管线，为智能对话系统提供高质量的上下文支撑",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("知识库构建服务启动中...")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    # 创建必要的目录
    import os
    os.makedirs("downloads/pdfs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info(f"应用启动完成，运行在 {settings.api_host}:{settings.api_port}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("知识库构建服务正在关闭...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
