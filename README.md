# 会计审计智能知识作战台

这是一个面向会计审计训练场景的智能体底座，已经部署到GitHub Pages。

## 访问地址

[https://xjblsy.github.io/Multimodal-Auditing-Intelligent-Agent](https://xjblsy.github.io/Multimodal-Auditing-Intelligent-Agent)

## 功能特性

- 专业知识库管理与搜索
- 基于LLM的智能问答与实践指导
- 实战场景模拟与评估
- 多模态实践指导（文本、图表、视频、模拟案例）
- 学习路径生成
- 财务数据管理与分析
- 审计风险评估
- 合规性检查
- 审计报告生成

## 本地开发

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 启动服务器：`python start.py`
4. 访问：`http://localhost:7860`

## 部署说明

本项目已部署到GitHub Pages，使用静态网站托管前端代码。由于GitHub Pages只支持静态网站，后端功能需要在本地或其他服务器上运行。

### 前端部署

1. 切换到gh-pages分支
2. 将前端文件（index.html, app.js, styles.css）复制到根目录
3. 提交并推送更改
4. 等待GitHub Pages自动部署

### 后端部署

后端服务需要在本地或云服务器上运行，提供API接口供前端调用。

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Python, Flask
- 数据库：SQLite
- 大模型：阿里云百炼

## 许可证

MIT License