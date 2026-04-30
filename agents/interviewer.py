from agents.base import BaseAgent
from models import EvaluatorSignal, InterviewPlan, Message
from utils import LLMClient


class InterviewerAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("interviewer", llm)

    async def generate_question(
        self,
        plan: InterviewPlan,
        conversation: list[Message],
        evaluation_signals: list[EvaluatorSignal] | None = None,
        follow_up_suggestion: str | None = None,
    ) -> str:
        if conversation:
            conv_lines = "\n".join(
                f"{msg.role.capitalize()}: {msg.content}"
                for msg in conversation
            )
        else:
            conv_lines = "No conversation yet — this is the opening question."

        if evaluation_signals:
            signals_text = ", ".join(s.value for s in evaluation_signals)
        else:
            signals_text = "No signals — this is the opening question."

        suggestion_text = follow_up_suggestion or "None"

        user_message = (
            f"<interview_plan>\n{plan.model_dump_json(indent=2)}\n</interview_plan>\n\n"
            f"<conversation_history>\n{conv_lines}\n</conversation_history>\n\n"
            f"<evaluator_signals>\n{signals_text}\n</evaluator_signals>\n\n"
            f"<follow_up_suggestion>\n{suggestion_text}\n</follow_up_suggestion>\n\n"
            "Generate the next interviewer message."
        )
        return await self.llm.call(
            system_prompt=self.system_prompt,
            user_message=user_message,
        )
