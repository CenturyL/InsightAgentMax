from __future__ import annotations

"""Prepare a reproducible public-document corpus for ingestion and evaluation demos."""

import json
import re
import subprocess
from html import unescape
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from local_agent_api.services.eval_service import run_retrieval_eval_job
from local_agent_api.retrieval.pipeline import has_document_source, process_and_store_document


TEST_DOC_SOURCES = [
    {
        "name": "beijing_hightech_notice",
        "url": "https://kw.beijing.gov.cn/zwgk/zwgksbrl/202504/t20250421_4070250.html",
        "title": "北京市高新技术企业认定试点工作通知",
        "region": "北京",
        "year": "2025",
        "doc_category": "policy",
        "source_type": "html",
        "query": "北京市高新技术企业认定试点工作通知主要围绕什么事项？",
        "generation_query": "请概括北京市高新技术企业认定试点工作通知的主要内容。",
        "expected_answer": "答案应概括高新技术企业认定试点工作的通知对象、申报安排或认定相关内容。",
        "expected_keywords": ["高新技术企业", "认定", "试点", "通知"],
        "use_for_generation": True,
    },
    {
        "name": "shanghai_ip_policy",
        "url": "https://www.shanghai.gov.cn/hsysjc-zscqqj1/20251011/b7fc07c92b5b48b9ac365c32b4da9b38.html",
        "title": "浦东新区知识产权专项资金项目申报通知",
        "region": "上海",
        "year": "2025",
        "doc_category": "policy",
        "source_type": "html",
        "query": "浦东新区知识产权专项资金项目申报通知讲了什么？",
        "generation_query": "请总结浦东新区知识产权专项资金项目申报通知的重点。",
        "expected_answer": "答案应概括知识产权专项资金项目的申报对象、申报方向或支持内容。",
        "expected_keywords": ["知识产权", "专项资金", "申报", "项目"],
        "use_for_generation": True,
    },
    {
        "name": "shanghai_vat_policy",
        "url": "https://www.shanghai.gov.cn/tsqygs-zzryqj1/20250709/d8a03682d1a541d5be77934efca6c89c_1ca.html",
        "title": "浦东新区外资研发中心采购设备增值税政策通知",
        "region": "上海",
        "year": "2025",
        "doc_category": "policy",
        "source_type": "html",
        "query": "浦东新区外资研发中心采购设备增值税政策通知的主题是什么？",
        "generation_query": "请概括浦东新区外资研发中心采购设备增值税政策通知的主要内容。",
        "expected_answer": "答案应概括外资研发中心采购设备增值税政策的适用对象和政策内容。",
        "expected_keywords": ["外资研发中心", "采购设备", "增值税", "通知"],
        "use_for_generation": False,
    },
    {
        "name": "wuhan_culture_policy",
        "url": "https://www.wehdz.gov.cn/2022/ggxw_68627/tz_68628/202601/t20260130_2721913.shtml",
        "title": "武汉东湖高新区文化旅游奖补政策申报通知",
        "region": "武汉",
        "year": "2026",
        "doc_category": "policy",
        "source_type": "html",
        "query": "武汉东湖高新区文化旅游奖补政策申报通知主要讲了什么？",
        "generation_query": "请总结武汉东湖高新区文化旅游奖补政策申报通知的重点。",
        "expected_answer": "答案应概括文化旅游奖补政策的申报对象、申报时间或奖补方向。",
        "expected_keywords": ["文化旅游", "奖补", "申报", "通知"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_data_governance_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202506/t20250611_24757347.htm",
        "title": "数据治理及应用建设项目公开招标公告",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "数据治理及应用建设项目公开招标公告的主题是什么？",
        "generation_query": "请概括数据治理及应用建设项目公开招标公告的核心信息。",
        "expected_answer": "答案应概括项目名称、采购内容或招标相关关键信息。",
        "expected_keywords": ["公开招标", "数据治理", "项目", "采购"],
        "use_for_generation": True,
    },
    {
        "name": "ccgp_property_service_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202501/t20250127_24128172.htm",
        "title": "物业服务项目公开招标公告",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "物业服务项目公开招标公告主要内容是什么？",
        "generation_query": "请概括物业服务项目公开招标公告的主要内容。",
        "expected_answer": "答案应概括物业服务项目的采购主题和招标公告核心要点。",
        "expected_keywords": ["物业服务", "公开招标", "项目", "公告"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_pv_project_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202501/t20250110_24051681.htm",
        "title": "光伏发电项目公开招标公告",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "光伏发电项目公开招标公告讲的是什么项目？",
        "generation_query": "请概括光伏发电项目公开招标公告的关键信息。",
        "expected_answer": "答案应概括光伏发电项目的名称、采购或招标核心信息。",
        "expected_keywords": ["光伏发电", "公开招标", "项目", "采购"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_wireless_monitor_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202512/t20251230_26011473.htm",
        "title": "无线电监测站项目招标文件附件",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "无线电监测站项目招标文件附件主要围绕什么内容？",
        "generation_query": "请概括无线电监测站项目招标文件附件的主要内容。",
        "expected_answer": "答案应概括无线电监测站相关项目的招标或附件内容。",
        "expected_keywords": ["无线电监测站", "招标", "附件", "项目"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_science_ship_bid",
        "url": "https://www.ccgp.gov.cn/cggg/zygg/zbgg/202504/t20250425_24504359.htm",
        "title": "科考船项目公开招标文件",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "科考船项目公开招标文件主要讲了什么？",
        "generation_query": "请概括科考船项目公开招标文件的核心内容。",
        "expected_answer": "答案应概括科考船项目的招标主题和核心要求。",
        "expected_keywords": ["科考船", "公开招标", "文件", "项目"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_medical_device_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202502/t20250208_24175634.htm",
        "title": "医疗设备采购项目公开招标公告",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "医疗设备采购项目公开招标公告主要围绕什么采购事项？",
        "generation_query": "请概括医疗设备采购项目公开招标公告的重点。",
        "expected_answer": "答案应概括医疗设备采购项目的采购范围或招标关键信息。",
        "expected_keywords": ["医疗设备", "采购", "公开招标", "项目"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_it_service_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202503/t20250306_24266289.htm",
        "title": "信息化运维服务项目公开招标公告",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "信息化运维服务项目公开招标公告的核心内容是什么？",
        "generation_query": "请概括信息化运维服务项目公开招标公告的主要内容。",
        "expected_answer": "答案应概括信息化运维服务项目的采购主题或招标要点。",
        "expected_keywords": ["信息化", "运维服务", "公开招标", "项目"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_legal_service_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202504/t20250430_24531095.htm",
        "title": "法律服务项目公开招标公告",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "法律服务项目公开招标公告主要采购什么服务？",
        "generation_query": "请概括法律服务项目公开招标公告的主要信息。",
        "expected_answer": "答案应概括法律服务项目的采购内容或招标关键信息。",
        "expected_keywords": ["法律服务", "公开招标", "采购", "项目"],
        "use_for_generation": False,
    },
    {
        "name": "ccgp_equipment_bid",
        "url": "https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202505/t20250528_24676195.htm",
        "title": "设备采购项目公开招标公告",
        "region": "全国",
        "year": "2025",
        "doc_category": "tender",
        "source_type": "html",
        "query": "设备采购项目公开招标公告主要讲了什么采购需求？",
        "generation_query": "请概括设备采购项目公开招标公告的主要内容。",
        "expected_answer": "答案应概括设备采购项目的招标主题或采购核心信息。",
        "expected_keywords": ["设备采购", "公开招标", "项目", "采购"],
        "use_for_generation": False,
    },
]


def _project_root() -> Path:
    """Resolve the project root from the service module location."""
    return Path(__file__).resolve().parent.parent


def _test_docs_dir() -> Path:
    """Directory that stores downloaded raw test documents and cleaned text files."""
    return _project_root() / "data" / "test_docs"


def _eval_dir() -> Path:
    """Directory that stores generated JSONL datasets for offline evaluation."""
    return _project_root() / "data" / "eval"


def _download_if_needed(url: str, destination: Path, force_download: bool) -> None:
    """Fetch a public document only when missing or when force refresh is requested."""
    if destination.exists() and not force_download:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    try:
        with urlopen(request) as response:
            destination.write_bytes(response.read())
    except Exception:
        subprocess.run(
            [
                "curl",
                "-L",
                "-A",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
                "-o",
                str(destination),
                url,
            ],
            check=True,
        )


def _clean_html_to_text(raw_path: Path, clean_path: Path) -> None:
    """Strip HTML tags/scripts/styles so the result is easier to chunk and index."""
    text = raw_path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"</(p|div|li|tr|h1|h2|h3|h4|h5|h6|table|section|article)>", "\n", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    clean_path.write_text(text.strip(), encoding="utf-8")


def _metadata_from_source(source: dict[str, Any]) -> dict[str, Any]:
    """Translate a test-source descriptor into ingestion metadata overrides."""
    return {
        "title": source.get("title"),
        "region": source.get("region"),
        "year": source.get("year"),
        "doc_category": source.get("doc_category"),
        "source_type": source.get("source_type"),
        "modality": "web",
    }


def _rewrite_eval_datasets(clean_paths: dict[str, Path]) -> dict[str, str]:
    """Rebuild retrieval/generation JSONL datasets after documents are refreshed."""
    eval_dir = _eval_dir()
    eval_dir.mkdir(parents=True, exist_ok=True)

    retrieval_dataset = eval_dir / "retrieval_eval_dataset.jsonl"
    retrieval_smoke_dataset = eval_dir / "retrieval_eval_dataset_smoke.jsonl"
    retrieval_compare_dataset = eval_dir / "retrieval_compare_dataset.jsonl"
    retrieval_example = eval_dir / "retrieval_eval_dataset.example.jsonl"
    generation_dataset = eval_dir / "generation_eval_dataset.jsonl"
    generation_example = eval_dir / "generation_eval_dataset.example.jsonl"

    retrieval_lines = []
    retrieval_smoke_lines = []
    generation_lines = []
    for source in TEST_DOC_SOURCES:
        if source["name"] not in clean_paths:
            continue
        clean_path = clean_paths[source["name"]]
        weak_filters = {"doc_category": source["doc_category"]}
        if source["region"] in {"北京", "上海", "武汉"}:
            weak_filters["region"] = source["region"]
        retrieval_lines.append(
            json.dumps(
                {
                    "query": source["query"],
                    "relevant_sources": [clean_path.name],
                    "metadata_filters": weak_filters,
                },
                ensure_ascii=False,
            )
        )
        retrieval_smoke_lines.append(
            json.dumps(
                {
                    "query": source["query"],
                    "relevant_sources": [clean_path.name],
                    "metadata_filters": {"source": str(clean_path)},
                },
                ensure_ascii=False,
            )
        )
        if source.get("use_for_generation", False):
            generation_lines.append(
                json.dumps(
                    {
                        "query": source["generation_query"],
                        "expected_answer": source["expected_answer"],
                        "expected_keywords": source["expected_keywords"],
                        "task_mode": "qa",
                        "metadata_filters": {"source": str(clean_path)},
                    },
                    ensure_ascii=False,
                )
            )

    compare_groups = [
        (
            "上海浦东新区有哪些政策通知分别涉及知识产权支持和外资研发中心采购设备税收支持？",
            ["shanghai_ip_policy", "shanghai_vat_policy"],
            {"doc_category": "policy", "region": "上海"},
        ),
        (
            "哪些通知属于产业扶持、奖补或专项资金申报类政策？",
            ["shanghai_ip_policy", "wuhan_culture_policy", "beijing_hightech_notice"],
            {"doc_category": "policy"},
        ),
        (
            "哪些公开招标公告与数据建设、新能源或设备采购相关？",
            ["ccgp_data_governance_bid", "ccgp_pv_project_bid", "ccgp_equipment_bid"],
            {"doc_category": "tender"},
        ),
        (
            "哪些招标公告主要采购服务而不是设备？",
            ["ccgp_property_service_bid", "ccgp_it_service_bid", "ccgp_legal_service_bid"],
            {"doc_category": "tender"},
        ),
    ]

    for query, names, metadata_filters in compare_groups:
        relevant_sources = [clean_paths[name].name for name in names if name in clean_paths]
        if not relevant_sources:
            continue
        retrieval_lines.append(
            json.dumps(
                {
                    "query": query,
                    "relevant_sources": relevant_sources,
                    "metadata_filters": metadata_filters,
                },
                ensure_ascii=False,
            )
        )

    retrieval_dataset.write_text("\n".join(retrieval_lines) + "\n", encoding="utf-8")
    retrieval_smoke_dataset.write_text("\n".join(retrieval_smoke_lines) + "\n", encoding="utf-8")
    retrieval_compare_dataset.write_text("\n".join(retrieval_lines) + "\n", encoding="utf-8")
    retrieval_example.write_text("\n".join(retrieval_lines) + "\n", encoding="utf-8")
    generation_dataset.write_text("\n".join(generation_lines) + "\n", encoding="utf-8")
    generation_example.write_text("\n".join(generation_lines) + "\n", encoding="utf-8")

    return {
        "retrieval_dataset": str(retrieval_dataset),
        "retrieval_smoke_dataset": str(retrieval_smoke_dataset),
        "retrieval_compare_dataset": str(retrieval_compare_dataset),
        "generation_dataset": str(generation_dataset),
    }


def rebuild_test_environment(
    force_download: bool = False,
    run_retrieval_eval: bool = True,
) -> dict[str, Any]:
    """Download, clean, ingest, and optionally evaluate the demo test corpus."""
    test_docs_dir = _test_docs_dir()
    test_docs_dir.mkdir(parents=True, exist_ok=True)

    raw_paths: list[str] = []
    clean_paths: dict[str, Path] = {}
    ingestion_results: dict[str, int] = {}
    failed_sources: list[dict[str, str]] = []

    for source in TEST_DOC_SOURCES:
        raw_path = test_docs_dir / f"{source['name']}.txt"
        clean_path = test_docs_dir / f"{source['name']}.clean.txt"
        try:
            _download_if_needed(source["url"], raw_path, force_download=force_download)
            _clean_html_to_text(raw_path, clean_path)
            inserted = process_and_store_document(str(clean_path), metadata_overrides=_metadata_from_source(source))
            if inserted > 0 or has_document_source(str(clean_path)):
                raw_paths.append(str(raw_path))
                clean_paths[source["name"]] = clean_path
                ingestion_results[str(clean_path)] = inserted
            else:
                failed_sources.append(
                    {
                        "name": source["name"],
                        "url": source["url"],
                        "error": "document content duplicated another source and was not inserted into the knowledge base",
                    }
                )
        except Exception as exc:
            failed_sources.append({"name": source["name"], "url": source["url"], "error": str(exc)})

    datasets = _rewrite_eval_datasets(clean_paths)

    result: dict[str, Any] = {
        "downloaded_raw_docs": raw_paths,
        "clean_docs": [str(path) for path in clean_paths.values()],
        "ingestion_results": ingestion_results,
        "datasets": datasets,
        "failed_sources": failed_sources,
    }

    if run_retrieval_eval:
        metrics = run_retrieval_eval_job(
            dataset_path=datasets["retrieval_dataset"],
            top_k=3,
            candidate_k=8,
        )
        result["retrieval_eval"] = metrics.model_dump()

    return result
