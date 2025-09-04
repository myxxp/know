# 配置管理说明

## 环境变量配置策略

本项目采用**敏感信息环境变量化**的配置策略：
- **敏感信息**（IP、用户名、密码、API密钥）必须通过环境变量设置
- **非敏感信息**（端口、日志级别等）有合理的默认值，可根据需要覆盖

## 必需的环境变量（敏感信息）

### 数据库配置
```bash
DB_HOST=localhost               # MySQL数据库主机
DB_USER=root                    # 数据库用户名
DB_PASSWORD=your_password       # 数据库密码
```

### Redis配置
```bash
REDIS_HOST=localhost            # Redis主机
REDIS_PASSWORD=                 # Redis密码（可选）
```

### Dify配置
```bash
DIFY_API_KEY=your_api_key      # Dify API密钥
```

## 可选的环境变量（有默认值）

### 基础配置
```bash
ENVIRONMENT=development          # 环境类型：development/test/production
```

### 数据库配置
```bash
DB_PORT=3306                    # MySQL数据库端口
DB_NAME=knowledge_db            # 数据库名称
```

### Redis配置
```bash
REDIS_PORT=6379                 # Redis端口
```

### API服务配置
```bash
API_HOST=0.0.0.0               # API服务监听地址
API_PORT=8000                  # API服务端口
```

### Dify配置
```bash
DIFY_BASE_URL=https://api.dify.ai/v1  # Dify API基础URL
```

### 日志配置
```bash
LOG_LEVEL=INFO                 # 日志级别：DEBUG/INFO/WARNING/ERROR
LOG_FILE=logs/app.log          # 日志文件路径
```

## 配置方式

### 方式1：使用.env文件（推荐）

1. 复制示例文件：
```bash
cp env.example .env
```

2. 编辑`.env`文件，设置敏感信息：
```bash
# 编辑 .env 文件，只需设置敏感信息
vim .env
```

### 方式2：直接设置环境变量

```bash
export DB_HOST=prod-mysql.example.com
export DB_USER=prod_user
export DB_PASSWORD=secure_password
export REDIS_HOST=prod-redis.example.com
export DIFY_API_KEY=prod_api_key
# ... 设置其他敏感信息
```

### 方式3：Docker环境变量

```yaml
# docker-compose.yml
environment:
  - DB_HOST=mysql
  - DB_USER=app_user
  - DB_PASSWORD=secure_password
  - REDIS_HOST=redis
  - DIFY_API_KEY=prod_api_key
  # ... 其他敏感信息
```

## 配置验证

启动应用时，系统会自动验证敏感信息环境变量：

- ✅ **敏感信息完整**：应用正常启动
- ❌ **敏感信息缺失**：显示详细错误信息并退出

### 错误示例

如果缺少敏感信息环境变量，会看到类似错误：

```
❌ 配置加载失败！缺少必需的环境变量：

请检查以下敏感信息环境变量是否已设置：

缺少的环境变量：DB_PASSWORD, DIFY_API_KEY

请参考 env.example 文件创建 .env 文件并设置敏感信息。
示例：
  cp env.example .env
  # 然后编辑 .env 文件，设置数据库、Redis、Dify等敏感配置
```

## 多环境配置

### 开发环境
```bash
# 敏感信息
DB_HOST=localhost
DB_USER=dev_user
DB_PASSWORD=dev_password
REDIS_HOST=localhost
DIFY_API_KEY=dev_api_key

# 可选覆盖
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### 测试环境
```bash
# 敏感信息
DB_HOST=test-mysql.example.com
DB_USER=test_user
DB_PASSWORD=test_password
REDIS_HOST=test-redis.example.com
DIFY_API_KEY=test_api_key

# 可选覆盖
ENVIRONMENT=test
LOG_LEVEL=INFO
```

### 生产环境
```bash
# 敏感信息
DB_HOST=prod-mysql.example.com
DB_USER=prod_user
DB_PASSWORD=secure_prod_password
REDIS_HOST=prod-redis.example.com
DIFY_API_KEY=prod_api_key

# 可选覆盖
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

## 安全注意事项

1. **不要将`.env`文件提交到版本控制系统**
2. **生产环境使用强密码**
3. **定期轮换API密钥**
4. **使用环境变量而不是硬编码配置**

## 故障排除

### 常见问题

1. **应用启动失败**
   - 检查是否设置了所有必需的环境变量
   - 确认`.env`文件格式正确

2. **数据库连接失败**
   - 验证`DB_HOST`、`DB_PORT`、`DB_USER`、`DB_PASSWORD`设置
   - 确认数据库服务正在运行

3. **Dify API调用失败**
   - 验证`DIFY_API_KEY`和`DIFY_BASE_URL`设置
   - 确认API密钥有效且有足够权限
