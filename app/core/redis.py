from __future__ import annotations
import asyncio
import os
from typing import AsyncGenerator, Optional
from redis.asyncio import Redis
from app.config import settings


class RedisService:
    """Redis服务封装类 - 自动管理连接"""
    
    _instance: Optional[RedisService] = None
    _redis: Optional[Redis] = None
    _is_initialized: bool = False
    
    def __new__(cls) -> RedisService:
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def _ensure_connected(self) -> None:
        """确保Redis连接已建立"""
        if self._redis is None or not self._is_initialized:
            await self._connect()
    
    async def _connect(self) -> None:
        """建立Redis连接"""
        if self._redis is not None:
            await self._disconnect()
        
        self._redis = Redis.from_url(
            settings.redis_url,
            db=settings.redis_db,
            decode_responses=True,
            health_check_interval=30,
            socket_timeout=5,
        )
        await self._redis.ping()
        self._is_initialized = True
    
    async def _disconnect(self) -> None:
        """断开Redis连接"""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None
            self._is_initialized = False
    
    async def get_client(self) -> Redis:
        """获取Redis客户端实例 - 自动管理连接"""
        await self._ensure_connected()
        assert self._redis is not None
        return self._redis
    
    async def init(self) -> None:
        """手动初始化Redis客户端（兼容性方法）"""
        await self._ensure_connected()
    
    async def close(self) -> None:
        """手动关闭Redis客户端（兼容性方法）"""
        await self._disconnect()
    
    async def __aenter__(self) -> Redis:
        """异步上下文管理器入口"""
        return await self.get_client()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口 - 不自动关闭，保持连接复用"""
        pass


# 全局实例
redis_service = RedisService()


async def get_redis() -> AsyncGenerator[Redis, None]:
    """FastAPI依赖注入，获取Redis客户端实例"""
    client = await redis_service.get_client()
    try:
        yield client
    finally:
        pass
