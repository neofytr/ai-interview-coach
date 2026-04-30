# AI Mock Interview Coach

A multi-agent AI system that conducts adaptive mock interviews and delivers actionable coaching feedback.

## Overview

This system uses four specialized AI agents — Planner, Interviewer, Evaluator, and Coach — orchestrated through a state machine to simulate realistic interview practice. Unlike static question lists, the interviewer adapts in real time based on invisible evaluation signals: probing deeper on weak answers, increasing difficulty for strong candidates, and redirecting off-topic responses. After the interview, a coaching agent synthesizes all evaluations into a detailed feedback report with scores, evidence-based strengths/weaknesses, and concrete practice recommendations.

## Architecture

### Agents

| Agent | Role | Input → Output |
|-------|------|----------------|
| **Planner** | Designs the interview strategy — selects topics, evaluation dimensions, and difficulty progression based on the target role and candidate background. Runs once at the start. | CandidateProfile → InterviewPlan (JSON) |
| **Interviewer** | Conducts the conversation. Asks questions, follows up, handles edge cases (candidate says "I don't know", goes off-topic, gives one-word answers). Adapts based on evaluator signals. | Plan + History + Signals → Next question (text) |
| **Evaluator** | Scores each answer against weighted dimensions (1–10) and emits signals (`probe_deeper`, `move_on`, `increase_difficulty`, `decrease_difficulty`, `redirect`) that drive interviewer adaptation. Invisible to the candidate. | Question + Answer + Rubric → TurnEvaluation (JSON) |
| **Coach** | Synthesizes all evaluations into a final feedback report. Identifies patterns across answers, maps scores to a hiring signal, and generates specific practice questions and action items. | Full transcript + Evaluations → FeedbackReport (JSON) |

### Orchestration Flow

```
Candidate Profile → Planner → Interview Plan
                                    ↓
              ┌─────────────────────────────────────┐
              │         Interview Loop              │
              │  Interviewer → Candidate → Evaluator│
              │       ↑                      │      │
              │       └── signals ───────────┘      │
              └─────────────────────────────────────┘
                                    ↓
                    Evaluations → Coach → Feedback Report
```

The orchestrator is a state machine (`PLANNING → INTERVIEWING ↔ EVALUATING → COACHING → DONE`) that makes decisions each turn:

- **Follow up or move on?** Based on evaluator signals and a per-topic follow-up limit (max 2) to prevent infinite probing.
- **Adjust difficulty?** Evaluator signals propagate to the interviewer's next prompt.
- **Conclude?** When all topics are covered or the turn budget is exhausted.

### Question Bank

The Planner agent is grounded by a curated question bank (`data/question_bank.json`) containing ~110 real interview questions across behavioral, technical, and case categories. When generating an interview plan, the planner receives questions filtered by the candidate's focus area and draws `suggested_questions` from this bank, adapting them to fit the specific role. This reduces hallucinated or generic questions while still allowing the planner to generate original questions when needed.

### Key Design Decisions

- **4 agents, not 3.** Separating the Planner from the Interviewer lets the interview be strategic (role-adaptive topics, weighted dimensions) rather than just reactive. The Planner thinks about what *should* happen; the Interviewer handles what *is* happening.
- **Real-time evaluation loop.** The Evaluator runs after every answer, emitting signals that the Interviewer consumes. This is what makes the interview adaptive — a strong answer triggers harder questions, a weak one triggers scaffolding.
- **Pydantic structured outputs.** All inter-agent data flows through validated Pydantic models, not raw string parsing. The LLM client validates JSON responses against schemas and retries on parse failure.
- **State machine with follow-up limits.** The orchestrator tracks follow-ups per topic (max 2) and enforces turn budgets, preventing runaway conversations while allowing natural probing depth.
- **Dual interface.** CLI (`rich`) for developers and local testing; Streamlit for a polished web UI with radar charts. Both use the same engine — the interface layer is thin.
- **Prompts as files.** Each agent's system prompt lives in its own `.md` file, loaded at init time via `pathlib`. Prompts are iterable without touching Python code.

### Tradeoffs

- **Single LLM for all agents.** All four agents use the same model (default: `gpt-4o-mini`). A production system might use a stronger model for the Evaluator/Coach (where accuracy matters most) and a faster one for the Interviewer (where latency matters most). Kept uniform here for simplicity and cost.
- **No RAG or external knowledge.** The system relies on a static question bank and the LLM's parametric knowledge for role-specific interview content. A production version could retrieve real job descriptions, rubrics, or domain-specific evaluation criteria.
- **Synchronous turn-taking.** The interview is strictly turn-based (question → answer → evaluate → next question). A more advanced system could stream the interviewer's response or evaluate in parallel with the next question generation.

## Setup

```bash
git clone <repo-url>
cd ai-mock-interview-coach
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `LLM_MODEL` | No | `gpt-4o-mini` | Model to use for all agents |
| `OPENAI_BASE_URL` | No | — | Custom API base URL (for compatible providers) |

## Usage

### CLI

```bash
python main.py
```

Interactive terminal interface with rich formatting. You'll be prompted for your target role, background, and focus area, then interviewed in real time.

### Streamlit

```bash
streamlit run app.py
```

Web UI with a chat interface, progress sidebar, and post-interview feedback tabs including a radar chart of dimension scores.

## Running Tests

```bash
pytest tests/ -v
```

All tests use `MockLLMClient` — zero API calls required. The test suite covers:
- **Schema validation** — Pydantic model constraints (score bounds, weight ranges, turn limits)
- **State machine logic** — Follow-up limits, topic advancement, conclusion triggers, signal handling
- **Engine integration** — Full interview flow from start through feedback generation
- **Agent contracts** — Each agent returns the correct type with expected structure

## Example Transcripts

Three example interviews demonstrating the system's adaptive behavior:

| Transcript | Scenario | Rating |
|-----------|----------|--------|
| [Strong Candidate](transcripts/strong_candidate.md) | Product Manager with structured, metrics-driven answers. System increases difficulty and probes tradeoffs. | Strong Hire (8.2) |
| [Weak Candidate](transcripts/weak_candidate.md) | Data Analyst bootcamp grad with shallow SQL/stats knowledge. System decreases difficulty and scaffolds. | Lean No Hire (4.2) |
| [Edge Case](transcripts/edge_case.md) | Frontend Intern who gives a one-word answer, goes off-topic, asks a question back, then recovers. System redirects, probes, and adapts. | Lean Hire (5.8) |

## Project Structure

```
ai-mock-interview-coach/
├── main.py                  # CLI entry point (Rich)
├── app.py                   # Streamlit web app
├── requirements.txt
├── .env.example
│
├── models/
│   └── schemas.py           # All Pydantic data models
│
├── utils/
│   ├── llm.py               # Async OpenAI client with retries and JSON parsing
│   └── mock_llm.py          # Mock client for testing (no API calls)
│
├── data/
│   └── question_bank.json   # Curated interview questions (~110 across 14 categories)
│
├── prompts/
│   ├── planner.md            # Planner agent system prompt
│   ├── interviewer.md        # Interviewer agent system prompt
│   ├── evaluator.md          # Evaluator agent system prompt
│   └── coach.md              # Coach agent system prompt
│
├── agents/
│   ├── base.py               # Base agent class
│   ├── planner.py            # Interview plan generation
│   ├── evaluator.py          # Per-turn answer evaluation
│   ├── interviewer.py        # Adaptive question generation
│   └── coach.py              # Final feedback synthesis
│
├── orchestrator/
│   ├── state.py              # Interview state machine
│   └── engine.py             # Main orchestration engine
│
├── tests/
│   ├── conftest.py           # Shared pytest fixtures
│   ├── test_schemas.py       # Pydantic validation tests
│   ├── test_state.py         # State machine logic tests
│   ├── test_engine.py        # Integration tests
│   └── test_agents.py        # Agent contract tests
│
└── transcripts/              # Example interview transcripts
    ├── strong_candidate.md
    ├── weak_candidate.md
    └── edge_case.md
```
