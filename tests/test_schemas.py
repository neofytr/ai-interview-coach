import pytest
from pydantic import ValidationError

from models import (
    CandidateProfile,
    DimensionScore,
    EvaluationDimension,
    EvaluatorSignal,
    FocusArea,
    InterviewPlan,
    InterviewState,
    Message,
    TurnEvaluation,
)


class TestFocusArea:
    def test_valid_values(self):
        assert FocusArea.behavioral == "behavioral"
        assert FocusArea.technical == "technical"
        assert FocusArea.case == "case"
        assert FocusArea.mixed == "mixed"


class TestCandidateProfile:
    def test_valid_creation(self):
        profile = CandidateProfile(name="Alex", target_role="PM", focus_area=FocusArea.mixed)
        assert profile.target_role == "PM"
        assert profile.name == "Alex"

    def test_optional_background_defaults_none(self):
        profile = CandidateProfile(name="Alex", target_role="PM", focus_area=FocusArea.mixed)
        assert profile.background is None

    def test_default_experience_level(self):
        profile = CandidateProfile(name="Alex", target_role="PM", focus_area=FocusArea.mixed)
        assert profile.experience_level == "mid"

    def test_accepts_background(self):
        profile = CandidateProfile(name="Alex", target_role="PM", focus_area=FocusArea.mixed, background="5 years exp")
        assert profile.background == "5 years exp"

    def test_accepts_none_background(self):
        profile = CandidateProfile(name="Alex", target_role="PM", focus_area=FocusArea.mixed, background=None)
        assert profile.background is None


class TestDimensionScore:
    def test_valid_score(self):
        ds = DimensionScore(dimension="Comm", score=7, justification="Good")
        assert ds.score == 7

    def test_rejects_zero(self):
        with pytest.raises(ValidationError):
            DimensionScore(dimension="Comm", score=0, justification="Too low")

    def test_rejects_eleven(self):
        with pytest.raises(ValidationError):
            DimensionScore(dimension="Comm", score=11, justification="Too high")

    def test_accepts_one(self):
        ds = DimensionScore(dimension="Comm", score=1, justification="Minimum")
        assert ds.score == 1

    def test_accepts_ten(self):
        ds = DimensionScore(dimension="Comm", score=10, justification="Maximum")
        assert ds.score == 10


class TestEvaluationDimension:
    def test_valid_weight(self):
        dim = EvaluationDimension(name="Comm", description="test", weight=0.5)
        assert dim.weight == 0.5

    def test_rejects_negative_weight(self):
        with pytest.raises(ValidationError):
            EvaluationDimension(name="Comm", description="test", weight=-0.1)

    def test_rejects_above_one(self):
        with pytest.raises(ValidationError):
            EvaluationDimension(name="Comm", description="test", weight=1.1)

    def test_accepts_zero_weight(self):
        dim = EvaluationDimension(name="Comm", description="test", weight=0.0)
        assert dim.weight == 0.0

    def test_accepts_one_weight(self):
        dim = EvaluationDimension(name="Comm", description="test", weight=1.0)
        assert dim.weight == 1.0


class TestInterviewPlan:
    def test_rejects_zero_turns(self):
        with pytest.raises(ValidationError):
            InterviewPlan(
                role_context="ctx",
                topics=[],
                evaluation_dimensions=[],
                difficulty_progression="gradual",
                opening_message="Hi",
                total_turns=0,
            )

    def test_rejects_sixteen_turns(self):
        with pytest.raises(ValidationError):
            InterviewPlan(
                role_context="ctx",
                topics=[],
                evaluation_dimensions=[],
                difficulty_progression="gradual",
                opening_message="Hi",
                total_turns=16,
            )

    def test_accepts_valid_turns(self, sample_plan):
        assert sample_plan.total_turns == 5

    def test_valid_creation(self, sample_plan):
        assert len(sample_plan.topics) == 3
        assert len(sample_plan.evaluation_dimensions) == 5


class TestEvaluatorSignal:
    def test_all_signal_values(self):
        values = {s.value for s in EvaluatorSignal}
        assert values == {"probe_deeper", "move_on", "increase_difficulty", "decrease_difficulty", "redirect"}


class TestTurnEvaluation:
    def test_optional_follow_up_none(self):
        ev = TurnEvaluation(
            turn_number=1,
            dimension_scores=[],
            overall_score=5.0,
            strengths=[],
            weaknesses=[],
            signals=[],
            follow_up_suggestion=None,
        )
        assert ev.follow_up_suggestion is None

    def test_with_follow_up(self, sample_evaluation):
        assert sample_evaluation.follow_up_suggestion is not None

    def test_valid_creation(self, sample_evaluation):
        assert sample_evaluation.turn_number == 1
        assert len(sample_evaluation.signals) == 1


class TestMessage:
    def test_valid_creation(self):
        msg = Message(role="interviewer", content="Hello", turn_number=0)
        assert msg.role == "interviewer"
        assert msg.turn_number == 0


class TestInterviewState:
    def test_all_states_present(self):
        values = {s.value for s in InterviewState}
        expected = {"planning", "interviewing", "evaluating", "following_up", "concluding", "coaching", "done"}
        assert values == expected
