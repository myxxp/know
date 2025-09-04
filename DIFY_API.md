# Dify API 客户端功能说明

基于[Dify官方API文档](https://docs.dify.ai/api-reference)重新设计的知识库API客户端，按照官方文档结构组织功能。

## 📚 API 功能模块

### 1. Datasets API (数据集管理)

#### 创建和管理数据集
```python
# 创建数据集
await dify_client.create_dataset(name="我的知识库", description="描述", permission="only_me")

# 获取数据集信息
await dify_client.get_dataset(dataset_id)

# 获取数据集列表
await dify_client.list_datasets(page=1, limit=20)

# 更新数据集
await dify_client.update_dataset(dataset_id, name="新名称", description="新描述")

# 删除数据集
await dify_client.delete_dataset(dataset_id)
```

### 2. Documents API (文档管理)

#### 创建文档
```python
# 通过文本创建文档
await dify_client.create_document_by_text(
    dataset_id="dataset_id",
    name="文档名称",
    text="文档内容",
    metadata={"source": "api"},
    indexing_technique="high_quality"
)

# 通过文件创建文档
await dify_client.create_document_by_file(
    dataset_id="dataset_id",
    file_path="/path/to/file.pdf",
    name="文档名称",
    metadata={"source": "file"},
    indexing_technique="high_quality"
)
```

#### 文档操作
```python
# 获取文档信息
await dify_client.get_document(dataset_id, document_id)

# 获取文档列表
await dify_client.list_documents(dataset_id, page=1, limit=20)

# 更新文档
await dify_client.update_document(dataset_id, document_id, name="新名称", text="新内容")

# 删除文档
await dify_client.delete_document(dataset_id, document_id)
```

#### 文档状态管理
```python
# 获取文档索引状态
await dify_client.get_document_indexing_status(dataset_id, document_id)

# 启用文档
await dify_client.enable_document(dataset_id, document_id)

# 禁用文档
await dify_client.disable_document(dataset_id, document_id)
```

### 3. Segments API (段落管理)

```python
# 获取文档段落列表
await dify_client.list_document_segments(dataset_id, document_id, page=1, limit=20)

# 更新文档段落
await dify_client.update_document_segment(
    dataset_id, document_id, segment_id,
    content="段落内容",
    answer="段落答案"
)

# 删除文档段落
await dify_client.delete_document_segment(dataset_id, document_id, segment_id)
```

### 4. Batch Operations (批量操作)

```python
# 批量创建文档
documents = [
    {"name": "文档1", "text": "内容1", "metadata": {}},
    {"name": "文档2", "text": "内容2", "metadata": {}}
]
await dify_client.batch_create_documents(dataset_id, documents)

# 批量删除文档
document_ids = ["doc1", "doc2", "doc3"]
await dify_client.batch_delete_documents(dataset_id, document_ids)
```

### 5. Retrieve API (检索功能)

```python
# 检索数据集
results = await dify_client.retrieve(
    dataset_id="dataset_id",
    query="查询内容",
    top_k=4,
    score_threshold=0.0,
    reranking_model="reranking_model_name"
)
```

## 🔄 兼容性方法

为了保持向后兼容，保留了原有的方法名：

```python
# 兼容性方法
await dify_client.create_knowledge_base(name, description)  # → create_dataset
await dify_client.upload_document(dataset_id, file_path, name, text, metadata)  # → create_document_by_*
await dify_client.get_dataset_info(dataset_id)  # → get_dataset
await dify_client.call_dify_api(endpoint, data)  # → _call_api
```

## 🚀 使用示例

### 完整的知识库构建流程

```python
async def build_knowledge_base_example():
    dify_client = DifyClient()
    
    try:
        # 1. 创建数据集
        dataset = await dify_client.create_dataset(
            name="报告引用资料库",
            description="2024年报告引用资料知识库",
            permission="only_me"
        )
        dataset_id = dataset["id"]
        
        # 2. 批量创建文档
        documents = [
            {
                "name": "报告1",
                "text": "报告内容1...",
                "metadata": {"source": "database", "report_id": "RPT-001"}
            },
            {
                "name": "报告2", 
                "text": "报告内容2...",
                "metadata": {"source": "api", "report_id": "RPT-002"}
            }
        ]
        await dify_client.batch_create_documents(dataset_id, documents)
        
        # 3. 检查文档索引状态
        for doc in documents:
            status = await dify_client.get_document_indexing_status(dataset_id, doc["id"])
            print(f"文档 {doc['name']} 索引状态: {status}")
        
        # 4. 检索测试
        results = await dify_client.retrieve(
            dataset_id=dataset_id,
            query="人工智能发展趋势",
            top_k=5
        )
        print(f"检索结果: {results}")
        
    finally:
        await dify_client.close()
```

### 文档状态管理

```python
async def manage_document_status():
    dify_client = DifyClient()
    
    try:
        # 获取文档列表
        docs = await dify_client.list_documents(dataset_id)
        
        for doc in docs["data"]:
            doc_id = doc["id"]
            
            # 检查索引状态
            status = await dify_client.get_document_indexing_status(dataset_id, doc_id)
            
            if status["indexing_status"] == "error":
                # 如果索引失败，重新启用
                await dify_client.enable_document(dataset_id, doc_id)
                print(f"重新启用文档: {doc['name']}")
            
    finally:
        await dify_client.close()
```

## 📋 API 响应格式

### 数据集响应
```json
{
  "id": "dataset_id",
  "name": "数据集名称",
  "description": "数据集描述",
  "permission": "only_me",
  "created_at": 1705407629,
  "updated_at": 1705407629
}
```

### 文档响应
```json
{
  "id": "document_id",
  "name": "文档名称",
  "text": "文档内容",
  "metadata": {},
  "indexing_status": "completed",
  "created_at": 1705407629,
  "updated_at": 1705407629
}
```

### 检索响应
```json
{
  "query": "查询内容",
  "records": [
    {
      "segment": {
        "id": "segment_id",
        "content": "段落内容",
        "answer": "段落答案"
      },
      "score": 0.95
    }
  ]
}
```

## 🔧 配置要求

确保在环境变量中设置：
```bash
DIFY_API_KEY=your_dify_api_key
DIFY_BASE_URL=https://api.dify.ai/v1
```

## 📚 参考文档

- [Dify API 官方文档](https://docs.dify.ai/api-reference)
- [知识库 API 文档](https://docs.dify.ai/guides/knowledge-base/maintain-dataset-via-api)
