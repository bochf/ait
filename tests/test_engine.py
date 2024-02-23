from typing import Literal
import pytest

from ait.base import InvalidState
from ait.state_engine import StateEngine
from tests.common import TestEvent, STATES, EVENTS, TRANSITION_TABLE


@pytest.mark.parametrize(
    "transition",
    [
        ("Start", "Initialize", "Running"),
        ("Start", "Reset", "Start"),
        ("Running", "Pause", "Paused"),
        ("Running", "Stop", "Stopped"),
        ("Paused", "Resume", "Running"),
        ("Paused", "Stop", "Stopped"),
        ("Stopped", "Reset", "Start"),
    ],
)
def test_transition(transition: Literal["Start"]):
    """test state transitions"""
    # GIVEN
    source_name = transition[0]
    expected_target_name = transition[2]
    event_name = transition[1]
    source = STATES[source_name]
    event = TestEvent(event_name)

    # WHEN
    target_state, response = event.fire(source, {})

    # THEN
    assert response["return_code"] == 0
    assert target_state == STATES[expected_target_name]


def test_invalide_transition():
    """test invalid transitions"""
    # GIVEN
    for source in STATES.values():
        for event in EVENTS:
            # WHEN
            if not event.name in TRANSITION_TABLE[source.name]["transitions"]:
                target_state, response = event.fire(source, {})

                # THEN
                assert response["return_code"] == -1
                assert not target_state.is_valid


def test_engine():
    """test state engine"""
    # GIVEN
    init_state = STATES["Start"]
    engine = StateEngine(init_state, EVENTS)
    engine.evolve(init_state)
