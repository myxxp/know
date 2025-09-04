# 知识库构建服务

围绕"报告引用资料"构建自动化数据抓取和知识库构建管线，为智能对话系统提供高质量的上下文支撑。

## 功能特性

- 🎯 **专注核心**: 专门用于构建知识库的API服务
- 🔄 **自动化管线**: 从数据查询到知识库构建的完整自动化流程
- 📊 **多数据源**: 支持MySQL数据库、外部API、PDF文件等多种数据源
- 🌐 **Dify集成**: 自动调用Dify API构建知识库
- 🔧 **环境配置**: 支持多环境配置管理
- 📝 **日志管理**: 完整的日志记录和监控

## 项目结构

```
knowleage/
├── app/
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   └── routes.py          # 知识库构建API
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── database.py        # 数据库连接管理
│   │   └── logger.py          # 日志配置
│   ├── model/                  # 数据模型
│   │   ├── __init__.py
│   │   └── datebase.py        # 数据库模型定义
│   ├── services/               # 业务服务
│   │   ├── __init__.py
│   │   ├── database_service.py # 数据库服务
│   │   ├── dify_client.py     # Dify API客户端
│   │   ├── external_api_client.py # 外部API客户端
│   │   └── knowledge_builder.py # 知识库构建核心服务
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   └── main.py                # 应用入口
├── downloads/                  # 下载文件目录
│   └── pdfs/                  # PDF文件存储
├── logs/                       # 日志目录
├── requirements.txt            # 依赖包
├── env.example                # 环境变量示例
├── run.py                     # 启动脚本
└── README.md                  # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

**重要：只有敏感信息需要环境变量配置，其他配置有合理的默认值！**

复制环境变量示例文件并修改配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，**只需设置敏感信息**：

```bash
# 敏感信息配置 (必需)
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password

# Redis配置
REDIS_HOST=localhost
REDIS_PASSWORD=

# Dify配置
DIFY_API_KEY=your_dify_api_key_here
```

**注意**：
- 只有敏感信息（IP、用户名、密码、API密钥）需要环境变量配置
- 其他配置（端口、日志级别等）有合理的默认值
- 如果缺少敏感信息环境变量，应用启动时会显示错误信息并退出

### 3. 启动应用

```bash
python run.py
```

或者使用uvicorn直接启动：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档

启动后访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 主要接口

- `POST /api/v1/build` - **构建知识库（异步）** - 主要API接口
- `POST /api/v1/build/sync` - **构建知识库（同步）** - 同步版本
- `GET /api/v1/status/{task_id}` - 获取任务状态

### 辅助接口

- `GET /api/v1/` - 根路径
- `GET /api/v1/health` - 健康检查

### 请求示例

```json
POST /api/v1/build
{
    "report_id": "RPT-2024-001",
    "query_conditions": {
        "date_range": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        "keywords": "人工智能"
    },
    "dataset_name": "AI报告知识库",
    "description": "2024年人工智能相关报告引用资料",
    "include_pdfs": true,
    "batch_size": 50
}
```

### 响应示例

```json
{
    "success": true,
    "dataset_id": "dataset_123456",
    "message": "知识库构建完成",
    "total_items": 150,
    "processed_items": 148,
    "failed_items": 2,
    "task_id": "task_789012"
}
```

## 环境配置

系统支持多环境配置，通过环境变量进行管理：

- `ENVIRONMENT`: 环境类型（development/test/production）
- `DB_*`: 数据库连接配置
- `REDIS_*`: Redis连接配置
- `DIFY_*`: Dify API配置
- `LOG_*`: 日志配置

## 业务流程

围绕"报告引用资料"的完整自动化管线：

1. **接收请求**: 外部系统调用API，提供报告ID或查询条件
2. **数据查询**: 从MySQL数据库查询相关报告引用资料
3. **数据增强**: 通过外部API获取补充数据和元数据
4. **文件下载**: 自动下载相关PDF文件到本地
5. **知识库创建**: 调用Dify API创建新的知识库
6. **数据上传**: 批量上传处理后的数据到Dify知识库
7. **结果返回**: 返回知识库ID和构建结果统计

### 数据流图

```
外部系统 ──→ API请求 ──→ 数据查询 ──→ 数据增强 ──→ PDF下载 ──→ Dify知识库
    ↑                                                                    ↓
    └─────────────── 返回结果 ←─────────────────────────────────────────┘
```

## 开发说明

### 自定义数据查询

在 `app/services/knowledge_builder.py` 中的 `_query_reference_data` 方法中修改SQL查询逻辑，支持：

- 根据报告ID查询特定报告
- 根据日期范围查询
- 根据关键词搜索
- 自定义查询条件

### 扩展数据源

1. 在 `app/services/external_api_client.py` 中添加新的API集成方法
2. 在 `knowledge_builder.py` 的 `_enrich_data_with_api` 方法中调用新API
3. 根据需要修改数据模型

### 自定义处理逻辑

- 修改 `_prepare_content` 方法自定义内容格式
- 修改 `_prepare_metadata` 方法自定义元数据结构
- 修改 `_generate_summary` 方法自定义摘要生成逻辑

## 许可证

MIT License
