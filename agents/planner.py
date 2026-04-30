import json

from agents.base import BaseAgent
from models import CandidateProfile, FocusArea, InterviewPlan
from utils import LLMClient
from utils.config import get_settings
from utils.logger import get_logger
from utils.rag import KnowledgeRetriever
from utils.web_search import WebSearcher

logger = get_logger("planner")


class PlannerAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("planner", llm)

    async def create_plan(self, profile: CandidateProfile) -> InterviewPlan:
        bank = LLMClient.load_question_bank()
        relevant = self._filter_questions(bank, profile.focus_area)

        user_message = profile.model_dump_json(indent=2)
        if relevant:
            user_message += f"\n\n<question_bank>\n{json.dumps(relevant, indent=2)}\n</question_bank>"

        settings = get_settings()

        if settings.enable_rag:
            knowledge = await self._get_rag_context(profile.target_role)
            if knowledge:
                user_message += f"\n\n<knowledge_context>\n{knowledge}\n</knowledge_context>"

        if settings.enable_web_search:
            web_context = await self._get_web_context(profile.target_role)
            if web_context:
                user_message += f"\n\n<web_search_results>\n{web_context}\n</web_search_results>"

        return await self.llm.call_json(
            system_prompt=self.system_prompt,
            user_message=user_message,
            response_model=InterviewPlan,
        )

    async def _get_rag_context(self, role: str) -> str:
        try:
            client = getattr(self.llm, "_client", None)
            retriever = KnowledgeRetriever(client=client)
            await retriever.build_index()
            result = await retriever.retrieve(f"{role} interview evaluation criteria", top_k=5)
            if result:
                logger.debug("RAG returned %d chars for role: %s", len(result), role)
            return result
        except Exception as exc:
            logger.warning("RAG retrieval failed: %s", exc)
            return ""

    @staticmethod
    async def _get_web_context(role: str) -> str:
        try:
            searcher = WebSearcher()
            result = await searcher.search_role_context(role)
            if result:
                logger.debug("Web search returned %d chars for role: %s", len(result), role)
            return result
        except Exception as exc:
            logger.warning("Web search failed: %s", exc)
            return ""

    @staticmethod
    def _filter_questions(bank: dict, focus_area: FocusArea) -> dict:
        if focus_area == FocusArea.mixed:
            return bank
        if focus_area == FocusArea.behavioral:
            return {"behavioral": bank.get("behavioral", {})}
        if focus_area == FocusArea.technical:
            return {"technical": bank.get("technical", {})}
        if focus_area == FocusArea.case:
            return {"case": bank.get("case", {})}
        return bank
