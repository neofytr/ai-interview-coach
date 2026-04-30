from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FocusArea(str, Enum):
    behavioral = "behavioral"
    technical = "technical"
    case = "case"
    mixed = "mixed"


class CandidateProfile(BaseModel):
    target_role: str
    background: Optional[str] = None
    focus_area: FocusArea


class InterviewTopic(BaseModel):
    name: str
    description: str
    suggested_questions: list[str]
    difficulty: str


class EvaluationDimension(BaseModel):
    name: str
    description: str
    weight: float = Field(ge=0.0, le=1.0)


class InterviewPlan(BaseModel):
    role_context: str
    topics: list[InterviewTopic]
    evaluation_dimensions: list[EvaluationDimension]
    difficulty_progression: str
    opening_message: str
    total_turns: int = Field(ge=1, le=15)


class EvaluatorSignal(str, Enum):
    probe_deeper = "probe_deeper"
    move_on = "move_on"
    increase_difficulty = "increase_difficulty"
    decrease_difficulty = "decrease_difficulty"
    redirect = "redirect"


class DimensionScore(BaseModel):
    dimension: str
    score: int = Field(ge=1, le=10)
    justification: str


class TurnEvaluation(BaseModel):
    turn_number: int
    dimension_scores: list[DimensionScore]
    overall_score: float = Field(ge=1.0, le=10.0)
    strengths: list[str]
    weaknesses: list[str]
    signals: list[EvaluatorSignal]
    follow_up_suggestion: Optional[str] = None


class FeedbackReport(BaseModel):
    overall_rating: str
    overall_score: float
    summary: str
    dimension_averages: dict[str, float]
    strengths: list[str]
    areas_for_improvement: list[str]
    practice_questions: list[str]
    action_items: list[str]


class Message(BaseModel):
    role: str
    content: str
    turn_number: int


class InterviewState(str, Enum):
    planning = "planning"
    interviewing = "interviewing"
    evaluating = "evaluating"
    following_up = "following_up"
    concluding = "concluding"
    coaching = "coaching"
    done = "done"


class InterviewResult(BaseModel):
    profile: CandidateProfile
    plan: InterviewPlan
    conversation: list[Message]
    evaluations: list[TurnEvaluation]
    feedback: FeedbackReport
