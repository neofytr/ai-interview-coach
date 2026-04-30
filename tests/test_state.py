from models import DimensionScore, EvaluatorSignal, TurnEvaluation
from orchestrator.state import InterviewStateManager


def make_eval(signals, turn=1, score=6.0):
    return TurnEvaluation(
        turn_number=turn,
        dimension_scores=[DimensionScore(dimension="Comm", score=int(score), justification="ok")],
        overall_score=score,
        strengths=["strength"],
        weaknesses=["weakness"],
        signals=signals,
    )


class TestInitialState:
    def test_turn_starts_at_zero(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert sm.current_turn == 0

    def test_topic_index_starts_at_zero(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert sm.current_topic_index == 0

    def test_conversation_starts_empty(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert sm.conversation == []

    def test_evaluations_starts_empty(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert sm.evaluations == []


class TestAddMessage:
    def test_appends_to_conversation(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.add_message("interviewer", "What is your experience?")
        assert len(sm.conversation) == 1
        assert sm.conversation[0].role == "interviewer"
        assert sm.conversation[0].content == "What is your experience?"

    def test_uses_current_turn_number(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.current_turn = 3
        sm.add_message("candidate", "I have 5 years of experience.")
        assert sm.conversation[0].turn_number == 3

    def test_multiple_messages(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.add_message("interviewer", "Q1")
        sm.add_message("candidate", "A1")
        sm.add_message("interviewer", "Q2")
        assert len(sm.conversation) == 3


class TestGetLastQuestion:
    def test_returns_empty_when_no_messages(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert sm.get_last_question() == ""

    def test_finds_interviewer_message(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.add_message("interviewer", "Tell me about yourself.")
        assert sm.get_last_question() == "Tell me about yourself."

    def test_skips_candidate_messages(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.add_message("interviewer", "Q1")
        sm.add_message("candidate", "A1")
        assert sm.get_last_question() == "Q1"

    def test_returns_most_recent_interviewer_message(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.add_message("interviewer", "Q1")
        sm.add_message("candidate", "A1")
        sm.add_message("interviewer", "Q2")
        sm.add_message("candidate", "A2")
        assert sm.get_last_question() == "Q2"


class TestShouldConclude:
    def test_false_when_both_remain(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert not sm.should_conclude()

    def test_true_when_turns_exhausted(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.current_turn = sample_plan.total_turns
        assert sm.should_conclude()

    def test_true_when_turns_exceed_max(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.current_turn = sample_plan.total_turns + 1
        assert sm.should_conclude()

    def test_true_when_topics_exhausted(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.current_topic_index = len(sample_plan.topics)
        assert sm.should_conclude()


class TestDecideNextAction:
    def test_follow_up_on_probe_deeper(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        ev = make_eval([EvaluatorSignal.probe_deeper])
        assert sm.decide_next_action(ev) == "follow_up"

    def test_next_topic_on_move_on(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        ev = make_eval([EvaluatorSignal.move_on])
        assert sm.decide_next_action(ev) == "next_topic"

    def test_next_topic_after_two_followups(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        ev = make_eval([EvaluatorSignal.probe_deeper])
        assert sm.decide_next_action(ev) == "follow_up"
        assert sm.decide_next_action(ev) == "follow_up"
        assert sm.decide_next_action(ev) == "next_topic"

    def test_conclude_overrides_probe_deeper(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.current_turn = sample_plan.total_turns
        ev = make_eval([EvaluatorSignal.probe_deeper])
        assert sm.decide_next_action(ev) == "conclude"

    def test_conclude_overrides_move_on(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        sm.current_turn = sample_plan.total_turns
        ev = make_eval([EvaluatorSignal.move_on])
        assert sm.decide_next_action(ev) == "conclude"

    def test_default_action_is_follow_up(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        ev = make_eval([EvaluatorSignal.increase_difficulty])
        assert sm.decide_next_action(ev) == "follow_up"

    def test_default_with_decrease_difficulty(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        ev = make_eval([EvaluatorSignal.decrease_difficulty])
        assert sm.decide_next_action(ev) == "follow_up"

    def test_followup_limit_resets_per_topic(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        ev_probe = make_eval([EvaluatorSignal.probe_deeper])
        sm.decide_next_action(ev_probe)
        sm.decide_next_action(ev_probe)
        sm.advance_topic()
        assert sm.decide_next_action(ev_probe) == "follow_up"


class TestAdvanceTopic:
    def test_increments_index(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert sm.current_topic_index == 0
        sm.advance_topic()
        assert sm.current_topic_index == 1

    def test_current_topic_changes(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        assert sm.get_current_topic().name == "Leadership"
        sm.advance_topic()
        assert sm.get_current_topic().name == "Strategy"
        sm.advance_topic()
        assert sm.get_current_topic().name == "Execution"


class TestAddEvaluation:
    def test_appends_evaluation(self, sample_plan):
        sm = InterviewStateManager(sample_plan)
        ev = make_eval([EvaluatorSignal.move_on])
        sm.add_evaluation(ev)
        assert len(sm.evaluations) == 1
        assert sm.evaluations[0] is ev
