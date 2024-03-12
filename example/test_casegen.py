"""
Automatically generate integration test cases for Arbiter
"""

import logging

from ait.state_engine import StateEngine
from ait.strategy.edge_cover import eulerize
from ait.strategy.edge_cover import EdgeCover
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
    state_graph = engine.state_graph

    # show the state machine
    state_labels = {name: {"label": name, "size": 60} for name in MockArbiter.states}
    state_graph.update_node_attr(state_labels)
    event_labels = {}
    for event_name in MockArbiter.events:
        event_labels[event_name] = {"label": str(len(event_labels))}
    state_graph.update_edge_attr(event_labels)
    state_graph.write_to_csv("logs/arb.csv")
    state_graph.export_graph("logs/arb.svg", show_self_circle=False, margin=150)

    # generate test cases
    eulerize(state_graph.graph)
    state_graph.export_graph("logs/euler_arb.svg", show_self_circle=False, margin=150)
    hhz = EdgeCover()
    path = hhz.travel(state_graph, "no room")
    assert path
    logging.info("path length=%d", len(path))

    result = path[-1][0]
    for state, event in path[-2::-1]:
        result += "--" + event + "->" + state
    logging.info("path=%s", result)
