# 服务架构说明

## 服务拆分

原来的 `api_service.py` 已经拆分为两个专门的服务：

### 1. DifyClient (`services/dify_client.py`)

专门用于与Dify API交互的客户端。

#### 主要功能
- 创建知识库
- 上传文档到知识库
- 获取知识库信息
- 列出知识库
- 删除知识库

#### 主要方法
```python
async def create_knowledge_base(name: str, description: str = "") -> Dict[str, Any]
async def upload_document(dataset_id: str, file_path: str, name: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
async def get_dataset_info(dataset_id: str) -> Dict[str, Any]
async def list_datasets() -> Dict[str, Any]
async def delete_dataset(dataset_id: str) -> Dict[str, Any]
```

### 2. ExternalAPIClient (`services/external_api_client.py`)

专门用于外部API请求和文件下载的客户端。

#### 主要功能
- 查询外部API数据
- 下载文件（包括PDF）
- 批量下载文件
- 获取文件信息
- 检查URL可访问性

#### 主要方法
```python
async def query_api_data(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]
async def post_api_data(url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]
async def download_file(url: str, save_path: str, headers: Optional[Dict[str, str]] = None) -> bool
async def download_pdf(url: str, save_path: str, headers: Optional[Dict[str, str]] = None) -> bool
async def batch_download_files(urls: list, save_dir: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, bool]
async def get_file_info(url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]
async def check_url_accessible(url: str, headers: Optional[Dict[str, str]] = None) -> bool
```

## 服务使用

### 在KnowledgeBuilder中的使用

```python
class KnowledgeBuilder:
    def __init__(self):
        self.db_service = DatabaseService()
        self.dify_client = DifyClient()           # Dify API客户端
        self.external_api_client = ExternalAPIClient()  # 外部API客户端
        self.logger = logger
    
    async def build_knowledge_base_sync(self, ...):
        # 使用外部API客户端获取数据
        api_data = await self.external_api_client.query_api_data(url)
        
        # 使用外部API客户端下载PDF
        await self.external_api_client.download_pdf(pdf_url, save_path)
        
        # 使用Dify客户端创建知识库
        dataset_result = await self.dify_client.create_knowledge_base(name, description)
        
        # 使用Dify客户端上传文档
        await self.dify_client.upload_document(dataset_id, file_path, name, text, metadata)
```

## 优势

### 1. 职责分离
- **DifyClient**: 专门处理Dify API相关操作
- **ExternalAPIClient**: 专门处理外部API和文件下载

### 2. 易于维护
- 每个服务职责单一，代码更清晰
- 修改Dify API逻辑不影响外部API功能
- 修改外部API逻辑不影响Dify功能

### 3. 易于扩展
- 可以独立扩展Dify功能
- 可以独立扩展外部API功能
- 可以轻松添加新的API客户端

### 4. 易于测试
- 可以独立测试每个客户端
- 可以模拟不同的API响应
- 测试覆盖更全面

## 扩展指南

### 扩展Dify功能
在 `dify_client.py` 中添加新的Dify API方法：

```python
async def update_dataset(self, dataset_id: str, name: str, description: str) -> Dict[str, Any]:
    """更新知识库"""
    data = {
        "name": name,
        "description": description
    }
    return await self.call_dify_api(f"datasets/{dataset_id}", data)
```

### 扩展外部API功能
在 `external_api_client.py` 中添加新的外部API方法：

```python
async def query_specific_api(self, api_url: str, api_key: str) -> Dict[str, Any]:
    """查询特定API"""
    headers = {"Authorization": f"Bearer {api_key}"}
    return await self.query_api_data(api_url, headers=headers)
```

### 添加新的API客户端
创建新的客户端文件，如 `services/wechat_client.py`：

```python
class WeChatClient:
    """微信API客户端"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_message(self, message: str) -> Dict[str, Any]:
        # 实现微信消息发送逻辑
        pass
```

然后在 `knowledge_builder.py` 中使用：

```python
class KnowledgeBuilder:
    def __init__(self):
        self.db_service = DatabaseService()
        self.dify_client = DifyClient()
        self.external_api_client = ExternalAPIClient()
        self.wechat_client = WeChatClient()  # 新增客户端
        self.logger = logger
```
