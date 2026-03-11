from __future__ import annotations

"""Helpers for converting retrieved documents into lightweight citation records."""

from langchain_core.documents import Document


def build_citations(docs: list[Document]) -> list[dict]:
    """Normalize document metadata so downstream code can render consistent citations."""
    citations: list[dict] = []
    for idx, doc in enumerate(docs, start=1):
        metadata = doc.metadata or {}
        citations.append(
            {
                "id": f"ref_{idx}",
                "source": metadata.get("source")
                or metadata.get("file_path")
                or metadata.get("title")
                or "unknown",
                "page": metadata.get("page"),
                "section": metadata.get("section_path"),
                "preview": doc.page_content[:160],
            }
        )
    return citations


def format_citations(citations: list[dict]) -> str:
    """Render citations into plain text for prompts and fallback answers."""
    if not citations:
        return "无"

    lines = []
    for citation in citations:
        source = citation.get("source", "unknown")
        page = citation.get("page")
        section = citation.get("section")
        suffix = []
        if page is not None:
            suffix.append(f"page={page}")
        if section:
            suffix.append(f"section={section}")
        label = f"{source} ({', '.join(suffix)})" if suffix else str(source)
        lines.append(f"- {label}")
    return "\n".join(lines)
