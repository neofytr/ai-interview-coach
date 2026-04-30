from agents.base import BaseAgent
from models import EvaluationDimension, TurnEvaluation
from utils import LLMClient


class EvaluatorAgent(BaseAgent):
    def __init__(self, llm: LLMClient) -> None:
        super().__init__("evaluator", llm)

    async def evaluate(
        self,
        question: str,
        answer: str,
        turn_number: int,
        dimensions: list[EvaluationDimension],
        role_context: str,
    ) -> TurnEvaluation:
        dims_text = "\n".join(
            f"- {d.name} (weight: {d.weight}): {d.description}"
            for d in dimensions
        )
        user_message = (
            f"<role_context>\n{role_context}\n</role_context>\n\n"
            f"<turn_number>{turn_number}</turn_number>\n\n"
            f"<question>\n{question}\n</question>\n\n"
            f"<answer>\n{answer}\n</answer>\n\n"
            f"<evaluation_dimensions>\n{dims_text}\n</evaluation_dimensions>"
        )
        return await self.llm.call_json(
            system_prompt=self.system_prompt,
            user_message=user_message,
            response_model=TurnEvaluation,
        )
