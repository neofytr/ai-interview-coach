import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from models import CandidateProfile, FocusArea
from orchestrator import InterviewEngine
from utils.config import get_settings
from utils.logger import set_verbose

load_dotenv()

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Mock Interview Coach — CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose per-turn output and debug logging")
    parser.add_argument("-o", "--output", type=str, default=None, help="Save interview result as JSON to this path")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode with mock responses (no API key needed)")
    return parser.parse_args()


def check_api_key() -> bool:
    settings = get_settings()
    if not settings.openai_api_key or settings.openai_api_key == "your-api-key-here":
        console.print(
            Panel(
                "[yellow]OPENAI_API_KEY not found or not set.[/yellow]\n\n"
                "To use with a real LLM:\n"
                "  1. Copy .env.example to .env\n"
                "  2. Add your OpenAI API key\n"
                "  3. Run again\n\n"
                "Or run with [bold]--demo[/bold] to try the system with mock responses.",
                title="Missing API Key",
                border_style="yellow",
            )
        )
        return False
    return True


def collect_profile() -> CandidateProfile:
    console.print()
    name = Prompt.ask("[bold cyan]Your name[/bold cyan]")
    role = Prompt.ask("[bold cyan]Target role[/bold cyan]")
    experience = Prompt.ask(
        "[bold cyan]Experience level[/bold cyan]",
        choices=["intern", "junior", "mid", "senior", "lead"],
        default="mid",
    )
    background = Prompt.ask(
        "[bold cyan]Background[/bold cyan] [dim](optional, press Enter to skip)[/dim]",
        default="",
    )
    focus = Prompt.ask(
        "[bold cyan]Focus area[/bold cyan]",
        choices=["behavioral", "technical", "case", "mixed"],
        default="mixed",
    )
    return CandidateProfile(
        name=name,
        target_role=role,
        experience_level=experience,
        background=background or None,
        focus_area=FocusArea(focus),
    )


def print_verbose_evaluation(evaluation) -> None:
    dim_scores = ", ".join(f"{d.dimension}: {d.score}" for d in evaluation.dimension_scores)
    signals = ", ".join(s.value for s in evaluation.signals) if evaluation.signals else "none"
    console.print(
        f"\n  [dim]Score: {evaluation.overall_score:.1f} | Signals: {signals} | Dimensions: {dim_scores}[/dim]"
    )


def print_feedback(feedback) -> str:
    rating_colors = {
        "Strong Hire": "green",
        "Hire": "green",
        "Lean Hire": "yellow",
        "Lean No Hire": "orange3",
        "No Hire": "red",
    }
    color = rating_colors.get(feedback.overall_rating, "white")

    md_lines = [
        f"## Summary\n\n{feedback.summary}\n",
        "## Strengths\n",
    ]
    for i, s in enumerate(feedback.strengths, 1):
        md_lines.append(f"{i}. {s}")
    md_lines.append("\n## Areas for Improvement\n")
    for i, a in enumerate(feedback.areas_for_improvement, 1):
        md_lines.append(f"{i}. {a}")
    md_lines.append("\n## Practice Questions\n")
    for i, q in enumerate(feedback.practice_questions, 1):
        md_lines.append(f"{i}. {q}")
    md_lines.append("\n## Action Items\n")
    for i, item in enumerate(feedback.action_items, 1):
        md_lines.append(f"{i}. {item}")
    md_lines.append("\n## Dimension Scores\n")
    md_lines.append("| Dimension | Score |")
    md_lines.append("|-----------|-------|")
    for dim, score in feedback.dimension_averages.items():
        md_lines.append(f"| {dim} | {score:.1f} |")

    body_md = "\n".join(md_lines)

    report_text = (
        f"# Interview Feedback Report\n\n"
        f"**Overall Rating:** {feedback.overall_rating}  \n"
        f"**Overall Score:** {feedback.overall_score:.1f} / 10.0\n\n"
        f"{body_md}"
    )

    console.print()
    console.print(
        f"  [{color}]●[/{color}] [bold]Overall Rating:[/bold] "
        f"[{color}]{feedback.overall_rating}[/{color}]  |  "
        f"[bold]Score:[/bold] {feedback.overall_score:.1f} / 10.0\n"
    )
    console.print(Panel(Markdown(body_md), title="Feedback Report", border_style="green"))

    return report_text


def save_transcript(result, report_text: str) -> None:
    save = Prompt.ask(
        "\n[bold cyan]Save transcript?[/bold cyan]",
        choices=["y", "n"],
        default="n",
    )
    if save != "y":
        return

    transcripts_dir = Path(__file__).parent / "transcripts"
    transcripts_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"interview_{timestamp}.md"
    filepath = transcripts_dir / filename

    lines = [
        "# Mock Interview Transcript\n",
        f"**Candidate:** {result.profile.name}",
        f"**Role:** {result.profile.target_role}",
        f"**Experience:** {result.profile.experience_level}",
        f"**Background:** {result.profile.background or 'Not provided'}",
        f"**Focus Area:** {result.profile.focus_area.value}\n",
        "---\n",
        "## Interview\n",
    ]
    for msg in result.conversation:
        speaker = "Interviewer" if msg.role == "interviewer" else "Candidate"
        lines.append(f"**{speaker}:** {msg.content}\n")
    lines.append("---\n")
    lines.append("## Feedback Report\n")
    lines.append(report_text)

    filepath.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"\n[green]Transcript saved to[/green] [bold]{filepath}[/bold]")


def save_json_output(result, output_path: str) -> None:
    data = result.model_dump(mode="json")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"\n[green]JSON output saved to[/green] [bold]{path}[/bold]")


async def run_interview(verbose: bool = False, output: str | None = None, demo: bool = False) -> None:
    if demo:
        from utils.mock_llm import MockLLMClient

        engine = InterviewEngine(llm=MockLLMClient())
        console.print("[dim]Running in demo mode with mock responses.[/dim]\n")
    else:
        engine = InterviewEngine()

    profile = collect_profile()

    with console.status("[bold yellow]Planning your interview...[/bold yellow]"):
        plan, first_question = await engine.start_interview(profile)

    console.print()
    console.print(
        Panel(
            f"[dim]Topics: {', '.join(t.name for t in plan.topics)} | "
            f"Turns: {plan.total_turns} | "
            f"Progression: {plan.difficulty_progression}[/dim]",
            title="Interview Plan",
            border_style="blue",
        )
    )

    console.print()
    console.print(Panel(first_question, title="Interviewer", border_style="cyan"))

    interrupted = False
    try:
        while True:
            console.print()
            answer = Prompt.ask("[bold green]Your answer[/bold green]")
            if not answer.strip():
                console.print("[dim]Please provide an answer.[/dim]")
                continue

            with console.status("[bold yellow]Thinking...[/bold yellow]"):
                next_question, evaluation = await engine.submit_answer(answer)

            state = engine.get_state()
            console.print(
                f"\n[dim]Turn {state['current_turn']}/{state['max_turns']} | Topic: {state['current_topic']}[/dim]"
            )

            if verbose:
                print_verbose_evaluation(evaluation)

            if next_question is None:
                console.print("\n[bold]Interview complete![/bold]")
                break

            console.print()
            console.print(Panel(next_question, title="Interviewer", border_style="cyan"))

    except KeyboardInterrupt:
        interrupted = True
        console.print("\n\n[yellow]Interview ended early.[/yellow]")

    if not engine.state_manager or not engine.state_manager.evaluations:
        console.print("[red]No answers were evaluated — cannot generate feedback.[/red]")
        return

    with console.status("[bold yellow]Generating your feedback report...[/bold yellow]"):
        feedback = await engine.end_interview()

    report_text = print_feedback(feedback)

    if not interrupted:
        result = engine.get_result()
        if output:
            save_json_output(result, output)
        save_transcript(result, report_text)


def main() -> None:
    args = parse_args()

    if args.verbose:
        set_verbose(True)

    console.print(
        Panel(
            "[bold]Practice interviews powered by AI agents[/bold]\n\n"
            "You'll be interviewed by an adaptive AI that adjusts its questions\n"
            "based on your responses. After the interview, you'll receive\n"
            "detailed feedback with scores and actionable advice.",
            title="[bold cyan]AI Mock Interview Coach[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    if not args.demo and not check_api_key():
        sys.exit(1)

    try:
        asyncio.run(run_interview(verbose=args.verbose, output=args.output, demo=args.demo))
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
