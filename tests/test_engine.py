"""Test state transitions"""

import logging
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
def test_transition(transition):
    """test state transitions"""
    # GIVEN
    test_app = TestApp()
    source_name = transition[0]
    test_app.state = TestApp.state_list[source_name]
    expected_target_name = transition[2]
    event_name = transition[1]
    event = TestEvent(event_name)

    # WHEN
    output = event.fire(test_app)

    # THEN
    assert output["success"]
    assert test_app.state == TestApp.state_list[expected_target_name]


def test_invalide_transition():
    """test invalid transitions"""
    # GIVEN
    test_app = TestApp()
    for source in TestApp.state_list.values():
        test_app.state = source
        for event in test_app.event_list.values():
            # WHEN
            if not event.name in TestApp.transition_table[source.name]:
                output = event.fire(test_app)

                # THEN
                assert not output["success"]
                assert test_app.state == source


def test_engine():
    """test state engine"""
    # GIVEN
    test_app = TestApp()
    init_state = test_app.start()
    engine = StateEngine(test_app)
    engine.evolve(init_state)
    state_graph = engine.state_graph
    logging.info("matrix=%s", engine.matrix)
    state_graph.export_graph("logs/test_engine.svg")
