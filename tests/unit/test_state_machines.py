from algo_tf.state.child_intent_machine import can_transition as child_can_transition
from algo_tf.state.execution_cycle_machine import can_transition as cycle_can_transition
from algo_tf.state.mandate_machine import can_transition as mandate_can_transition


def test_mandate_halted_is_terminal() -> None:
    assert mandate_can_transition("HALTED", "ACTIVE") is False


def test_execution_cycle_transitions() -> None:
    assert cycle_can_transition("MONITORING", "WORKING") is True
    assert cycle_can_transition("WORKING", "ARMED") is False


def test_child_intent_transitions() -> None:
    assert child_can_transition("CREATED", "VALIDATING") is True
    assert child_can_transition("FILLED", "SUBMITTED") is False
