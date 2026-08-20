# InsightAgentPro

一个用于演示和求职展示的通用智能体项目，包含 React 前端、FastAPI/LangGraph 后端和 PostgreSQL/pgvector 知识库。

## 主要能力

- ReAct Agent 主循环，可手动或自动进入 Plan-and-Execute（PAE）。
- 会话、消息、Trace 和 LangGraph Checkpoint 持久化与回放。
- PostgreSQL/pgvector 统一存储长期记忆和知识库数据。
- Dense + `jieba/rank_bm25` + RRF + 在线 Reranker 混合检索。
- 文档上传、切块、引用、重复上传幂等和知识库重建。
- 模型与检索 usage 记录；开发环境默认关闭每日额度拦截。

## 技术栈

- 前端：React 19、TypeScript、Vite
- 后端：FastAPI、LangChain、LangGraph
- 数据库：PostgreSQL 16、pgvector 0.8.1
- 模型：DeepSeek 对话模型、SiliconFlow Embedding/Reranker

## 环境准备

推荐使用项目现有 Conda 环境：

```bash
conda activate agent
pip install -r backend/requirements.txt
npm install --prefix frontend
```

复制并修改后端配置：

```bash
cp backend/.env.example backend/.env
```

至少需要配置：

```env
POSTGRES_URL=postgresql://user:password@127.0.0.1:15432/insightagent
DEEPSEEK_API_KEY=your_key
SILICONFLOW_API_KEY=your_key
RETRIEVAL_MODEL_PROVIDER=siliconflow

# 本地开发关闭；部署时改为 true
USAGE_LIMIT_ENABLED=false
```

PostgreSQL/pgvector 的构建说明见 `ops/postgres/README.md`。已有本地容器可直接启动：

```bash
podman start insightagent-postgres
```

## 启动项目

后端：

```bash
conda activate agent
python -m uvicorn backend.main:app --host 127.0.0.1 --port 18003 --reload
```

前端：

```bash
npm run dev --prefix frontend
```

访问地址：

- 前端：`http://127.0.0.1:5175`
- 后端：`http://127.0.0.1:18003`
- API 文档：`http://127.0.0.1:18003/docs`

## 测试

```bash
python -m pytest backend/tests -q
npm run build --prefix frontend
```

永久知识库端到端回归集位于 `testdata/knowledge_e2e_v1`。

## 目录结构

```text
backend/       FastAPI、Agent、PAE、记忆、检索和额度服务
frontend/      React 管理与聊天界面
ops/postgres/  PostgreSQL + pgvector 本地镜像配置
testdata/      永久端到端测试文档和问题集
enhance2.md    当前开发成果与后续计划
```

当前知识库以 PostgreSQL 为唯一事实源，不再依赖 ChromaDB。
