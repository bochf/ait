"""Test state transitions"""

import logging
import pytest

from ait.explorer import Explorer
from ait.fsm_exporter import FsmExporter
from tests.common import EventTest, AppTest
from ait.strategy.edge_cover import EdgeCover
from ait.strategy.node_cover import NodeCover

EVENT_LIST = {
    name: EventTest(name) for name in ["Initialize", "Reset", "Pause", "Stop", "Resume"]
}


@pytest.mark.parametrize(
    "transition",
    [  # current state, event, target state
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
    test_app = AppTest()
    source_name = transition[0]
    test_app.state = AppTest.state_list[source_name]
    expected_target_name = transition[2]
    event_name = transition[1]
    event = EventTest(event_name)

    # WHEN
    output = event.fire(test_app)

    # THEN
    assert "success" in output
    assert test_app.state == AppTest.state_list[expected_target_name]


def test_invalide_transition():
    """test invalid transitions"""
    # GIVEN
    test_app = AppTest()
    for source in AppTest.state_list.values():
        test_app.state = source
        for event in EVENT_LIST.values():
            # WHEN
            if not event.name in AppTest.transition_table[source.name]:
                output = event.fire(test_app)

                # THEN
                assert "error" in output
                assert test_app.state == source


def test_engine():
    """test state engine"""
    # GIVEN
    test_app = AppTest()
    init_state = test_app.start()
    explorer = Explorer(test_app, EVENT_LIST)
    explorer.explore(init_state)
    state_graph = explorer.state_machine
    logging.info("matrix=%s", explorer.maze)
    exporter = FsmExporter(state_graph)
    exporter.to_svg(
        "logs/test_engine.svg",
        show_self_circle=False,
        margin=100,
    )
    exporter.to_csv("logs/test_engine.csv", True)

    state_traveller = NodeCover()
    state_traveller.travel(explorer.state_machine, "Idle")
    logging.info(
        "Paths start from initial state to all other states at least once: \n%s",
        state_traveller.tracks,
    )

    transition_traveller = EdgeCover()
    transition_traveller.travel(explorer.state_machine, "Idle")
    logging.info(
        "Paths start from initial state via all transitions at least once: \n%s",
        transition_traveller.tracks,
    )
