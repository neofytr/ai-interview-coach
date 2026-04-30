# AI Mock Interview Coach

[![CI](https://github.com/neofytr/ai-interview-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/neofytr/ai-interview-coach/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A multi-agent system that runs adaptive mock interviews and gives you real feedback afterwards. Four agents work together: one plans the interview, one asks questions, one silently evaluates your answers in real time, and one writes up a coaching report at the end.

The key thing that makes this different from a static question list is the evaluation loop. After every answer, the evaluator scores you and sends signals back to the interviewer (probe deeper, move on, increase difficulty, etc.), so the conversation adapts to how you're actually doing.

## How It Works

```
You fill in your profile -> Planner creates interview strategy
                                      |
                +-------------------------------------+
                |         Interview Loop              |
                |  Interviewer -> You -> Evaluator    |
                |       ^                    |        |
                |       +-- signals ---------+        |
                +-------------------------------------+
                                      |
                      All scores -> Coach -> Feedback Report
```

The orchestrator runs a state machine that decides after each answer whether to follow up (max 2 per topic), move to the next topic, adjust difficulty, or wrap up. It's not just a for loop.

**Agents:**

| Agent | What it does | Output |
|-------|-------------|--------|
| Planner | Picks topics, dimensions, and difficulty based on your role and background. Pulls from a question bank, RAG knowledge base, and web search. | InterviewPlan (JSON) |
| Interviewer | Asks questions, follows up, handles edge cases (IDK answers, off-topic, one-word responses). Adapts based on evaluator signals. | Plain text question |
| Evaluator | Scores each answer 1-10 on weighted dimensions. Emits signals that drive the interviewer. You never see this during the interview. | TurnEvaluation (JSON) |
| Coach | Reads through everything and writes a feedback report with scores, patterns, and specific things to work on. | FeedbackReport (JSON) |

## Setup

```bash
git clone https://github.com/neofytr/ai-interview-coach.git
cd ai-interview-coach
pip install -r requirements.txt
cp .env.example .env
# add your API key to .env
```

Works with OpenAI, Gemini, or any OpenAI-compatible provider. Set `OPENAI_BASE_URL` in `.env` if you're not using OpenAI directly.

| Variable | Default | What it does |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | API key |
| `LLM_MODEL` | `gpt-4o-mini` | Model for all agents |
| `OPENAI_BASE_URL` | | Custom API endpoint |
| `ENABLE_RAG` | `true` | Pull from knowledge base during planning |
| `ENABLE_WEB_SEARCH` | `true` | Search for current interview trends |

## Usage

**CLI:**

```bash
python main.py              # normal mode
python main.py -v            # shows per-turn scores after each answer
python main.py --demo        # runs with mock responses, no API key needed
python main.py -o result.json
```

**Web UI:**

```bash
streamlit run app.py
```

Chat interface with progress tracking, radar charts, score progression graphs, and per-turn evaluation breakdowns. Has a demo mode button if you don't have an API key set up.

## What's in the box

- **112 curated questions** across 14 subcategories (behavioral, technical, case) in `data/question_bank.json`
- **14 knowledge base documents** covering 7 roles, 4 interview frameworks, and 3 scoring rubrics, used by the RAG retriever during planning
- **Web search** via DuckDuckGo for current role-specific interview trends
- **115 tests** using a mock LLM client (zero API calls). Run with `pytest tests/ -v`
- **CI pipeline** on GitHub Actions: linting with ruff + tests on Python 3.11 and 3.12

## Example Transcripts

Three sample interviews showing how the system adapts:

| Transcript | What happens | Result |
|-----------|-------------|--------|
| [Strong Candidate](transcripts/strong_candidate.md) | PM role, structured answers with metrics. System increases difficulty. | Strong Hire (8.2) |
| [Weak Candidate](transcripts/weak_candidate.md) | Data Analyst, vague SQL answers. System scaffolds and decreases difficulty. | Lean No Hire (4.2) |
| [Edge Case](transcripts/edge_case.md) | Frontend Intern, one-word answer, goes off-topic, asks a question back. System redirects. | Lean Hire (5.8) |

## Project Structure

```
models/schemas.py        - Pydantic models (CandidateProfile, InterviewPlan, TurnEvaluation, etc.)
utils/llm.py             - Async OpenAI client with retries and JSON parsing
utils/rag.py             - Embedding-based knowledge retrieval with caching
utils/web_search.py      - DuckDuckGo search wrapper
utils/config.py          - Centralized settings via pydantic-settings
agents/                  - Planner, Interviewer, Evaluator, Coach (each with its own prompt in prompts/)
orchestrator/state.py    - Interview state machine with follow-up limits and turn budgets
orchestrator/engine.py   - Ties everything together
main.py                  - CLI (Rich)
app.py                   - Streamlit web app
tests/                   - 8 test files, 115 tests total
```
