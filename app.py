import asyncio

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from models import CandidateProfile, FocusArea
from orchestrator import InterviewEngine
from utils.config import get_settings

load_dotenv()


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def init_session_state() -> None:
    defaults = {
        "engine": None,
        "plan": None,
        "messages": [],
        "evaluations": [],
        "feedback": None,
        "interview_started": False,
        "interview_complete": False,
        "current_turn": 0,
        "max_turns": 0,
        "current_topic": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def check_api_key() -> bool:
    settings = get_settings()
    return bool(settings.openai_api_key and settings.openai_api_key != "your-api-key-here")


def render_sidebar_setup() -> None:
    st.sidebar.title("AI Interview Coach")
    st.sidebar.divider()

    role = st.sidebar.text_input("Target Role", placeholder="e.g. Product Manager")
    background = st.sidebar.text_area(
        "Background (optional)",
        placeholder="2-3 line resume snippet",
        height=80,
    )
    focus = st.sidebar.selectbox(
        "Focus Area",
        ["behavioral", "technical", "case", "mixed"],
        index=3,
    )

    if st.sidebar.button("Start Interview", type="primary", use_container_width=True):
        if not role.strip():
            st.sidebar.error("Please enter a target role.")
            return

        profile = CandidateProfile(
            target_role=role.strip(),
            background=background.strip() or None,
            focus_area=FocusArea(focus),
        )
        engine = InterviewEngine()

        with st.spinner("Planning your interview..."):
            plan, first_question = run_async(engine.start_interview(profile))

        st.session_state.engine = engine
        st.session_state.plan = plan
        st.session_state.interview_started = True
        st.session_state.messages = [{"role": "assistant", "content": first_question}]
        state = engine.get_state()
        st.session_state.current_turn = state["current_turn"]
        st.session_state.max_turns = state["max_turns"]
        st.session_state.current_topic = state["current_topic"]
        st.rerun()


def render_sidebar_progress() -> None:
    st.sidebar.title("AI Interview Coach")
    st.sidebar.divider()

    turn = st.session_state.current_turn
    max_turns = st.session_state.max_turns

    st.sidebar.metric("Progress", f"Turn {turn} / {max_turns}")
    st.sidebar.progress(min(turn / max_turns, 1.0) if max_turns > 0 else 0.0)
    st.sidebar.metric("Current Topic", st.session_state.current_topic)

    if st.session_state.plan:
        topics = [t.name for t in st.session_state.plan.topics]
        st.sidebar.divider()
        st.sidebar.caption("**Topics**")
        for t in topics:
            st.sidebar.caption(f"  {t}")

    st.sidebar.divider()
    settings = get_settings()
    st.sidebar.caption(f"Powered by `{settings.llm_model}`")

    if st.session_state.interview_complete:
        st.sidebar.divider()
        if st.sidebar.button("Start New Interview", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_chat() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.interview_complete:
        return

    answer = st.chat_input("Type your answer...")
    if answer:
        st.session_state.messages.append({"role": "user", "content": answer})
        with st.chat_message("user"):
            st.markdown(answer)

        engine: InterviewEngine = st.session_state.engine

        with st.spinner("Thinking..."):
            next_question, evaluation = run_async(engine.submit_answer(answer))

        st.session_state.evaluations.append(evaluation)
        state = engine.get_state()
        st.session_state.current_turn = state["current_turn"]
        st.session_state.current_topic = state["current_topic"]

        if next_question is None:
            with st.spinner("Generating your feedback report..."):
                feedback = run_async(engine.end_interview())
            st.session_state.feedback = feedback
            st.session_state.interview_complete = True
            st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": next_question})
            st.rerun()


def format_feedback_markdown(feedback) -> str:
    lines = [
        "# Interview Feedback Report\n",
        f"**Overall Rating:** {feedback.overall_rating}  ",
        f"**Overall Score:** {feedback.overall_score:.1f} / 10.0\n",
        f"## Summary\n\n{feedback.summary}\n",
        "## Strengths\n",
    ]
    for i, s in enumerate(feedback.strengths, 1):
        lines.append(f"{i}. {s}")
    lines.append("\n## Areas for Improvement\n")
    for i, a in enumerate(feedback.areas_for_improvement, 1):
        lines.append(f"{i}. {a}")
    lines.append("\n## Practice Questions\n")
    for i, q in enumerate(feedback.practice_questions, 1):
        lines.append(f"{i}. {q}")
    lines.append("\n## Action Items\n")
    for i, item in enumerate(feedback.action_items, 1):
        lines.append(f"{i}. {item}")
    lines.append("\n## Dimension Scores\n")
    lines.append("| Dimension | Score |")
    lines.append("|-----------|-------|")
    for dim, score in feedback.dimension_averages.items():
        lines.append(f"| {dim} | {score:.1f} |")
    return "\n".join(lines)


def render_feedback() -> None:
    feedback = st.session_state.feedback

    tab_feedback, tab_scores, tab_transcript = st.tabs(["Feedback", "Scores", "Transcript"])

    with tab_feedback:
        render_feedback_tab(feedback)
    with tab_scores:
        render_scores_tab(feedback)
    with tab_transcript:
        render_transcript_tab()

    st.divider()
    report_md = format_feedback_markdown(feedback)
    st.download_button(
        label="Download Feedback Report",
        data=report_md,
        file_name="interview_feedback.md",
        mime="text/markdown",
    )


def render_feedback_tab(feedback) -> None:
    color_map = {
        "Strong Hire": "green",
        "Hire": "green",
        "Lean Hire": "orange",
        "Lean No Hire": "red",
        "No Hire": "red",
    }
    color = color_map.get(feedback.overall_rating, "gray")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### :{color}[{feedback.overall_rating}]")
    with col2:
        st.metric("Overall Score", f"{feedback.overall_score:.1f} / 10")

    st.divider()
    st.subheader("Summary")
    st.write(feedback.summary)

    st.divider()
    col_s, col_i = st.columns(2)
    with col_s:
        st.subheader("Strengths")
        for s in feedback.strengths:
            st.markdown(f"- {s}")
    with col_i:
        st.subheader("Areas for Improvement")
        for a in feedback.areas_for_improvement:
            st.markdown(f"- {a}")

    st.divider()
    with st.expander("Practice Questions", expanded=False):
        for i, q in enumerate(feedback.practice_questions, 1):
            st.markdown(f"{i}. {q}")

    st.subheader("Action Items")
    for item in feedback.action_items:
        st.checkbox(item, value=False, disabled=False, key=f"action_{item[:30]}")


def render_scores_tab(feedback) -> None:
    dims = list(feedback.dimension_averages.keys())
    scores = list(feedback.dimension_averages.values())

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=scores + [scores[0]],
            theta=dims + [dims[0]],
            fill="toself",
            name="Scores",
            line=dict(color="#636EFA"),
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10]),
        ),
        showlegend=False,
        margin=dict(t=40, b=40, l=80, r=80),
    )
    st.plotly_chart(fig, use_container_width=True)

    evaluations = st.session_state.evaluations
    if evaluations:
        st.divider()
        st.subheader("Score Progression")

        turns = [e.turn_number for e in evaluations]
        overall_scores = [e.overall_score for e in evaluations]

        fig_line = go.Figure()
        fig_line.add_trace(
            go.Scatter(
                x=turns,
                y=overall_scores,
                mode="lines+markers",
                name="Overall Score",
                line=dict(color="#636EFA", width=3),
                marker=dict(size=8),
            )
        )
        fig_line.update_layout(
            title="Overall Score by Turn",
            xaxis_title="Turn",
            yaxis_title="Score",
            yaxis=dict(range=[0, 10]),
            xaxis=dict(dtick=1),
            margin=dict(t=40, b=40, l=60, r=40),
        )
        st.plotly_chart(fig_line, use_container_width=True)

        all_dims = set()
        for e in evaluations:
            for ds in e.dimension_scores:
                all_dims.add(ds.dimension)
        all_dims = sorted(all_dims)

        if all_dims:
            colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692"]
            fig_multi = go.Figure()
            for idx, dim in enumerate(all_dims):
                dim_turns = []
                dim_scores = []
                for e in evaluations:
                    for ds in e.dimension_scores:
                        if ds.dimension == dim:
                            dim_turns.append(e.turn_number)
                            dim_scores.append(ds.score)
                            break
                fig_multi.add_trace(
                    go.Scatter(
                        x=dim_turns,
                        y=dim_scores,
                        mode="lines+markers",
                        name=dim,
                        line=dict(color=colors[idx % len(colors)]),
                        marker=dict(size=6),
                    )
                )
            fig_multi.update_layout(
                title="Dimension Scores by Turn",
                xaxis_title="Turn",
                yaxis_title="Score",
                yaxis=dict(range=[0, 10]),
                xaxis=dict(dtick=1),
                margin=dict(t=40, b=40, l=60, r=40),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            )
            st.plotly_chart(fig_multi, use_container_width=True)

    st.divider()
    st.subheader("Dimension Breakdown")
    score_data = {
        "Dimension": dims,
        "Score": [f"{s:.1f}" for s in scores],
    }
    st.table(score_data)


def render_transcript_tab() -> None:
    messages = st.session_state.messages
    evaluations = st.session_state.evaluations

    eval_index = 0
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

        if msg["role"] == "user" and eval_index < len(evaluations):
            ev = evaluations[eval_index]
            with st.expander(f"Turn {ev.turn_number} Evaluation (Score: {ev.overall_score:.1f})", expanded=False):
                cols = st.columns(len(ev.dimension_scores))
                for col, ds in zip(cols, ev.dimension_scores, strict=True):
                    with col:
                        st.metric(ds.dimension, f"{ds.score}/10")

                if ev.strengths:
                    st.markdown("**Strengths:** " + "; ".join(ev.strengths))
                if ev.weaknesses:
                    st.markdown("**Weaknesses:** " + "; ".join(ev.weaknesses))

                signals = ", ".join(s.value for s in ev.signals) if ev.signals else "none"
                st.caption(f"Signals: {signals}")
            eval_index += 1


def main() -> None:
    st.set_page_config(
        page_title="AI Mock Interview Coach",
        page_icon="🎯",
        layout="wide",
    )

    init_session_state()

    if not check_api_key():
        st.error("**OPENAI_API_KEY not found.** Copy `.env.example` to `.env` and add your API key.")
        st.stop()

    if not st.session_state.interview_started:
        render_sidebar_setup()
        st.title("AI Mock Interview Coach")
        st.markdown(
            "Practice interviews powered by AI agents that adapt to your responses. "
            "Set up your interview in the sidebar to begin."
        )
    elif st.session_state.interview_complete:
        render_sidebar_progress()
        render_feedback()
    else:
        render_sidebar_progress()
        render_chat()


if __name__ == "__main__":
    main()
