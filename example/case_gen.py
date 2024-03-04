"""
Automatically generate integration test cases for Arbiter
"""

import logging

from ait.base import Event, State
from ait.sut import SUT
from ait.state_engine import StateEngine
from ait.finite_state_machine import FiniteStateMachine
from example.sut_arb import MockArbiter
from example.st_arb import ArbiterState
from example.evt_arb import ArbiterEvent


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

    engine.evolve(MockArbiter.states["no room"])

    fsm = engine.state_machine
    fsm.write_to_csv("fsm.csv")
    fsm.export_graph("arb.svg")
