from __future__ import annotations

import argparse

from backend.core.config import settings
from backend.core.embedding import get_embedding_model
from backend.retrieval.postgres_store import (
    KnowledgeStoreError,
    activate_rebuilt_index,
    create_building_index_version,
    get_index_chunk_ids,
    list_active_chunks_for_reindex,
    upsert_reindexed_chunks,
)


class ReindexError(RuntimeError):
    pass


def rebuild_vector_collection(
    source_name: str | None = None,
    target_name: str | None = None,
    *,
    batch_size: int | None = None,
) -> dict[str, int | str]:
    version_name = (target_name or settings.KNOWLEDGE_INDEX_VERSION).strip()
    target = create_building_index_version(
        version_name,
        settings.RETRIEVAL_MODEL_PROVIDER,
        settings.EMBEDDING_MODEL,
        settings.EMBEDDING_DIMENSIONS,
    )
    if target["status"] == "active":
        return {
            "source": source_name or "active_postgres_index",
            "target": version_name,
            "source_count": int(target["document_count"]),
            "embedded_count": 0,
            "target_count": int(target["document_count"]),
        }

    actual_batch_size = max(1, int(batch_size or settings.EMBEDDING_BATCH_SIZE))
    embedded_count = 0
    model = get_embedding_model()
    rows: list[dict] = []
    expected_ids: set[str] = set()
    for attempt in range(3):
        rows = list_active_chunks_for_reindex()
        expected_ids = {row["chunk_id"] for row in rows}
        existing_ids = get_index_chunk_ids(str(target["id"]))
        pending = [row for row in rows if row["chunk_id"] not in existing_ids]
        for start in range(0, len(pending), actual_batch_size):
            batch = pending[start:start + actual_batch_size]
            embeddings = model.embed_documents([row["content"] for row in batch])
            embedded_count += upsert_reindexed_chunks(str(target["id"]), batch, embeddings)
        try:
            activate_rebuilt_index(str(target["id"]), expected_ids)
            break
        except KnowledgeStoreError as exc:
            if exc.code != "KNOWLEDGE_REINDEX_SOURCE_CHANGED" or attempt == 2:
                raise
    return {
        "source": source_name or "active_postgres_index",
        "target": version_name,
        "source_count": len(rows),
        "embedded_count": embedded_count,
        "target_count": len(expected_ids),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="安全重建 PostgreSQL/pgvector 知识索引。")
    parser.add_argument("--target", default=settings.KNOWLEDGE_INDEX_VERSION)
    parser.add_argument("--batch-size", type=int, default=settings.EMBEDDING_BATCH_SIZE)
    args = parser.parse_args()
    print(rebuild_vector_collection(target_name=args.target, batch_size=args.batch_size))


if __name__ == "__main__":
    main()
