"""
This moudle test FiniteStateMachine
"""

import logging

from ait.graph_wrapper import GraphWrapper
from ait.graph_wrapper import Arrow
from tests.common import SAMPLE_DATA


def verify_graph(state_graph: GraphWrapper, nodes: list[str], arrows: list[Arrow]):
    """verify a graph wrapper is as expected"""
    assert len(state_graph.nodes) == len(nodes)
    assert len(state_graph.arcs) == len(arrows)

    for name in nodes:
        assert state_graph.has_node(name)

    for arc in arrows:
        assert state_graph.get_arcs(arc)


def test_add_nodes():
    """test add a new state to a state graph"""
    # GIVEN an empty finite state machine
    state_graph = GraphWrapper()

    # WHEN add a new state
    state_graph.add_node("A")

    # THEN
    verify_graph(state_graph, ["A"], [])

    # WHEN add another state
    state_graph.add_node("B")

    # THEN
    verify_graph(state_graph, ["A", "B"], [])

    # WHEN add the same state again
    state_graph.add_node("A")

    # THEN
    verify_graph(state_graph, ["A", "B"], [])


def test_add_arcs():
    """test add edges"""
    # GIVEN an empty finite state machine
    state_graph = GraphWrapper()
    connections = []

    # WHEN add a new arc
    conn = Arrow("A", "B", "1")
    connections.append(conn)
    state_graph.add_arc(conn)

    # THEN
    verify_graph(state_graph, ["A", "B"], connections)

    # WHEN add another arc
    conn = Arrow("A", "C", "2")
    connections.append(conn)
    state_graph.add_arc(conn)

    # THEN
    verify_graph(state_graph, ["A", "B", "C"], connections)


def test_load_from_dict():
    """test load graph from dictionary"""
    # GIVEN
    input_dict = SAMPLE_DATA.copy()

    # WHEN
    state_graph = GraphWrapper()
    state_graph.load_from_dict(input_dict)

    output = state_graph.export_to_dict()

    # THEN
    assert input_dict == output
    logging.info("%s", output)


def test_export_to_csv():
    """test export data from graph wrpper to a csv file"""
    # GIVEN
    state_graph = GraphWrapper()
    state_graph.load_from_dict(SAMPLE_DATA)

    # WHEN
    state_graph.write_to_csv("logs/test_export_state_graph.csv")

    # THEN
    sg2 = GraphWrapper()
    sg2.read_from_csv("logs/test_export_state_graph.csv")
    output_data = sg2.export_to_dict()
    assert output_data == SAMPLE_DATA
