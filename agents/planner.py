from agents.base import BaseAgent
from models import CandidateProfile, InterviewPlan
from utils import LLMClient


class PlannerAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("planner", llm)

    async def create_plan(self, profile: CandidateProfile) -> InterviewPlan:
        return await self.llm.call_json(
            system_prompt=self.system_prompt,
            user_message=profile.model_dump_json(indent=2),
            response_model=InterviewPlan,
        )
