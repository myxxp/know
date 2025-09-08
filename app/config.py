from pydantic_settings import BaseSettings
from pydantic import ValidationError
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类 - 敏感信息从环境变量加载，其他使用默认值"""
    
    # 环境配置
    environment: str = "development"
    
    # 数据库配置 - 敏感信息
    db_host: str
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str = "knowledge_db"
    
    # Redis配置 - 敏感信息
    redis_host: str
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # API配置 - 非敏感信息使用默认值
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Dify配置 - 敏感信息
    dify_api_key: str
    dify_base_url: str = "https://api.dify.ai/v1"
    
    # 日志配置 - 非敏感信息使用默认值
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def redis_url(self) -> str:
        """构建Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        return f"redis://{self.redis_host}:{self.redis_port}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_settings() -> Settings:
    """加载配置，提供详细的错误信息"""
    try:
        return Settings()
    except ValidationError as e:
        print("❌ 配置加载失败！缺少必需的环境变量：")
        print("\n请检查以下敏感信息环境变量是否已设置：")
        
        # 必需的环境变量列表（只包含敏感信息）
        required_vars = [
            "DB_HOST", "DB_USER", "DB_PASSWORD",
            "REDIS_HOST", 
            "DIFY_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n缺少的环境变量：{', '.join(missing_vars)}")
        
        print("\n请参考 env.example 文件创建 .env 文件并设置敏感信息。")
        print("示例：")
        print("  cp env.example .env")
        print("  # 然后编辑 .env 文件，设置数据库、Redis、Dify等敏感配置")
        
        raise e


# 全局配置实例
try:
    settings = load_settings()
except ValidationError:
    # 如果配置加载失败，程序应该退出
    import sys
    sys.exit(1)
