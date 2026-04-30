from agents import CoachAgent, EvaluatorAgent, InterviewerAgent, PlannerAgent
from models import (
    CandidateProfile,
    FeedbackReport,
    InterviewPlan,
    InterviewResult,
    TurnEvaluation,
)
from orchestrator.state import InterviewStateManager
from utils import LLMClient
from utils.logger import get_logger

logger = get_logger("engine")


class InterviewEngine:
    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()
        self.planner = PlannerAgent(self._llm)
        self.interviewer = InterviewerAgent(self._llm)
        self.evaluator = EvaluatorAgent(self._llm)
        self.coach = CoachAgent(self._llm)
        self.state_manager: InterviewStateManager | None = None
        self._profile: CandidateProfile | None = None
        self._feedback: FeedbackReport | None = None

    async def start_interview(self, profile: CandidateProfile) -> tuple[InterviewPlan, str]:
        self._profile = profile
        logger.debug("Starting interview for role: %s", profile.target_role)
        plan = await self.planner.create_plan(profile)
        logger.debug("Plan created: %d topics, %d turns", len(plan.topics), plan.total_turns)
        self.state_manager = InterviewStateManager(plan)

        first_question = await self.interviewer.generate_question(
            plan=plan,
            conversation=[],
        )
        self.state_manager.add_message("interviewer", first_question)
        self.state_manager.current_turn += 1

        return plan, first_question

    async def submit_answer(self, answer: str) -> tuple[str | None, TurnEvaluation]:
        sm = self.state_manager
        assert sm is not None

        sm.add_message("candidate", answer)

        evaluation = await self.evaluator.evaluate(
            question=sm.get_last_question(),
            answer=answer,
            turn_number=sm.current_turn,
            dimensions=sm.plan.evaluation_dimensions,
            role_context=sm.plan.role_context,
        )
        sm.add_evaluation(evaluation)

        if sm.should_conclude():
            logger.debug("Interview concluding (turn %d/%d)", sm.current_turn, sm.max_turns)
            return None, evaluation

        action = sm.decide_next_action(evaluation)
        logger.debug(
            "Turn %d: action=%s, score=%.1f, signals=%s",
            sm.current_turn,
            action,
            evaluation.overall_score,
            [s.value for s in evaluation.signals],
        )
        if action == "conclude":
            return None, evaluation

        if action == "next_topic":
            sm.advance_topic()

        next_question = await self.interviewer.generate_question(
            plan=sm.plan,
            conversation=sm.conversation,
            evaluation_signals=evaluation.signals,
            follow_up_suggestion=evaluation.follow_up_suggestion,
        )
        sm.add_message("interviewer", next_question)
        sm.current_turn += 1

        return next_question, evaluation

    async def end_interview(self) -> FeedbackReport:
        sm = self.state_manager
        assert sm is not None
        assert self._profile is not None
        logger.debug("Generating feedback from %d evaluations", len(sm.evaluations))

        self._feedback = await self.coach.generate_feedback(
            profile=self._profile,
            plan=sm.plan,
            conversation=sm.conversation,
            evaluations=sm.evaluations,
        )
        return self._feedback

    def get_state(self) -> dict:
        sm = self.state_manager
        if sm is None:
            return {"state": "not_started"}
        topic_name = sm.get_current_topic().name if sm.current_topic_index < len(sm.plan.topics) else "Complete"
        return {
            "state": sm.state.value,
            "current_turn": sm.current_turn,
            "max_turns": sm.max_turns,
            "current_topic": topic_name,
            "topics_remaining": max(0, len(sm.plan.topics) - sm.current_topic_index),
        }

    def get_result(self) -> InterviewResult:
        sm = self.state_manager
        assert sm is not None
        assert self._profile is not None
        assert self._feedback is not None

        return InterviewResult(
            profile=self._profile,
            plan=sm.plan,
            conversation=sm.conversation,
            evaluations=sm.evaluations,
            feedback=self._feedback,
        )
