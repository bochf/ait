"""Test state transitions"""

from typing import Literal
import pytest

from ait.state_engine import StateEngine
from tests.common import TestEvent, TestApp


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
    test_app = TestApp()
    source_name = transition[0]
    test_app.state = TestApp.state_list[source_name]
    expected_target_name = transition[2]
    event_name = transition[1]
    event = TestEvent(event_name)

    # WHEN
    target_state, response = event.fire(test_app, {})

    # THEN
    assert "success" in response
    assert target_state == TestApp.state_list[expected_target_name]


def test_invalide_transition():
    """test invalid transitions"""
    # GIVEN
    test_app = TestApp()
    for source in TestApp.state_list.values():
        test_app.state = source
        for event in TestApp.event_list.values():
            # WHEN
            if not event.name in TestApp.transition_table[source.name]:
                target_state, response = event.fire(test_app, {})

                # THEN
                assert "error" in response
                assert not target_state.is_valid


def test_engine():
    """test state engine"""
    # GIVEN
    init_state = TestApp.state_list["Start"]
    engine = StateEngine(init_state, list(TestApp.event_list.values()))
    engine.evolve(init_state)
