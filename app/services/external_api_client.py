import httpx
import os
from typing import Dict, Any, Optional
from loguru import logger


class ExternalAPIClient:
    """外部API客户端"""
    
    def __init__(self):
        self.logger = logger
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def query_api_data(self, url: str, params: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """查询外部API数据"""
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"外部API查询失败: {e}")
            raise
    
    async def post_api_data(self, url: str, data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """POST请求外部API"""
        try:
            response = await self.client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"外部API POST请求失败: {e}")
            raise
    
    async def download_file(self, url: str, save_path: str, 
                          headers: Optional[Dict[str, str]] = None) -> bool:
        """下载文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"文件下载成功: {save_path}")
            return True
        except Exception as e:
            self.logger.error(f"文件下载失败: {e}")
            return False
    
    async def download_pdf(self, url: str, save_path: str, 
                          headers: Optional[Dict[str, str]] = None) -> bool:
        """下载PDF文件"""
        return await self.download_file(url, save_path, headers)
    
    async def get_file_info(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """获取文件信息（HEAD请求）"""
        try:
            response = await self.client.head(url, headers=headers)
            response.raise_for_status()
            
            return {
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length"),
                "last_modified": response.headers.get("last-modified"),
                "status_code": response.status_code
            }
        except Exception as e:
            self.logger.error(f"获取文件信息失败: {e}")
            raise
    
    async def check_url_accessible(self, url: str, headers: Optional[Dict[str, str]] = None) -> bool:
        """检查URL是否可访问"""
        try:
            response = await self.client.head(url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"URL不可访问: {url}, 错误: {e}")
            return False
    
    async def batch_download_files(self, urls: list, save_dir: str, 
                                 headers: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
        """批量下载文件"""
        results = {}
        
        for i, url in enumerate(urls):
            try:
                # 生成文件名
                filename = f"file_{i+1}.pdf"  # 可以根据URL或其他信息生成更好的文件名
                save_path = os.path.join(save_dir, filename)
                
                success = await self.download_file(url, save_path, headers)
                results[url] = success
                
                if success:
                    self.logger.info(f"批量下载成功: {url} -> {save_path}")
                else:
                    self.logger.error(f"批量下载失败: {url}")
                    
            except Exception as e:
                self.logger.error(f"批量下载异常: {url}, 错误: {e}")
                results[url] = False
        
        return results
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
