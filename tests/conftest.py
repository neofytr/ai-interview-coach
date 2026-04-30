import pytest

from models import (
    CandidateProfile,
    DimensionScore,
    EvaluationDimension,
    EvaluatorSignal,
    FeedbackReport,
    FocusArea,
    InterviewPlan,
    InterviewTopic,
    TurnEvaluation,
)
from utils.mock_llm import MockLLMClient


@pytest.fixture
def sample_profile():
    return CandidateProfile(
        name="Alex",
        target_role="Product Manager",
        focus_area=FocusArea.mixed,
    )


@pytest.fixture
def sample_plan():
    return InterviewPlan(
        role_context="A PM needs strong communication, analytical thinking, and stakeholder management.",
        topics=[
            InterviewTopic(
                name="Leadership",
                description="Leadership and team management experience",
                suggested_questions=["Tell me about a time you led a team.", "How do you handle conflict?"],
                difficulty="easy",
            ),
            InterviewTopic(
                name="Strategy",
                description="Strategic thinking and prioritization",
                suggested_questions=["How do you prioritize features?", "Describe a difficult tradeoff."],
                difficulty="medium",
            ),
            InterviewTopic(
                name="Execution",
                description="Delivery, metrics, and execution",
                suggested_questions=["Walk me through a launch.", "How do you measure success?"],
                difficulty="hard",
            ),
        ],
        evaluation_dimensions=[
            EvaluationDimension(name="Communication Clarity", description="Structure and articulation", weight=0.20),
            EvaluationDimension(name="Problem-Solving", description="Methodology and reasoning", weight=0.25),
            EvaluationDimension(name="Use of Examples", description="Concrete evidence and specifics", weight=0.20),
            EvaluationDimension(name="Critical Thinking", description="Analysis and tradeoffs", weight=0.20),
            EvaluationDimension(name="Self-Awareness", description="Growth mindset and honesty", weight=0.15),
        ],
        difficulty_progression="gradual",
        opening_message="Welcome to the interview!",
        total_turns=5,
    )


@pytest.fixture
def sample_evaluation():
    return TurnEvaluation(
        turn_number=1,
        dimension_scores=[
            DimensionScore(dimension="Communication Clarity", score=7, justification="Clear and structured"),
            DimensionScore(dimension="Problem-Solving", score=6, justification="Decent framework"),
        ],
        overall_score=6.5,
        strengths=["Clear communication"],
        weaknesses=["Lacked depth on tradeoffs"],
        signals=[EvaluatorSignal.probe_deeper],
        follow_up_suggestion="Ask about specific methodology used",
    )


@pytest.fixture
def sample_feedback():
    return FeedbackReport(
        overall_rating="Hire",
        overall_score=7.0,
        summary="Solid performance with good communication and structured thinking.",
        dimension_averages={"Communication Clarity": 7.5, "Problem-Solving": 6.8},
        strengths=["Strong structured communication", "Good use of examples", "Self-aware about gaps"],
        areas_for_improvement=[
            "Add more depth to analytical answers",
            "Quantify impact consistently",
            "Explore systemic root causes",
        ],
        practice_questions=["Tell me about a failure.", "Walk me through a metrics framework."],
        action_items=["Build a story bank with 8-10 examples", "Practice STAR format for 90 seconds per answer"],
    )


@pytest.fixture
def mock_llm_client():
    return MockLLMClient()
