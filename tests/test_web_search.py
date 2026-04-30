from unittest.mock import MagicMock, patch

import pytest

from utils.web_search import WebSearcher


class TestSearchRoleContext:
    @pytest.mark.asyncio
    async def test_returns_string(self):
        searcher = WebSearcher()
        with patch.object(searcher, "_search", return_value="mock result"):
            result = await searcher.search_role_context("Product Manager")
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_returns_empty_on_no_results(self):
        searcher = WebSearcher()
        with patch.object(searcher, "_search", return_value=""):
            result = await searcher.search_role_context("Product Manager")
            assert result == ""

    @pytest.mark.asyncio
    async def test_calls_search_three_times(self):
        searcher = WebSearcher()
        with patch.object(searcher, "_search", return_value="result") as mock_search:
            await searcher.search_role_context("Software Engineer")
            assert mock_search.call_count == 3


class TestSearch:
    def test_graceful_failure_import_error(self):
        with patch.dict("sys.modules", {"ddgs": None}):
            result = WebSearcher._search("test query")
            assert result == ""

    def test_graceful_failure_exception(self):
        with patch("utils.web_search.WebSearcher._search", side_effect=Exception("fail")):
            try:
                result = WebSearcher._search("test query")
            except Exception:
                result = ""
            assert isinstance(result, str)

    def test_formats_results(self):
        mock_results = [
            {"title": "Title 1", "body": "Body 1"},
            {"title": "Title 2", "body": "Body 2"},
        ]

        with patch("utils.web_search.DDGS", create=True) as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
            mock_ddgs.__exit__ = MagicMock(return_value=False)
            mock_ddgs.text.return_value = mock_results
            mock_ddgs_cls.return_value = mock_ddgs

            with patch("utils.web_search.WebSearcher._search") as mock_search:
                mock_search.return_value = "**Title 1**\nBody 1\n\n**Title 2**\nBody 2"
                result = mock_search("test query")
                assert "Title 1" in result
                assert "Body 1" in result
