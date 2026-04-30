import json
import math
from pathlib import Path

from openai import AsyncOpenAI

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger("rag")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge_base"
CACHE_PATH = PROJECT_ROOT / ".embedding_cache.json"


class KnowledgeRetriever:
    def __init__(self, client: AsyncOpenAI | None = None) -> None:
        settings = get_settings()
        self._client = client
        self._model = settings.embedding_model
        self._chunks: list[dict] = []
        self._embeddings: list[list[float]] = []

    async def build_index(self) -> int:
        documents = self._load_documents()
        if not documents:
            logger.warning("No knowledge base documents found")
            return 0

        self._chunks = []
        for doc in documents:
            self._chunks.extend(self._chunk_document(doc["content"], doc["path"]))

        cached = self._load_cache()
        uncached_indices = []
        self._embeddings = [[] for _ in self._chunks]

        for i, chunk in enumerate(self._chunks):
            cache_key = chunk["text"][:200]
            if cache_key in cached:
                self._embeddings[i] = cached[cache_key]
            else:
                uncached_indices.append(i)

        if uncached_indices and self._client:
            texts = [self._chunks[i]["text"] for i in uncached_indices]
            try:
                response = await self._client.embeddings.create(model=self._model, input=texts)
                for j, idx in enumerate(uncached_indices):
                    embedding = response.data[j].embedding
                    self._embeddings[idx] = embedding
                    cache_key = self._chunks[idx]["text"][:200]
                    cached[cache_key] = embedding
                self._save_cache(cached)
            except Exception as exc:
                logger.warning("Embedding API call failed: %s", exc)
                self._chunks = [c for i, c in enumerate(self._chunks) if self._embeddings[i]]
                self._embeddings = [e for e in self._embeddings if e]

        elif uncached_indices:
            self._chunks = [c for i, c in enumerate(self._chunks) if self._embeddings[i]]
            self._embeddings = [e for e in self._embeddings if e]

        logger.debug("Built index with %d chunks from %d documents", len(self._chunks), len(documents))
        return len(self._chunks)

    async def retrieve(self, query: str, top_k: int = 5) -> str:
        if not self._chunks or not self._client:
            return ""

        try:
            response = await self._client.embeddings.create(model=self._model, input=[query])
            query_embedding = response.data[0].embedding
        except Exception as exc:
            logger.warning("Query embedding failed: %s", exc)
            return ""

        scored = []
        for i, emb in enumerate(self._embeddings):
            if emb:
                score = self._cosine_similarity(query_embedding, emb)
                scored.append((score, i))

        scored.sort(reverse=True)
        top_chunks = scored[:top_k]

        results = []
        for score, idx in top_chunks:
            chunk = self._chunks[idx]
            results.append(f"[{chunk['source']}] (relevance: {score:.2f})\n{chunk['text']}")

        return "\n\n---\n\n".join(results)

    @staticmethod
    def _chunk_document(text: str, source: str, chunk_size: int = 500, overlap: int = 100) -> list[dict]:
        words = text.split()
        if len(words) <= chunk_size:
            return [{"text": text.strip(), "source": source}]

        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_text = " ".join(words[start:end])
            chunks.append({"text": chunk_text.strip(), "source": source})
            start += chunk_size - overlap

        return chunks

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def _load_documents() -> list[dict]:
        docs = []
        if not KNOWLEDGE_DIR.exists():
            return docs
        for md_file in sorted(KNOWLEDGE_DIR.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8").strip()
            if content:
                relative = md_file.relative_to(KNOWLEDGE_DIR)
                docs.append({"path": str(relative), "content": content})
        return docs

    @staticmethod
    def _load_cache() -> dict:
        if CACHE_PATH.exists():
            try:
                with open(CACHE_PATH, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    @staticmethod
    def _save_cache(cache: dict) -> None:
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(cache, f)
        except OSError as exc:
            logger.warning("Failed to save embedding cache: %s", exc)
