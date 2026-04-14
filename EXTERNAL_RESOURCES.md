# 会计审计智能体 - 外部资源需求文档

## 概述

本文档详细说明会计审计智能体运行所需的外部资源、API密钥和第三方服务配置。

## 1. 大语言模型 API

### 阿里云百炼（DashScope）

**用途**: 为智能体提供自然语言理解和生成能力

**必需配置项**:
- `AUDIT_AGENT_API_KEY`: 阿里云百炼 API 密钥

**获取方式**:
1. 访问阿里云百炼平台：https://dashscope.console.aliyun.com/
2. 注册或登录阿里云账号
3. 在"API密钥管理"中创建新的API密钥
4. 复制生成的API密钥

**环境变量配置**:
```bash
AUDIT_AGENT_API_KEY=your-api-key-here
AUDIT_AGENT_MODEL_PROVIDER=dashscope
AUDIT_AGENT_MODEL_NAME=qwen-flash
AUDIT_AGENT_OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**可选模型配置**:
| 模型名称 | 用途 | 特点 |
|---------|------|------|
| qwen-flash | 快速问答 | 响应速度快，适合日常查询 |
| qwen-plus | 复杂分析 | 推理能力强，适合深度分析 |
| qwen-max | 高精度任务 | 最高精度，适合关键决策 |

### OpenAI API

**用途**: 替代阿里云百炼的备选方案

**必需配置项**:
- `AUDIT_AGENT_API_KEY`: OpenAI API 密钥
- `AUDIT_AGENT_OPENAI_BASE_URL`: OpenAI API 端点（通常为 https://api.openai.com/v1）

**获取方式**:
1. 访问 OpenAI 平台：https://platform.openai.com/
2. 注册账号并完成认证
3. 在 API Keys 中创建新的密钥
4. 注意：OpenAI API 需要境外服务器访问

**环境变量配置**:
```bash
AUDIT_AGENT_API_KEY=sk-your-api-key-here
AUDIT_AGENT_MODEL_PROVIDER=openai-compatible
AUDIT_AGENT_MODEL_NAME=gpt-4o-mini
AUDIT_AGENT_OPENAI_BASE_URL=https://api.openai.com/v1
```

### OpenRouter

**用途**: 统一访问多个大模型提供商

**必需配置项**:
- `AUDIT_AGENT_API_KEY`: OpenRouter API 密钥
- `AUDIT_AGENT_MODEL_PROVIDER`: 设置为 openrouter
- `AUDIT_AGENT_MODEL_NAME`: 想要使用的模型名称

**获取方式**:
1. 访问 OpenRouter：https://openrouter.ai/
2. 注册账号并获取 API 密钥

**环境变量配置**:
```bash
AUDIT_AGENT_API_KEY=sk-or-your-api-key-here
AUDIT_AGENT_MODEL_PROVIDER=openrouter
AUDIT_AGENT_MODEL_NAME=anthropic/claude-3-haiku
```

### Ollama（本地部署）

**用途**: 在本地运行开源大模型，保护数据隐私

**必需配置项**:
- `AUDIT_AGENT_MODEL_PROVIDER`: 设置为 ollama
- `AUDIT_AGENT_MODEL_NAME`: 已下载的模型名称
- `AUDIT_AGENT_OPENAI_BASE_URL`: Ollama 服务地址（默认为 http://localhost:11434）

**安装和配置**:
1. 下载 Ollama：https://ollama.com/download
2. 安装并启动 Ollama 服务
3. 下载模型：`ollama pull qwen2.5:7b`
4. 验证服务：`curl http://localhost:11434`

**环境变量配置**:
```bash
AUDIT_AGENT_MODEL_PROVIDER=ollama
AUDIT_AGENT_MODEL_NAME=qwen2.5:7b
AUDIT_AGENT_OPENAI_BASE_URL=http://localhost:11434
```

## 2. 文档导入服务

### DashScope 文档解析（可选）

**用途**: 支持远程导入和解析 PDF、Word 等文档

**启用条件**:
- 已配置阿里云百炼 API 密钥
- `AUDIT_AGENT_ENABLE_REMOTE_IMPORT=true`

**环境变量配置**:
```bash
AUDIT_AGENT_ENABLE_REMOTE_IMPORT=true
AUDIT_AGENT_DOC_MODEL_NAME=qwen-doc-turbo
```

### 本地文档导入

**用途**: 不依赖云端服务，本地处理文档导入

**支持格式**:
- PDF（需要 pdfminer 或 pdfplumber）
- Word（需要 python-docx）
- Excel（需要 openpyxl）
- Markdown
- 纯文本

**安装依赖**:
```bash
pip install pdfminer.six python-docx openpyxl markdown
```

## 3. 数据库

### SQLite（内置）

**用途**: 知识库全文搜索索引

**无需额外配置**，系统自动管理

**数据文件位置**:
- `data/generated/knowledge.db`

## 4. 配置文件位置

**主配置文件**: `.env`

**示例配置**:
```bash
# 基础配置
AUDIT_AGENT_HOST=127.0.0.1
AUDIT_AGENT_PORT=7860
AUDIT_AGENT_DEFAULT_INDUSTRY=制造业

# 大模型配置（选择一种）
# 方案1: 阿里云百炼
AUDIT_AGENT_MODEL_PROVIDER=dashscope
AUDIT_AGENT_MODEL_NAME=qwen-flash
AUDIT_AGENT_API_KEY=sk-your-dashscope-key-here
AUDIT_AGENT_OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 方案2: OpenAI
# AUDIT_AGENT_MODEL_PROVIDER=openai-compatible
# AUDIT_AGENT_MODEL_NAME=gpt-4o-mini
# AUDIT_AGENT_API_KEY=sk-your-openai-key-here
# AUDIT_AGENT_OPENAI_BASE_URL=https://api.openai.com/v1

# 方案3: Ollama 本地部署
# AUDIT_AGENT_MODEL_PROVIDER=ollama
# AUDIT_AGENT_MODEL_NAME=qwen2.5:7b
# AUDIT_AGENT_OPENAI_BASE_URL=http://localhost:11434

# 文档导入配置
AUDIT_AGENT_ENABLE_REMOTE_IMPORT=false
AUDIT_AGENT_DOC_MODEL_NAME=qwen-doc-turbo
AUDIT_AGENT_VISION_MODEL_NAME=qwen-vl-ocr-latest

# 模型参数
AUDIT_AGENT_MODEL_TEMPERATURE=0.2
```

## 5. 安全注意事项

### API 密钥保护

1. **不要将 API 密钥提交到 Git 仓库**
   - 确保 `.env` 文件已添加到 `.gitignore`
   - 使用 `.env.example` 作为模板

2. **定期轮换 API 密钥**
   - 建议每 3-6 个月更换一次
   - 及时吊销不再使用的密钥

3. **限制 API 密钥使用范围**
   - 阿里云：设置 IP 白名单
   - OpenAI：设置使用限额

### 数据隐私

1. **本地部署方案**
   - 使用 Ollama 完全本地运行
   - 数据不会离开本地环境

2. **云端服务**
   - 了解数据存储和处理位置
   - 确认符合企业数据安全政策

## 6. 故障排除

### 模型连接失败

**症状**: 状态显示"离线模式"或"连接失败"

**排查步骤**:
1. 确认 API 密钥配置正确
2. 检查网络连接
3. 验证 API 端点可访问
4. 查看服务器日志

**常见错误**:
| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| "API密钥无效" | API 密钥错误或过期 | 检查并更新 API 密钥 |
| "请求超时" | 网络问题或服务不可用 | 检查网络连接 |
| "额度已用完" | API 配额耗尽 | 检查账户余额或升级套餐 |

### 文档导入失败

**症状**: 无法上传或解析文档

**排查步骤**:
1. 确认已安装所需依赖库
2. 检查文档格式是否支持
3. 验证文档大小是否超限
4. 查看导入日志

## 7. 成本估算

### 阿里云百炼

| 模型 | 输入价格 | 输出价格 | 适用场景 |
|------|---------|---------|---------|
| qwen-flash | 免费 | 免费 | 开发测试 |
| qwen-plus | ¥0.004/千tokens | ¥0.012/千tokens | 生产环境 |
| qwen-max | ¥0.12/千tokens | ¥0.36/千tokens | 关键任务 |

### OpenAI

| 模型 | 输入价格 | 输出价格 | 适用场景 |
|------|---------|---------|---------|
| gpt-4o-mini | $0.15/千tokens | $0.60/千tokens | 日常对话 |
| gpt-4o | $2.5/千tokens | $10/千tokens | 复杂任务 |

### Ollama

| 成本类型 | 金额 |
|---------|------|
| 模型下载 | 免费 |
| 本地运行 | 仅需电费 |
| API 调用 | 免费 |

## 8. 联系支持

如遇到问题，请通过以下方式获取帮助：
1. 查看项目 GitHub Issues
2. 提交新的 Issue 描述问题
3. 附上错误日志和配置信息（注意脱敏）