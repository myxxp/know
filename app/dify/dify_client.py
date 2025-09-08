# client.py
import os
import asyncio
from typing import Dict, Optional, Any
import httpx
from loguru import logger


class DifyHttpClientError(Exception):
    """Dify HTTP客户端基础异常"""
    pass


class DifyAuthenticationError(DifyHttpClientError):
    """Dify认证异常"""
    pass


class DifyRateLimitError(DifyHttpClientError):
    """Dify限流异常"""
    pass


class DifyServerError(DifyHttpClientError):
    """Dify服务器异常"""
    pass


class DifyNetworkError(DifyHttpClientError):
    """Dify网络异常"""
    pass


class DifyTimeoutError(DifyHttpClientError):
    """Dify超时异常"""
    pass


class DifyHttpClient:
    """Dify HTTP客户端 - 带完善异常处理"""
    
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0, max_retries: int = 3):
        """
        初始化Dify HTTP客户端
        
        Args:
            base_url: Dify API基础URL
            api_key: API密钥
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "DifyClient/1.0.0"
        }
        
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        
        logger.info(f"Dify客户端初始化完成: {self.base_url}")

    async def request(self, method: str, endpoint: str, *, 
                     json: Optional[Dict[str, Any]] = None,
                     files: Optional[Dict[str, Any]] = None, 
                     params: Optional[Dict[str, Any]] = None,
                     retry_count: int = 0) -> Dict[str, Any]:
        """
        发送HTTP请求到Dify API
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            endpoint: API端点
            json: JSON数据
            files: 文件数据
            params: URL参数
            retry_count: 当前重试次数
            
        Returns:
            API响应数据
            
        Raises:
            DifyAuthenticationError: 认证失败
            DifyRateLimitError: 请求频率限制
            DifyServerError: 服务器错误
            DifyNetworkError: 网络错误
            DifyTimeoutError: 请求超时
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.headers.copy()
        
        try:
            logger.debug(f"发送请求: {method} {url}")
            
            if files:
                # 文件上传请求
                response = await self.client.request(
                    method, url, data=json, files=files, headers=headers, params=params
                )
            else:
                # JSON请求
                headers["Content-Type"] = "application/json"
                response = await self.client.request(
                    method, url, json=json, headers=headers, params=params
                )
            
            # 检查响应状态码
            await self._handle_response(response, method, url, retry_count)
            
            return response.json()
            
        except httpx.TimeoutException as e:
            error_msg = f"请求超时: {method} {url}"
            logger.error(f"{error_msg}: {e}")
            raise DifyTimeoutError(error_msg) from e
            
        except httpx.ConnectError as e:
            error_msg = f"连接错误: {method} {url}"
            logger.error(f"{error_msg}: {e}")
            raise DifyNetworkError(error_msg) from e
            
        except httpx.RequestError as e:
            error_msg = f"请求错误: {method} {url}"
            logger.error(f"{error_msg}: {e}")
            raise DifyNetworkError(error_msg) from e
            
        except Exception as e:
            error_msg = f"未知错误: {method} {url}"
            logger.error(f"{error_msg}: {e}")
            raise DifyHttpClientError(error_msg) from e

    async def _handle_response(self, response: httpx.Response, method: str, url: str, retry_count: int):
        """
        处理HTTP响应
        
        Args:
            response: HTTP响应对象
            method: HTTP方法
            url: 请求URL
            retry_count: 当前重试次数
        """
        status_code = response.status_code
        
        # 成功响应
        if 200 <= status_code < 300:
            logger.debug(f"请求成功: {method} {url} - {status_code}")
            return
        
        # 客户端错误 (4xx)
        if 400 <= status_code < 500:
            await self._handle_client_error(response, method, url, retry_count)
        
        # 服务器错误 (5xx)
        elif 500 <= status_code < 600:
            await self._handle_server_error(response, method, url, retry_count)
        
        # 其他状态码
        else:
            error_msg = f"未知状态码: {status_code} - {method} {url}"
            logger.error(error_msg)
            raise DifyHttpClientError(error_msg)

    async def _handle_client_error(self, response: httpx.Response, method: str, url: str, retry_count: int):
        """
        处理客户端错误 (4xx)
        """
        status_code = response.status_code
        error_detail = await self._get_error_detail(response)
        
        if status_code == 401:
            error_msg = f"认证失败: {method} {url} - {error_detail}"
            logger.error(error_msg)
            raise DifyAuthenticationError(error_msg)
            
        elif status_code == 403:
            error_msg = f"权限不足: {method} {url} - {error_detail}"
            logger.error(error_msg)
            raise DifyAuthenticationError(error_msg)
            
        elif status_code == 429:
            # 限流错误，可以重试
            if retry_count < self.max_retries:
                retry_after = response.headers.get("Retry-After", "60")
                wait_time = int(retry_after)
                logger.warning(f"请求被限流，{wait_time}秒后重试: {method} {url}")
                await asyncio.sleep(wait_time)
                raise DifyRateLimitError(f"请求被限流，正在重试: {method} {url}")
            else:
                error_msg = f"请求被限流，重试次数已达上限: {method} {url} - {error_detail}"
                logger.error(error_msg)
                raise DifyRateLimitError(error_msg)
                
        elif status_code == 404:
            error_msg = f"资源不存在: {method} {url} - {error_detail}"
            logger.error(error_msg)
            raise DifyHttpClientError(error_msg)
            
        else:
            error_msg = f"客户端错误 {status_code}: {method} {url} - {error_detail}"
            logger.error(error_msg)
            raise DifyHttpClientError(error_msg)

    async def _handle_server_error(self, response: httpx.Response, method: str, url: str, retry_count: int):
        """
        处理服务器错误 (5xx)
        """
        status_code = response.status_code
        error_detail = await self._get_error_detail(response)
        
        # 服务器错误，可以重试
        if retry_count < self.max_retries:
            wait_time = min(2 ** retry_count, 30)  # 指数退避，最大30秒
            logger.warning(f"服务器错误 {status_code}，{wait_time}秒后重试: {method} {url}")
            await asyncio.sleep(wait_time)
            raise DifyServerError(f"服务器错误，正在重试: {method} {url}")
        else:
            error_msg = f"服务器错误 {status_code}，重试次数已达上限: {method} {url} - {error_detail}"
            logger.error(error_msg)
            raise DifyServerError(error_msg)

    async def _get_error_detail(self, response: httpx.Response) -> str:
        """
        获取错误详情
        """
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                return error_data.get("message", error_data.get("error", str(error_data)))
            return str(error_data)
        except Exception:
            return response.text or f"HTTP {response.status_code}"

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET请求"""
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, 
                  files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST请求"""
        return await self.request("POST", endpoint, json=json, files=files)

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PUT请求"""
        return await self.request("PUT", endpoint, json=json)

    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """DELETE请求"""
        return await self.request("DELETE", endpoint, params=params)

    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        logger.info("Dify客户端已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行，创建任务来关闭客户端
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except Exception as e:
            logger.error(f"关闭Dify客户端时出错: {e}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()