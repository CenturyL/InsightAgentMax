from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

import httpx

from backend.retrieval.pipeline import retrieve_knowledge_bundle
from backend.retrieval.postgres_store import knowledge_store_stats
from backend.services.retrieval_context import reset_retrieval_request_context, set_retrieval_request_context


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).resolve().parent
REPORT_JSON = DATA_DIR / "LAST_RUN_REPORT.json"
REPORT_MD = DATA_DIR / "LAST_RUN_REPORT.md"


@dataclass(frozen=True)
class RetrievalCase:
    case_id: str
    question: str
    expected_sources: tuple[str, ...]
    required_terms: tuple[str, ...]
    forbidden_terms: tuple[str, ...] = ()


FILES = (
    DATA_DIR / "01_澄海智造_数据治理与分级规范_v1.md",
    DATA_DIR / "02_澄海智造_生产变更与回滚手册_v1.txt",
    DATA_DIR / "03_澄海智造_客户支持SLA_v1.html",
    DATA_DIR / "04_澄海智造_供应商评分样例_v1.csv",
    ROOT / "output" / "pdf" / "05_澄海智造_AI演示平台安全运行手册_v1.pdf",
)


CASES = (
    RetrievalCase("Q01", "澄海智造的数据分为哪四个级别？L4 数据有哪些典型例子？", (FILES[0].name,), ("L1", "L4", "API Key")),
    RetrievalCase("Q02", "L3 和 L4 数据的默认保留期限分别是多少？备份过期数据应在多久内删除？", (FILES[0].name,), ("3 年", "1 年", "35 天")),
    RetrievalCase("Q03", "什么是玄武四级？", (FILES[0].name,), ("玄武四级", "L4")),
    RetrievalCase("Q04", "C3 生产变更需要哪些审批？蓝鲸回滚阈值有哪些强制停止条件？", (FILES[1].name,), ("变更委员会", "HTTP 5xx", "99.5%")),
    RetrievalCase("Q05", "澄海智造的 RTO 和 RPO 分别是多少？核心交易和知识检索有什么区别？", (FILES[1].name,), ("RTO 为 15 分钟", "RPO 为 5 分钟", "RTO 为 30 分钟", "RPO 为 24 小时")),
    RetrievalCase("Q06", "P0 客户事件的首次响应、状态更新和目标恢复时间是多少？", (FILES[2].name,), ("10 分钟", "每 20 分钟", "2 小时")),
    RetrievalCase("Q07", "P1 事件超过多久没有明确恢复方案会升级为橙色关注事件？", (FILES[2].name,), ("4 小时", "不会自动改变为 P0")),
    RetrievalCase("Q08", "哪个供应商总分最高？哪个供应商有重大安全事件？", (FILES[3].name,), ("恒星数据", "91.0", "暂停准入并整改")),
    RetrievalCase("Q09", "安全运行手册中的星盾模式什么时候启用？启用后保留什么能力？", (FILES[4].name,), ("星盾模式", "健康检查", "只读会话查询")),
    RetrievalCase("Q10", "如果模型费用达到每日额度上限，系统应该怎么做？", (FILES[4].name,), ("达到 100%", "拒绝新调用", "未受控模型")),
    RetrievalCase("Q11", "客户支持 P0 的升级规则是什么？", (FILES[2].name,), ("支持总监", "技术副总裁")),
    RetrievalCase("Q12", "例外权限最长可以有效多久？", (FILES[0].name,), ("72 小时", "自动失效")),
    RetrievalCase("Q13", "请比较蓝鲸回滚阈值与 P0 客户事件的首次响应、状态更新和目标恢复时限。", (FILES[1].name, FILES[2].name), ("HTTP 5xx", "10 分钟", "每 20 分钟", "2 小时")),
    RetrievalCase("Q14", "供应商安全得分最高的是谁？总分和重大安全事件情况如何？", (FILES[3].name,), ("北辰云服", "96", "87.0", "否")),
    RetrievalCase("Q15", "根据现有文档，L4 核心数据能否直接上传到公共模型？", (FILES[0].name,), ("禁止进入公共模型", "上传前必须移除 L4")),
    RetrievalCase("Q16", "文档中没有说明 P0 客户事件的赔偿金额时应该怎么回答？", (FILES[2].name,), (), ("赔偿金额",)),
)


def upload_files(base_url: str) -> list[dict]:
    results = []
    with httpx.Client(timeout=120) as client:
        for path in FILES:
            payload = path.read_bytes()
            source_hash = hashlib.sha256(payload).hexdigest()
            with path.open("rb") as file_obj:
                response = client.post(
                    f"{base_url.rstrip('/')}/api/v3/knowledge/upload",
                    headers={"Idempotency-Key": f"knowledge-e2e-v1-regression-{source_hash[:24]}"},
                    files={"file": (path.name, file_obj)},
                )
            response.raise_for_status()
            body = response.json()
            if body.get("chunks_inserted") != 0:
                raise AssertionError(f"永久测试文件重复上传应为 0：{path.name} -> {body}")
            results.append({"source": path.name, "sha256": source_hash, "chunks_inserted": 0})
    return results


def run_retrieval_cases() -> list[dict]:
    run_id = uuid.uuid4().hex[:12]
    results = []
    for case in CASES:
        token = set_retrieval_request_context(
            f"knowledge-e2e-v1-regression-{run_id}-{case.case_id.lower()}",
            "127.0.0.1",
        )
        try:
            bundle = retrieve_knowledge_bundle(
                case.question,
                k=3,
                candidate_k=15,
                strategy="hybrid_rerank",
            )
        finally:
            reset_retrieval_request_context(token)
        sources = [str((doc.metadata or {}).get("source")) for doc in bundle.docs]
        if not bundle.docs or len(bundle.docs) > 3:
            raise AssertionError(f"{case.case_id} Top 3 契约失败：{len(bundle.docs)}")
        if not bundle.parent_docs or not bundle.citations:
            raise AssertionError(f"{case.case_id} 缺少 Parent 或 Citation")
        missing_sources = [source for source in case.expected_sources if source not in sources]
        if missing_sources:
            raise AssertionError(f"{case.case_id} 缺少来源：{missing_sources}，实际：{sources}")
        missing_terms = [term for term in case.required_terms if term not in bundle.context_text]
        if missing_terms:
            raise AssertionError(f"{case.case_id} 缺少证据：{missing_terms}")
        forbidden_terms = [term for term in case.forbidden_terms if term in bundle.context_text]
        if forbidden_terms:
            raise AssertionError(f"{case.case_id} 不应出现无依据结论：{forbidden_terms}")
        results.append(
            {
                "id": case.case_id,
                "question": case.question,
                "sources": sources,
                "sections": [str((doc.metadata or {}).get("section_path")) for doc in bundle.docs],
                "citations": bundle.citations,
                "status": "passed",
            }
        )
    return results


def write_report(upload_results: list[dict], retrieval_results: list[dict], stats: dict) -> None:
    report = {
        "dataset": "knowledge_e2e_v1",
        "uploads": upload_results,
        "retrieval_cases": retrieval_results,
        "knowledge_store_stats": stats,
        "cleanup_performed": False,
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# 专业知识库端到端回归 - 最近一次结果",
        "",
        "- 数据集：`knowledge_e2e_v1`",
        f"- 重复上传：`{len(upload_results)}/{len(FILES)}` 通过，全部 `chunks_inserted=0`",
        f"- 检索用例：`{len(retrieval_results)}/{len(CASES)}` 通过",
        f"- 数据库：`{stats['source_count']} Source / {stats['parent_count']} Parent / {stats['chunk_count']} Chunk`",
        "- 清理：未执行，文件、Source、Parent、Chunk 和真实 usage 均保留",
        "",
        "## 用例结果",
        "",
        "| 编号 | 状态 | Top 来源 |",
        "|---|---|---|",
    ]
    for row in retrieval_results:
        sources = "；".join(dict.fromkeys(row["sources"]))
        lines.append(f"| {row['id']} | passed | {sources} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="运行永久知识库文件的真实端到端回归，不删除测试数据。")
    parser.add_argument("--base-url", default="http://127.0.0.1:18004")
    args = parser.parse_args()
    upload_results = upload_files(args.base_url)
    retrieval_results = run_retrieval_cases()
    stats = knowledge_store_stats()
    write_report(upload_results, retrieval_results, stats)
    print(json.dumps({"uploads": len(upload_results), "retrieval_cases": len(retrieval_results), "stats": stats}, ensure_ascii=False))


if __name__ == "__main__":
    main()
