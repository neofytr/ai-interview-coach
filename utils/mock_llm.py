import asyncio
from typing import TypeVar

from pydantic import BaseModel

from utils.llm import LLMClient

T = TypeVar("T", bound=BaseModel)

MOCK_PLAN = {
    "role_context": "A strong Product Manager combines analytical thinking with user empathy. They must prioritize ruthlessly, communicate clearly across engineering and design, and make data-informed decisions while navigating ambiguity.",
    "topics": [
        {
            "name": "Product Thinking & Prioritization",
            "description": "Ability to identify user needs, define problems, and prioritize solutions",
            "suggested_questions": [
                "Tell me about a time you had to prioritize between competing feature requests.",
                "How do you decide what NOT to build?",
            ],
            "difficulty": "medium",
        },
        {
            "name": "Cross-functional Collaboration",
            "description": "Working effectively with engineering, design, and stakeholders",
            "suggested_questions": [
                "Describe a time you had to align engineering and design on a contentious decision.",
                "How do you handle pushback from a senior engineer on your product direction?",
            ],
            "difficulty": "medium",
        },
        {
            "name": "Data-Driven Decision Making",
            "description": "Using metrics, experimentation, and analysis to guide product decisions",
            "suggested_questions": [
                "Walk me through how you'd measure the success of a new feature.",
                "Tell me about a time data changed your mind about a product decision.",
            ],
            "difficulty": "hard",
        },
        {
            "name": "Handling Failure & Ambiguity",
            "description": "Resilience, learning from mistakes, navigating uncertainty",
            "suggested_questions": [
                "Tell me about a product launch that didn't go as planned.",
                "How do you make progress when requirements are unclear?",
            ],
            "difficulty": "medium",
        },
    ],
    "evaluation_dimensions": [
        {"name": "Communication Clarity", "description": "Structure, conciseness, articulation", "weight": 0.20},
        {"name": "Problem-Solving Approach", "description": "Methodology, frameworks, reasoning", "weight": 0.25},
        {"name": "Use of Examples", "description": "Concrete examples, STAR method, specifics", "weight": 0.20},
        {"name": "Critical Thinking", "description": "Analysis, tradeoffs, nuance", "weight": 0.20},
        {"name": "Self-Awareness", "description": "Honesty about gaps, growth mindset", "weight": 0.15},
    ],
    "difficulty_progression": "gradual",
    "opening_message": "Hi there! Thanks for joining this mock interview. I'll be asking you a mix of behavioral and product questions to get a sense of how you think and work. There are no trick questions — just be yourself and walk me through your thinking. Ready to dive in?",
    "total_turns": 6,
}

MOCK_QUESTIONS = [
    "Great, let's start with something broad. Tell me about a time you had to choose between two features that your team really wanted to build. How did you decide which one to prioritize?",
    "That's a solid approach. You mentioned using customer feedback to guide your decision — can you walk me through specifically how you gathered and weighted that feedback? I'm curious about your process.",
    "Interesting. Let's shift gears a bit. Tell me about a time you had to work through a disagreement with an engineer or designer on your team. How did you handle it?",
    "You mentioned finding a compromise — what made you confident that was the right call rather than pushing harder for your original position? I'd love to hear how you weighed those tradeoffs.",
    "Good example. Now let's talk about metrics. Imagine you just launched a new onboarding flow for a SaaS product. Walk me through how you'd measure whether it's actually working — what would you track and why?",
    "Last question. Tell me about a time something you shipped didn't work out the way you expected. What happened, and what did you take away from it?",
]

MOCK_EVALUATIONS = [
    {
        "turn_number": 1,
        "dimension_scores": [
            {
                "dimension": "Communication Clarity",
                "score": 7,
                "justification": "Answer was well-structured with a clear beginning, middle, and end.",
            },
            {
                "dimension": "Problem-Solving Approach",
                "score": 6,
                "justification": "Mentioned a framework but didn't fully articulate the prioritization criteria used.",
            },
            {
                "dimension": "Use of Examples",
                "score": 7,
                "justification": "Gave a concrete example from their startup experience with specific context.",
            },
            {
                "dimension": "Critical Thinking",
                "score": 5,
                "justification": "Described the decision but didn't explore tradeoffs or alternatives considered.",
            },
            {
                "dimension": "Self-Awareness",
                "score": 6,
                "justification": "Acknowledged the difficulty of the decision but didn't reflect on what they'd do differently.",
            },
        ],
        "overall_score": 6.2,
        "strengths": ["Provided a real example with specific context about the feature prioritization decision"],
        "weaknesses": ["Didn't discuss the tradeoffs or alternatives considered in depth"],
        "signals": ["probe_deeper"],
        "follow_up_suggestion": "Ask about the specific process for gathering and weighting customer feedback",
    },
    {
        "turn_number": 2,
        "dimension_scores": [
            {
                "dimension": "Communication Clarity",
                "score": 8,
                "justification": "Clearly walked through the feedback gathering process step by step.",
            },
            {
                "dimension": "Problem-Solving Approach",
                "score": 7,
                "justification": "Described a structured approach using surveys, user interviews, and usage data.",
            },
            {
                "dimension": "Use of Examples",
                "score": 7,
                "justification": "Referenced specific numbers — 15 user interviews and NPS survey results.",
            },
            {
                "dimension": "Critical Thinking",
                "score": 7,
                "justification": "Discussed how to weight qualitative vs quantitative feedback.",
            },
            {
                "dimension": "Self-Awareness",
                "score": 6,
                "justification": "Acknowledged that their process has evolved but didn't specify how.",
            },
        ],
        "overall_score": 7.1,
        "strengths": [
            "Demonstrated a structured, multi-source approach to gathering customer feedback",
            "Used specific numbers to quantify their process",
        ],
        "weaknesses": ["Could have discussed limitations or biases in their feedback collection"],
        "signals": ["move_on"],
        "follow_up_suggestion": None,
    },
    {
        "turn_number": 3,
        "dimension_scores": [
            {
                "dimension": "Communication Clarity",
                "score": 6,
                "justification": "Answer started strong but became somewhat disorganized toward the end.",
            },
            {
                "dimension": "Problem-Solving Approach",
                "score": 7,
                "justification": "Showed a collaborative approach to conflict resolution.",
            },
            {
                "dimension": "Use of Examples",
                "score": 6,
                "justification": "Gave an example but lacked specific details about the outcome.",
            },
            {
                "dimension": "Critical Thinking",
                "score": 6,
                "justification": "Described the compromise but didn't fully analyze why it was the right approach.",
            },
            {
                "dimension": "Self-Awareness",
                "score": 7,
                "justification": "Showed awareness of different perspectives and willingness to adapt.",
            },
        ],
        "overall_score": 6.4,
        "strengths": ["Demonstrated willingness to understand the engineer's perspective before pushing back"],
        "weaknesses": ["Lacked specifics about the outcome and impact of the compromise"],
        "signals": ["probe_deeper"],
        "follow_up_suggestion": "Ask what made them confident the compromise was right vs pushing harder for their original position",
    },
    {
        "turn_number": 4,
        "dimension_scores": [
            {
                "dimension": "Communication Clarity",
                "score": 7,
                "justification": "Clearly articulated the decision-making framework for choosing compromise.",
            },
            {
                "dimension": "Problem-Solving Approach",
                "score": 8,
                "justification": "Showed sophisticated thinking about when to compromise vs when to hold firm.",
            },
            {
                "dimension": "Use of Examples",
                "score": 7,
                "justification": "Tied the reasoning back to the specific situation with concrete details.",
            },
            {
                "dimension": "Critical Thinking",
                "score": 8,
                "justification": "Excellent analysis of the tradeoffs between shipping speed and technical quality.",
            },
            {
                "dimension": "Self-Awareness",
                "score": 7,
                "justification": "Acknowledged that they've learned to pick their battles more strategically.",
            },
        ],
        "overall_score": 7.5,
        "strengths": [
            "Strong analysis of tradeoffs between speed and quality",
            "Showed growth in how they approach disagreements",
        ],
        "weaknesses": ["Could have quantified the impact of the compromise decision"],
        "signals": ["move_on", "increase_difficulty"],
        "follow_up_suggestion": None,
    },
    {
        "turn_number": 5,
        "dimension_scores": [
            {
                "dimension": "Communication Clarity",
                "score": 8,
                "justification": "Very well-structured walkthrough of the metrics framework.",
            },
            {
                "dimension": "Problem-Solving Approach",
                "score": 8,
                "justification": "Identified leading and lagging indicators, showed funnel thinking.",
            },
            {
                "dimension": "Use of Examples",
                "score": 6,
                "justification": "Stayed somewhat theoretical — didn't tie metrics back to a real experience.",
            },
            {
                "dimension": "Critical Thinking",
                "score": 8,
                "justification": "Discussed guardrail metrics and potential pitfalls of optimizing for wrong metrics.",
            },
            {
                "dimension": "Self-Awareness",
                "score": 6,
                "justification": "Confident answer but didn't acknowledge limitations of the proposed approach.",
            },
        ],
        "overall_score": 7.4,
        "strengths": [
            "Comprehensive metrics framework covering acquisition, activation, and retention",
            "Mentioned guardrail metrics to prevent gaming",
        ],
        "weaknesses": ["Answer was more theoretical than experience-based — would benefit from a real example"],
        "signals": ["move_on"],
        "follow_up_suggestion": None,
    },
    {
        "turn_number": 6,
        "dimension_scores": [
            {
                "dimension": "Communication Clarity",
                "score": 7,
                "justification": "Clear narrative structure following the STAR format.",
            },
            {
                "dimension": "Problem-Solving Approach",
                "score": 7,
                "justification": "Described a systematic post-mortem process and corrective actions.",
            },
            {
                "dimension": "Use of Examples",
                "score": 8,
                "justification": "Specific example with concrete failure details and measurable outcome.",
            },
            {
                "dimension": "Critical Thinking",
                "score": 7,
                "justification": "Good reflection on root causes but could have explored systemic issues.",
            },
            {
                "dimension": "Self-Awareness",
                "score": 9,
                "justification": "Excellent vulnerability and genuine learning — admitted what they'd do differently.",
            },
        ],
        "overall_score": 7.5,
        "strengths": [
            "Showed genuine vulnerability in discussing failure",
            "Connected the failure to a concrete learning that changed their behavior",
        ],
        "weaknesses": [
            "Could have explored whether the failure pointed to systemic process issues, not just individual mistakes"
        ],
        "signals": ["move_on"],
        "follow_up_suggestion": None,
    },
]

MOCK_FEEDBACK = {
    "overall_rating": "Hire",
    "overall_score": 7.0,
    "summary": "You demonstrated solid product thinking with good communication skills and a structured approach to decision-making. Your strongest moments came when discussing tradeoffs and handling failure, showing genuine self-awareness. The main area for growth is grounding your analytical answers in real examples — your metrics answer was strong conceptually but would have been more compelling with a concrete story.",
    "dimension_averages": {
        "Communication Clarity": 7.2,
        "Problem-Solving Approach": 7.2,
        "Use of Examples": 6.8,
        "Critical Thinking": 6.8,
        "Self-Awareness": 6.8,
    },
    "strengths": [
        "Strong structured communication — your prioritization answer followed a clear beginning-middle-end format that made it easy to follow your thinking process.",
        "Excellent vulnerability when discussing failure — you didn't just describe what went wrong, you connected it to a concrete behavioral change, which shows real growth.",
        "Sophisticated tradeoff analysis — when discussing the engineering disagreement, you articulated a nuanced framework for when to compromise vs hold firm.",
    ],
    "areas_for_improvement": [
        "Ground analytical answers in real experience — your metrics framework for the onboarding question was theoretically strong but stayed abstract. Practice tying frameworks back to actual projects: 'At [company], I tracked X and it revealed Y.'",
        "Quantify your impact more consistently — you mentioned customer feedback and user interviews but only occasionally cited specific numbers. Practice attaching metrics to every example: adoption rates, revenue impact, time saved.",
        "Explore systemic root causes — when discussing your product failure, you focused on what you personally did wrong. Strong PMs also analyze whether the process or org structure contributed. Practice asking 'what systemic change would prevent this?'",
    ],
    "practice_questions": [
        "Walk me through a specific metrics dashboard you built or used. What did you track, what did you learn, and what did you change as a result?",
        "Tell me about a time you used data to kill a feature or project that the team was excited about.",
        "Describe a situation where you had to make a product decision with incomplete data. What was your framework?",
        "How would you design an A/B test for a checkout flow change? Walk me through the hypothesis, metrics, and minimum detectable effect.",
    ],
    "action_items": [
        "Build a 'story bank' of 8-10 product stories, each with specific metrics — write out the Situation, Action, and Result with at least 2 numbers per story.",
        "Practice the metrics question format: pick 3 products you use and prepare a 90-second answer on how you'd measure their core feature's success.",
        "For your failure story, add a '5 Whys' analysis — practice tracing the failure to a systemic root cause, not just a personal mistake.",
        "Record yourself answering 'Tell me about a tradeoff you made' and review for structure — aim for 2 minutes with clear problem, options, reasoning, and outcome.",
    ],
}


class MockLLMClient(LLMClient):
    def __init__(self) -> None:
        self.model = "mock-testing"
        self._call_count = 0
        self._question_index = 0

    async def call(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
    ) -> str:
        await asyncio.sleep(0.5)
        idx = min(self._question_index, len(MOCK_QUESTIONS) - 1)
        question = MOCK_QUESTIONS[idx]
        self._question_index += 1
        return question

    async def call_json(
        self,
        system_prompt: str,
        user_message: str,
        response_model: type[T],
        temperature: float = 0.3,
    ) -> T:
        await asyncio.sleep(0.5)
        model_name = response_model.__name__

        if model_name == "InterviewPlan":
            data = MOCK_PLAN
        elif model_name == "TurnEvaluation":
            idx = min(self._call_count, len(MOCK_EVALUATIONS) - 1)
            data = MOCK_EVALUATIONS[idx]
            self._call_count += 1
        elif model_name == "FeedbackReport":
            data = MOCK_FEEDBACK
        else:
            raise ValueError(f"No mock data for {model_name}")

        return response_model.model_validate(data)
