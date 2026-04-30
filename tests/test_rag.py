import pytest

from utils.rag import KnowledgeRetriever


class TestChunkDocument:
    def test_short_document_single_chunk(self):
        text = "This is a short document with only a few words."
        chunks = KnowledgeRetriever._chunk_document(text, "test.md")
        assert len(chunks) == 1
        assert chunks[0]["source"] == "test.md"
        assert chunks[0]["text"] == text

    def test_long_document_multiple_chunks(self):
        words = ["word"] * 1000
        text = " ".join(words)
        chunks = KnowledgeRetriever._chunk_document(text, "long.md", chunk_size=500, overlap=100)
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk["source"] == "long.md"
            assert len(chunk["text"]) > 0

    def test_overlap_creates_redundancy(self):
        words = ["word"] * 800
        text = " ".join(words)
        chunks = KnowledgeRetriever._chunk_document(text, "test.md", chunk_size=500, overlap=100)
        assert len(chunks) == 2

    def test_preserves_source(self):
        chunks = KnowledgeRetriever._chunk_document("hello world", "roles/pm.md")
        assert chunks[0]["source"] == "roles/pm.md"

    def test_empty_text(self):
        chunks = KnowledgeRetriever._chunk_document("", "empty.md")
        assert len(chunks) == 1

    def test_exact_chunk_size(self):
        words = ["word"] * 500
        text = " ".join(words)
        chunks = KnowledgeRetriever._chunk_document(text, "exact.md", chunk_size=500)
        assert len(chunks) == 1


class TestCosineSimilarity:
    def test_identical_vectors(self):
        a = [1.0, 2.0, 3.0]
        score = KnowledgeRetriever._cosine_similarity(a, a)
        assert abs(score - 1.0) < 1e-6

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        score = KnowledgeRetriever._cosine_similarity(a, b)
        assert abs(score) < 1e-6

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        score = KnowledgeRetriever._cosine_similarity(a, b)
        assert abs(score + 1.0) < 1e-6

    def test_zero_vector_returns_zero(self):
        a = [0.0, 0.0, 0.0]
        b = [1.0, 2.0, 3.0]
        score = KnowledgeRetriever._cosine_similarity(a, b)
        assert score == 0.0

    def test_similar_vectors_high_score(self):
        a = [1.0, 2.0, 3.0]
        b = [1.1, 2.1, 3.1]
        score = KnowledgeRetriever._cosine_similarity(a, b)
        assert score > 0.99


class TestLoadDocuments:
    def test_finds_knowledge_base_files(self):
        docs = KnowledgeRetriever._load_documents()
        assert len(docs) > 0
        for doc in docs:
            assert "path" in doc
            assert "content" in doc
            assert len(doc["content"]) > 0

    def test_includes_role_files(self):
        docs = KnowledgeRetriever._load_documents()
        paths = [d["path"] for d in docs]
        role_files = [p for p in paths if p.startswith("roles/")]
        assert len(role_files) >= 7

    def test_includes_framework_files(self):
        docs = KnowledgeRetriever._load_documents()
        paths = [d["path"] for d in docs]
        framework_files = [p for p in paths if p.startswith("frameworks/")]
        assert len(framework_files) >= 4

    def test_includes_rubric_files(self):
        docs = KnowledgeRetriever._load_documents()
        paths = [d["path"] for d in docs]
        rubric_files = [p for p in paths if p.startswith("rubrics/")]
        assert len(rubric_files) >= 3


class TestBuildIndexNoClient:
    @pytest.mark.asyncio
    async def test_builds_without_client(self):
        retriever = KnowledgeRetriever(client=None)
        count = await retriever.build_index()
        assert count >= 0

    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_without_client(self):
        retriever = KnowledgeRetriever(client=None)
        await retriever.build_index()
        result = await retriever.retrieve("test query")
        assert result == ""
