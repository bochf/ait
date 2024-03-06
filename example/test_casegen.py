"""
Automatically generate integration test cases for Arbiter
"""

import logging

from ait.state_engine import StateEngine
from ait.utils import eulerize
from ait.traveller import Hierholzer
from example.sut_arb import MockArbiter


def test_arb():
    """main entry"""
    test_data = {
        "roomId": "chat-123",
        "creator": "user1",
        "participants": ["user2"],
        "inviter": "user1",
        "invitees": ["user2"],
        "remover": "user1",
        "removee": "user2",
        "user": "user1",
        "content": "test content",
    }
    arb = MockArbiter(test_data)
    engine = StateEngine(arb)

    # construct a finite state machine by trying all states and requests
    engine.evolve(MockArbiter.states["no room"])
    fsm = engine.state_machine

    # show the state machine
    state_labels = {name: {"label": name, "size": 60} for name in MockArbiter.states}
    fsm.update_node_attr(state_labels)
    event_labels = {}
    for event_name in MockArbiter.events:
        event_labels[event_name] = {"label": str(len(event_labels))}
    fsm.update_edge_attr(event_labels)
    fsm.write_to_csv("logs/arb.csv")
    fsm.export_graph("logs/arb.svg", show_self_circle=False, margin=150)

    # generate test cases
    eulerize(fsm.graph)
    fsm.export_graph("logs/euler_arb.svg", show_self_circle=False, margin=150)
    hhz = Hierholzer(fsm.graph)
    path = hhz.travel("no room")
    assert path
    logging.info("path length=%d", len(path))

    result = path[-1][0]
    for state, event in path[-2::-1]:
        result += "--" + event + "->" + state
    logging.info("path=%s", result)
