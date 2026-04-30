import pytest

from models import (
    CandidateProfile,
    FeedbackReport,
    FocusArea,
    InterviewPlan,
    InterviewResult,
    TurnEvaluation,
)
from orchestrator import InterviewEngine
from utils.mock_llm import MockLLMClient


@pytest.fixture
def engine():
    return InterviewEngine(llm=MockLLMClient())


@pytest.fixture
def profile():
    return CandidateProfile(name="Test", target_role="Product Manager", focus_area=FocusArea.mixed)


@pytest.mark.asyncio
class TestStartInterview:
    async def test_returns_plan_and_question(self, engine, profile):
        plan, question = await engine.start_interview(profile)
        assert isinstance(plan, InterviewPlan)
        assert isinstance(question, str)
        assert len(question) > 0

    async def test_initializes_state(self, engine, profile):
        await engine.start_interview(profile)
        assert engine.state_manager is not None
        assert engine.state_manager.current_turn == 1

    async def test_plan_has_topics(self, engine, profile):
        plan, _ = await engine.start_interview(profile)
        assert len(plan.topics) > 0

    async def test_first_message_in_conversation(self, engine, profile):
        await engine.start_interview(profile)
        assert len(engine.state_manager.conversation) == 1
        assert engine.state_manager.conversation[0].role == "interviewer"


@pytest.mark.asyncio
class TestSubmitAnswer:
    async def test_returns_question_and_evaluation(self, engine, profile):
        await engine.start_interview(profile)
        next_q, evaluation = await engine.submit_answer("I led a team of 5 engineers.")
        assert isinstance(evaluation, TurnEvaluation)
        assert isinstance(next_q, str) or next_q is None

    async def test_returns_none_when_concluding(self, engine, profile):
        await engine.start_interview(profile)
        concluded = False
        for i in range(10):
            next_q, _ = await engine.submit_answer(f"Answer {i}")
            if next_q is None:
                concluded = True
                break
        assert concluded

    async def test_adds_candidate_message(self, engine, profile):
        await engine.start_interview(profile)
        await engine.submit_answer("My answer")
        candidate_msgs = [m for m in engine.state_manager.conversation if m.role == "candidate"]
        assert len(candidate_msgs) == 1
        assert candidate_msgs[0].content == "My answer"


@pytest.mark.asyncio
class TestEndInterview:
    async def test_returns_feedback_report(self, engine, profile):
        await engine.start_interview(profile)
        await engine.submit_answer("Test answer")
        feedback = await engine.end_interview()
        assert isinstance(feedback, FeedbackReport)

    async def test_feedback_has_rating(self, engine, profile):
        await engine.start_interview(profile)
        await engine.submit_answer("Test answer")
        feedback = await engine.end_interview()
        assert feedback.overall_rating in ["Strong Hire", "Hire", "Lean Hire", "Lean No Hire", "No Hire"]


@pytest.mark.asyncio
class TestGetResult:
    async def test_assembles_complete_result(self, engine, profile):
        await engine.start_interview(profile)
        await engine.submit_answer("Test answer")
        await engine.end_interview()
        result = engine.get_result()
        assert isinstance(result, InterviewResult)
        assert result.profile == profile
        assert len(result.conversation) > 0
        assert len(result.evaluations) > 0
        assert result.feedback is not None


@pytest.mark.asyncio
class TestGetState:
    async def test_before_start(self, engine):
        state = engine.get_state()
        assert state["state"] == "not_started"

    async def test_during_interview(self, engine, profile):
        await engine.start_interview(profile)
        state = engine.get_state()
        assert state["current_turn"] == 1
        assert state["max_turns"] > 0
        assert "current_topic" in state
        assert "topics_remaining" in state

    async def test_state_updates_after_answer(self, engine, profile):
        await engine.start_interview(profile)
        state_before = engine.get_state()
        await engine.submit_answer("Test answer")
        state_after = engine.get_state()
        assert state_after["current_turn"] >= state_before["current_turn"]


@pytest.mark.asyncio
class TestFullFlow:
    async def test_complete_interview(self, engine, profile):
        plan, first_q = await engine.start_interview(profile)
        assert isinstance(first_q, str)

        answers_given = 0
        for i in range(plan.total_turns + 2):
            next_q, evaluation = await engine.submit_answer(f"Answer {i}")
            answers_given += 1
            if next_q is None:
                break

        await engine.end_interview()
        result = engine.get_result()

        assert answers_given >= 1
        assert len(result.evaluations) == answers_given
        assert isinstance(result.feedback, FeedbackReport)
