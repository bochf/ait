"""
This moudle test FiniteStateMachine
"""

import logging

from ait.finite_state_machine import FiniteStateMachine, Arrow


def verify_fsm(fsm: FiniteStateMachine, nodes: list[str], arrows: list[Arrow]):
    """verify a finite state machine is as expected"""
    assert len(fsm.nodes) == len(nodes)
    assert len(fsm.arcs) == len(arrows)

    for name in nodes:
        assert fsm.find_node(name)

    for arc in arrows:
        assert fsm.get_arcs(arc.tail, arc.head, arc.name)


def test_add_nodes():
    """test add a new state to a fsm"""
    # GIVEN an empty finite state machine
    fsm = FiniteStateMachine()

    # WHEN add a new state
    fsm.add_node("A")

    # THEN
    verify_fsm(fsm, ["A"], [])

    # WHEN add another state
    fsm.add_node("B")

    # THEN
    verify_fsm(fsm, ["A", "B"], [])

    # WHEN add the same state again
    fsm.add_node("A")

    # THEN
    verify_fsm(fsm, ["A", "B"], [])


def test_add_arcs():
    # GIVEN an empty finite state machine
    fsm = FiniteStateMachine()
    connections = []

    # WHEN add a new arc
    conn = Arrow("A", "B", "1")
    connections.append(conn)
    fsm.add_arc(conn.tail, conn.head, conn.name)

    # THEN
    verify_fsm(fsm, ["A", "B"], connections)

    # WHEN add another arc
    conn = Arrow("A", "C", "2")
    connections.append(conn)
    fsm.add_arc(conn.tail, conn.head, conn.name)

    # THEN
    verify_fsm(fsm, ["A", "B", "C"], connections)
