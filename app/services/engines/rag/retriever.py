from typing import List, Dict, Any, Optional
from app.services.engines.rag.embeddings import EmbeddingProvider
from app.models.journal import GuidelineVersion, GuidelineChunk


class GuidelineRetriever:
    """
    Retrieves official guideline passages with strict metadata filtering to prevent cross-journal leakage.
    """

    @classmethod
    def retrieve_relevant_chunks(
        cls,
        query: str,
        guideline_version: GuidelineVersion,
        top_k: int = 3,
        threshold: float = 0.15,
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic search strictly filtered by the specific guideline_version.id.
        """
        if not guideline_version or not guideline_version.chunks:
            return []

        query_vec = EmbeddingProvider.get_embedding(query)
        scored_chunks: List[Dict[str, Any]] = []

        for chunk in guideline_version.chunks:
            # Metadata isolation check: chunk must strictly belong to this guideline_version
            if chunk.guideline_version_id != guideline_version.id:
                continue

            chunk_vec = chunk.embedding
            if not chunk_vec:
                # Fallback embed dynamically if needed
                text = f"{chunk.section_heading or ''} {chunk.content}"
                chunk_vec = EmbeddingProvider.get_embedding(text)

            sim = EmbeddingProvider.cosine_similarity(query_vec, chunk_vec)
            if sim >= threshold:
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "section_heading": chunk.section_heading,
                    "content": chunk.content,
                    "source_url": chunk.source_url,
                    "similarity": round(sim, 4),
                })

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:top_k]
