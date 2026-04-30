import json

from agents.base import BaseAgent
from models import CandidateProfile, FocusArea, InterviewPlan
from utils import LLMClient


class PlannerAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("planner", llm)

    async def create_plan(self, profile: CandidateProfile) -> InterviewPlan:
        bank = LLMClient.load_question_bank()
        relevant = self._filter_questions(bank, profile.focus_area)

        user_message = profile.model_dump_json(indent=2)
        if relevant:
            user_message += f"\n\n<question_bank>\n{json.dumps(relevant, indent=2)}\n</question_bank>"

        return await self.llm.call_json(
            system_prompt=self.system_prompt,
            user_message=user_message,
            response_model=InterviewPlan,
        )

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
