import pytest

from agents import CoachAgent, EvaluatorAgent, InterviewerAgent, PlannerAgent
from agents.base import BaseAgent
from models import (
    CandidateProfile,
    DimensionScore,
    EvaluationDimension,
    EvaluatorSignal,
    FeedbackReport,
    FocusArea,
    InterviewPlan,
    Message,
    TurnEvaluation,
)
from utils.mock_llm import MockLLMClient


@pytest.fixture
def mock_llm():
    return MockLLMClient()


class TestBaseAgent:
    def test_loads_nonempty_prompt(self, mock_llm):
        agent = BaseAgent("planner", mock_llm)
        assert len(agent.system_prompt) > 0

    def test_prompt_contains_agent_name(self, mock_llm):
        agent = BaseAgent("planner", mock_llm)
        assert "Planner" in agent.system_prompt

    def test_stores_llm_reference(self, mock_llm):
        agent = BaseAgent("planner", mock_llm)
        assert agent.llm is mock_llm


@pytest.mark.asyncio
class TestPlannerAgent:
    async def test_create_plan_returns_interview_plan(self, mock_llm):
        agent = PlannerAgent(mock_llm)
        profile = CandidateProfile(name="Test", target_role="PM", focus_area=FocusArea.mixed)
        plan = await agent.create_plan(profile)
        assert isinstance(plan, InterviewPlan)

    async def test_plan_has_topics(self, mock_llm):
        agent = PlannerAgent(mock_llm)
        profile = CandidateProfile(name="Test", target_role="PM", focus_area=FocusArea.mixed)
        plan = await agent.create_plan(profile)
        assert len(plan.topics) > 0

    async def test_plan_has_dimensions(self, mock_llm):
        agent = PlannerAgent(mock_llm)
        profile = CandidateProfile(name="Test", target_role="PM", focus_area=FocusArea.mixed)
        plan = await agent.create_plan(profile)
        assert len(plan.evaluation_dimensions) > 0


@pytest.mark.asyncio
class TestEvaluatorAgent:
    async def test_evaluate_returns_turn_evaluation(self, mock_llm):
        agent = EvaluatorAgent(mock_llm)
        dims = [EvaluationDimension(name="Comm", description="Communication", weight=1.0)]
        result = await agent.evaluate(
            question="Tell me about leadership",
            answer="I led a team of 5",
            turn_number=1,
            dimensions=dims,
            role_context="PM role",
        )
        assert isinstance(result, TurnEvaluation)

    async def test_evaluation_has_scores(self, mock_llm):
        agent = EvaluatorAgent(mock_llm)
        dims = [EvaluationDimension(name="Comm", description="Communication", weight=1.0)]
        result = await agent.evaluate(
            question="Q",
            answer="A",
            turn_number=1,
            dimensions=dims,
            role_context="ctx",
        )
        assert len(result.dimension_scores) > 0


@pytest.mark.asyncio
class TestInterviewerAgent:
    async def test_returns_string(self, mock_llm, sample_plan):
        agent = InterviewerAgent(mock_llm)
        question = await agent.generate_question(plan=sample_plan, conversation=[])
        assert isinstance(question, str)
        assert len(question) > 0

    async def test_not_json(self, mock_llm, sample_plan):
        agent = InterviewerAgent(mock_llm)
        question = await agent.generate_question(plan=sample_plan, conversation=[])
        assert not question.strip().startswith("{")

    async def test_accepts_signals(self, mock_llm, sample_plan):
        agent = InterviewerAgent(mock_llm)
        question = await agent.generate_question(
            plan=sample_plan,
            conversation=[Message(role="interviewer", content="Q1", turn_number=1)],
            evaluation_signals=[EvaluatorSignal.probe_deeper],
            follow_up_suggestion="Ask about specifics",
        )
        assert isinstance(question, str)


@pytest.mark.asyncio
class TestCoachAgent:
    async def test_returns_feedback_report(self, mock_llm, sample_plan):
        agent = CoachAgent(mock_llm)
        profile = CandidateProfile(name="Test", target_role="PM", focus_area=FocusArea.mixed)
        conversation = [
            Message(role="interviewer", content="Tell me about leadership", turn_number=1),
            Message(role="candidate", content="I led a team", turn_number=1),
        ]
        evals = [
            TurnEvaluation(
                turn_number=1,
                dimension_scores=[DimensionScore(dimension="Comm", score=7, justification="Good")],
                overall_score=7.0,
                strengths=["Strong communication"],
                weaknesses=["Lacked depth"],
                signals=[EvaluatorSignal.move_on],
            )
        ]
        feedback = await agent.generate_feedback(
            profile=profile,
            plan=sample_plan,
            conversation=conversation,
            evaluations=evals,
        )
        assert isinstance(feedback, FeedbackReport)
        assert len(feedback.strengths) > 0
