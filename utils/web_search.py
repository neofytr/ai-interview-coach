from utils.logger import get_logger

logger = get_logger("web_search")


class WebSearcher:
    async def search_role_context(self, role: str) -> str:
        queries = [
            f"{role} interview questions and what interviewers look for",
            f"{role} key skills competencies hiring criteria",
            f"{role} common interview mistakes and best practices",
        ]

        all_results = []
        for query in queries:
            result = self._search(query)
            if result:
                all_results.append(result)

        if not all_results:
            logger.debug("No web search results for role: %s", role)
            return ""

        combined = "\n\n".join(all_results)
        logger.debug("Web search returned %d characters for role: %s", len(combined), role)
        return combined

    @staticmethod
    def _search(query: str, max_results: int = 3) -> str:
        try:
            from ddgs import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return ""

            lines = []
            for r in results:
                title = r.get("title", "")
                body = r.get("body", "")
                if title and body:
                    lines.append(f"**{title}**\n{body}")

            return "\n\n".join(lines)

        except ImportError:
            logger.debug("ddgs not installed — web search disabled")
            return ""
        except Exception as exc:
            logger.warning("Web search failed for query '%s': %s", query, exc)
            return ""
