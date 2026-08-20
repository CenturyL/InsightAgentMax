# InsightAgentMax

一个面向求职展示的全栈 Agent Demo：把多轮对话、长期记忆、知识库检索、工具调用和执行轨迹整合到一个可运行的 Web 应用中。

项目重点不是“堆功能”，而是展示一个 Agent 系统如何围绕**可观测、可恢复、可控成本和安全边界**落地。

## 项目亮点

- **多轮 Agent 对话**：基于 LangChain / LangGraph 实现 ReAct 工作流，并支持按需进入 Plan-and-Execute。
- **长期记忆**：保存用户身份、偏好、工作经历等稳定信息，在后续会话中进行语义检索。
- **知识库问答**：支持文档上传、切块、引用和增量重建，采用 PostgreSQL + pgvector 作为统一数据源。
- **混合检索**：Dense 向量检索结合 `jieba` + BM25，使用 RRF 融合候选结果，再由 Reranker 精排。
- **Trace 与回放**：持久化会话消息、工具调用和执行轨迹，便于调试 Agent 决策过程。
- **安全与成本控制**：工具白名单、请求预算、超时、并发保护和可配置的每日模型额度。

## 系统结构

```text
React + TypeScript + Vite
              │
              ▼
FastAPI ── LangGraph Agent ── Tools / PAE / Trace
              │
              ├── DeepSeek：对话与路由模型
              ├── SiliconFlow：Embedding 与 Reranker
              └── PostgreSQL + pgvector：会话、记忆、知识库、用量
```

## 技术栈

- 前端：React 19、TypeScript、Vite
- 后端：Python、FastAPI、LangChain、LangGraph
- 数据库：PostgreSQL 16、pgvector
- 检索：向量检索、BM25、RRF、Reranker
- 默认对话模型：`deepseek-v4-flash`

## 本地运行

### 1. 准备环境

推荐使用 Conda 环境 `agent`：

```bash
conda activate agent
pip install -r backend/requirements.txt
npm install --prefix frontend
```

准备环境变量：

```bash
cp backend/.env.example backend/.env
```

至少配置数据库和模型服务密钥：

```env
POSTGRES_URL=postgresql://postgres:postgres@127.0.0.1:15432/insightagent
DEEPSEEK_API_KEY=your_deepseek_key
SILICONFLOW_API_KEY=your_siliconflow_key
USAGE_LIMIT_ENABLED=false
```

不要提交 `backend/.env` 或任何真实密钥。

### 2. 启动 PostgreSQL

项目需要启用 pgvector 的 PostgreSQL。若本机已有项目容器，可直接启动：

```bash
podman start insightagent-postgres
```

首次部署或容器不存在时，参考 `ops/postgres/README.md` 构建并启动数据库。

### 3. 启动后端和前端

后端：

```bash
conda activate agent
python -m uvicorn backend.main:app --host 127.0.0.1 --port 18003 --reload
```

前端：

```bash
npm run dev --prefix frontend
```

打开：`http://127.0.0.1:5175`

API 文档：`http://127.0.0.1:18003/docs`

## 测试

```bash
python -m pytest backend/tests -q
npm run build --prefix frontend
```

可复用的知识库端到端测试资料位于 `testdata/knowledge_e2e_v1/`，覆盖上传、处理、检索、引用和回归提问。

## 目录结构

```text
backend/       FastAPI、Agent、PAE、记忆、检索和用量控制
frontend/      React 聊天与 Trace 展示界面
ops/postgres/  PostgreSQL + pgvector 本地运行配置
testdata/      知识库端到端测试资料
```

## 展示说明

这是一个可本地运行的求职展示项目，不包含线上演示地址或默认密钥。公开仓库只保留可运行的代码、配置模板和脱敏测试资料；实际使用时请自行配置模型服务和数据库。
