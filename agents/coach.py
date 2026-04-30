from agents.base import BaseAgent
from models import (
    CandidateProfile,
    FeedbackReport,
    InterviewPlan,
    Message,
    TurnEvaluation,
)
from utils import LLMClient


class CoachAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("coach", llm)

    async def generate_feedback(
        self,
        profile: CandidateProfile,
        plan: InterviewPlan,
        conversation: list[Message],
        evaluations: list[TurnEvaluation],
    ) -> FeedbackReport:
        transcript = "\n".join(
            f"{msg.role.capitalize()}: {msg.content}"
            for msg in conversation
        )
        evals_json = (
            "[\n"
            + ",\n".join(e.model_dump_json(indent=2) for e in evaluations)
            + "\n]"
        )
        user_message = (
            f"<candidate_profile>\n{profile.model_dump_json(indent=2)}\n</candidate_profile>\n\n"
            f"<interview_plan>\n{plan.model_dump_json(indent=2)}\n</interview_plan>\n\n"
            f"<transcript>\n{transcript}\n</transcript>\n\n"
            f"<turn_evaluations>\n{evals_json}\n</turn_evaluations>"
        )
        return await self.llm.call_json(
            system_prompt=self.system_prompt,
            user_message=user_message,
            response_model=FeedbackReport,
        )
