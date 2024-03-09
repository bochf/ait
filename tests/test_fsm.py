"""
This moudle test FiniteStateMachine
"""

import logging

from ait.finite_state_machine import GraphWrapper
from ait.base import Arrow
from tests.common import SAMPLE_DATA


def verify_fsm(fsm: GraphWrapper, nodes: list[str], arrows: list[Arrow]):
    """verify a finite state machine is as expected"""
    assert len(fsm.nodes) == len(nodes)
    assert len(fsm.arcs) == len(arrows)

    for name in nodes:
        assert fsm.has_node(name)

    for arc in arrows:
        assert fsm.get_arcs(arc)


def test_add_nodes():
    """test add a new state to a fsm"""
    # GIVEN an empty finite state machine
    fsm = GraphWrapper()

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
    """test add edges"""
    # GIVEN an empty finite state machine
    fsm = GraphWrapper()
    connections = []

    # WHEN add a new arc
    conn = Arrow("A", "B", "1")
    connections.append(conn)
    fsm.add_arc(conn)

    # THEN
    verify_fsm(fsm, ["A", "B"], connections)

    # WHEN add another arc
    conn = Arrow("A", "C", "2")
    connections.append(conn)
    fsm.add_arc(conn)

    # THEN
    verify_fsm(fsm, ["A", "B", "C"], connections)


def test_load_from_dict():
    """test load graph from dictionary"""
    # GIVEN
    input_dict = SAMPLE_DATA.copy()

    # WHEN
    fsm = GraphWrapper()
    fsm.load_from_dict(input_dict)

    output = fsm.export_to_dict()

    # THEN
    assert input_dict == output
    logging.info("%s", output)


def test_export_to_csv():
    """test export fsm to csv file"""
    # GIVEN
    fsm = GraphWrapper()
    fsm.load_from_dict(SAMPLE_DATA)

    # WHEN
    fsm.write_to_csv("logs/test_fsm.csv")

    # THEN
    fsm2 = GraphWrapper()
    fsm2.read_from_csv("logs/test_fsm.csv")
    output_data = fsm2.export_to_dict()
    assert output_data == SAMPLE_DATA
