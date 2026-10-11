import math
import hashlib
from typing import List


class EmbeddingProvider:
    """
    Embedding service supporting deterministic fast semantic hashing for zero-dependency local execution,
    extensible to SentenceTransformers or OpenAI.
    """

    DIMENSION = 384

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        # Fast, deterministic semantic-aware n-gram projection
        clean = text.lower().strip()
        vec = [0.0] * cls.DIMENSION
        if not clean:
            return vec

        words = clean.split()
        for w_idx, word in enumerate(words):
            # Generate deterministic hashes for character trigrams
            for i in range(len(word) - 2):
                tri = word[i : i + 3]
                h = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16)
                idx = h % cls.DIMENSION
                vec[idx] += 1.0

            # Whole word feature
            wh = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            w_idx_mod = wh % cls.DIMENSION
            vec[w_idx_mod] += 2.0

        # L2 normalize vector
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @classmethod
    def cosine_similarity(cls, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        return max(0.0, min(1.0, dot))
