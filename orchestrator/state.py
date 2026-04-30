from collections import defaultdict

from models import (
    EvaluatorSignal,
    InterviewPlan,
    InterviewState,
    InterviewTopic,
    Message,
    TurnEvaluation,
)


class InterviewStateManager:
    def __init__(self, plan: InterviewPlan) -> None:
        self.plan = plan
        self.state = InterviewState.interviewing
        self.conversation: list[Message] = []
        self.evaluations: list[TurnEvaluation] = []
        self.current_turn: int = 0
        self.current_topic_index: int = 0
        self.max_turns: int = plan.total_turns
        self._topic_followups: dict[int, int] = defaultdict(int)

    def add_message(self, role: str, content: str) -> None:
        self.conversation.append(
            Message(role=role, content=content, turn_number=self.current_turn)
        )

    def add_evaluation(self, evaluation: TurnEvaluation) -> None:
        self.evaluations.append(evaluation)

    def get_last_question(self) -> str:
        for msg in reversed(self.conversation):
            if msg.role == "interviewer":
                return msg.content
        return ""

    def should_conclude(self) -> bool:
        return (
            self.current_turn >= self.max_turns
            or self.current_topic_index >= len(self.plan.topics)
        )

    def decide_next_action(self, evaluation: TurnEvaluation) -> str:
        if self.should_conclude():
            return "conclude"

        signals = evaluation.signals
        topic_exhausted = self._topic_followups[self.current_topic_index] >= 2

        if EvaluatorSignal.probe_deeper in signals and not topic_exhausted:
            self._topic_followups[self.current_topic_index] += 1
            return "follow_up"

        if EvaluatorSignal.move_on in signals or topic_exhausted:
            return "next_topic"

        self._topic_followups[self.current_topic_index] += 1
        return "follow_up"

    def advance_topic(self) -> None:
        self.current_topic_index += 1

    def get_current_topic(self) -> InterviewTopic:
        return self.plan.topics[self.current_topic_index]
