# Personal Knowledge Base System

基于 Obsidian 的个人知识库智能管理系统，支持多用户认证、AI 驱动的语义检索、智能对话、知识整合和 GitHub 多端同步。

## 功能特性

- ✅ 多用户认证与管理，独立知识库隔离
- ✅ 基于 embedding-3 的语义检索，支持自然语言查询
- ✅ AI 智能对话，支持多轮上下文（DeepSeek/GLM-4.7）
- ✅ 碎片化信息智能整合与知识化
- ✅ AI 交互经验沉淀与用户画像建模
- ✅ 知识库结构优化建议
- ✅ GitHub 多端双向同步（Web/桌面/移动端）
- ✅ Streamlit 简洁高效的交互界面

## 技术栈

### 后端
- **框架**: Python + FastAPI (异步高性能)
- **AI**: LangChain 0.3.7 + langchain-community
- **向量存储**: ChromaDB
- **对话模型**: DeepSeek (deepseek-chat/deepseek-reasoner) + 智谱AI GLM-4.7
- **Embedding**: 智谱AI embedding-3
- **数据存储**: 本地文件系统 + GitHub API
- **用户认证**: JWT + 用户数据库

### 前端
- **框架**: Streamlit 1.28+
- **通信**: HTTP 客户端
- **UI 风格**: Material Design

## 项目结构

personal-knowledge-base-system/ 
├── backend/ # 后端 API 服务 
├── frontend/ # Streamlit 前端 
├── data/ # 数据目录 
├── .gitignore # Git 忽略规则 
└──README.md # 项目说明 


## 快速开始

### 1. 克隆仓库

```bash
git clone <repository-url>
cd personal-knowledge-base-system
```

### 2. 安装依赖

后端：
```bash
cd backend
pip install -r requirements.txt
```

前端：
```bash
cd frontend
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 backend/.env.example 为 backend/.env，并填入：

DEEPSEEK_API_KEY: DeepSeek API 密钥
ZHIPUAI_API_KEY: 智谱AI API 密钥
GITHUB_TOKEN: GitHub 访问令牌（可选）

### 4. 启动服务

后端：
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

前端：
```bash
cd frontend
streamlit run app.py
```

### 5. 访问应用
打开浏览器访问 http://localhost:8000

## 核心功能

### AI 集成
- **LLM 工厂模式**: 统一接口，灵活切换模型
- **支持的模型**: DeepSeek Chat, DeepSeek Reasoner, 智谱AI GLM-4.7
- **Embedding**: 智谱AI embedding-3 高质量向量化

### RAG 检索
- **语义检索**: 基于向量相似度的自然语言查询
- **文档分块**: 固定大小 + 重叠策略
- **引用来源**: 自动标注答案来源

### 多轮对话
- **上下文管理**: LangChain Memory 保存历史
- **会话管理**: 支持多会话切换
- **模型切换**: 实时切换不同 LLM

### GitHub 同步
- **双向同步**: 自动检测本地和远程差异
- **冲突解决**: 智能合并策略
- **增量更新**: 只同步变更文件

## 开发计划
- 阶段 1: 项目基础
- 阶段 2: 用户认证系统
- 阶段 3: AI 集成（重点）
- 阶段 4: 向量存储
- 阶段 5: RAG 检索
- 阶段 6: 对话系统
- 阶段 7: GitHub 同步
- 阶段 8: 前端界面

## 贡献指南
欢迎贡献！请遵循以下步骤：

Fork 本仓库
创建特性分支 (git checkout -b feature/AmazingFeature)
提交变更 (git commit -m 'feat: Add some AmazingFeature')
推送到分支 (git push origin feature/AmazingFeature)
开启 Pull Request

## 许可证
MIT License

## 联系方式
问题反馈: [GitHub Issues](/issues)
功能建议: [GitHub Discussions](/discussions)