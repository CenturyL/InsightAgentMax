# 专业知识库端到端回归集 V1

该目录用于长期保留上传、切块、Embedding、Dense、BM25、RRF、Reranker、Parent 和 Citation 回归样本。文档均为虚构业务资料，不包含真实用户或企业信息。

## 文件清单

- `01_澄海智造_数据治理与分级规范_v1.md`
- `02_澄海智造_生产变更与回滚手册_v1.txt`
- `03_澄海智造_客户支持SLA_v1.html`
- `04_澄海智造_供应商评分样例_v1.csv`
- `../../output/pdf/05_澄海智造_AI演示平台安全运行手册_v1.pdf`

## PDF 生成

```bash
python3 \
  testdata/knowledge_e2e_v1/generate_security_manual_pdf.py
```

## 数据保留原则

- 文件和已上传的 PostgreSQL Source/Parent/Chunk 均长期保留。
- 重复执行上传时应返回 `chunks_inserted=0`，不得生成重复 Source。
- 如需升级测试集，新增 V2 文件，不直接修改已经上传的 V1 内容。
- 测试问题和期望结果见 `TEST_CASES.md`。

## 完整回归

后端启动后执行：

```bash
PYTHONPATH=. python \
  testdata/knowledge_e2e_v1/run_e2e_regression.py
```

脚本会重复上传全部文件、执行 16 条真实 Hybrid/Reranker 检索、检查 Parent/Citation 和关键答案证据，并覆盖写入 `LAST_RUN_REPORT.json` 与 `LAST_RUN_REPORT.md`。脚本不会删除数据库中的测试数据，也不会回减真实检索 usage。
