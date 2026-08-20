# Local PostgreSQL + pgvector

本项目的长期记忆依赖 PostgreSQL 16 和 pgvector。纯 `postgres:16-alpine` 不包含 `vector.control`，不能直接使用。

构建本地镜像：

```bash
podman build --http-proxy=false \
  -t localhost/insightagent-postgres-pgvector:16-0.8.1 \
  -f ops/postgres/Containerfile .
```

当前本地开发实例：

- 容器：`insightagent-postgres`
- 镜像：`localhost/insightagent-postgres-pgvector:16-0.8.1`
- 宿主机端口：`127.0.0.1:15432`
- 数据卷：`insightagent_pgdata_pgvector`

应用启动时会执行 pgvector 预检。扩展文件缺失或无法创建时启动直接失败，不再等到对话结束后静默跳过长期记忆。
