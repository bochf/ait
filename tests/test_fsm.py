"""
This moudle test FiniteStateMachine
"""

import logging
from ait.finite_state_machine import FiniteStateMachine, Arrow, Eulerian

SAMPLE_DATA = {
    "A": {"B": {"label": "1"}, "C": {"label": "2"}},
    "B": {"D": {"label": "3"}},
    "C": {"D": {"label": "4"}},
    "D": {"E": {"label": "5"}, "F": {"label": "6"}},
    "E": {"G": {"label": "7"}},
    "F": {"G": {"label": "8"}},
}


def verify_fsm(fsm: FiniteStateMachine, nodes: list[str], arrows: list[Arrow]):
    """verify a finite state machine is as expected"""
    assert len(fsm.nodes) == len(nodes)
    assert len(fsm.arcs) == len(arrows)

    for name in nodes:
        assert fsm._has_node(name)

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
    """test add edges"""
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


def test_load_from_dict():
    """test load graph from dictionary"""
    # GIVEN
    input_dict = SAMPLE_DATA.copy()

    # WHEN
    fsm = FiniteStateMachine()
    fsm.load_from_dict(input_dict)

    output = fsm.export_to_dict()

    # THEN
    assert input_dict == output
    logging.info("%s", output)


def test_connectivity():
    """test connectivity of a state machine"""
    # GIVEN
    fsm = FiniteStateMachine()

    # THEN
    assert not fsm.is_connected

    # WHEN
    fsm.load_from_dict(SAMPLE_DATA)

    # THEN the graph is connected
    assert fsm.is_connected

    # WHEN add a new node
    fsm.add_node("H")

    # THEN the new node does not connect to any other existing nodes
    assert not fsm.is_connected


def test_export_to_csv():
    """test export fsm to csv file"""
    # GIVEN
    fsm = FiniteStateMachine()
    fsm.load_from_dict(SAMPLE_DATA)

    # WHEN
    fsm.write_to_csv("fsm.csv")

    # THEN
    fsm2 = FiniteStateMachine()
    fsm2.read_from_csv("fsm.csv")
    output_data = fsm2.export_to_dict()
    assert output_data == SAMPLE_DATA


def test_eulerian():
    """test eulerian of a graph"""
    # GIVEN an empty graph
    fsm = FiniteStateMachine()

    # THEN empty graph is not a eulerian graph
    assert fsm.eulerian == Eulerian.NONE

    # WHEN add a node
    fsm.add_node("A")

    # THEN the graph is a eulerian graph
    assert fsm.eulerian == Eulerian.CIRCUIT

    # WHEN add another node
    fsm.add_node("B")

    # THEN the graph is still not a eulerian graph be cause 2 nodes are not connected
    assert fsm.eulerian == Eulerian.NONE

    # WHEN connecte the 2 nodes
    fsm.add_arc("A", "B", "INVITE")

    # THEN the graph has a eulerian path A to B
    assert fsm.eulerian == Eulerian.PATH

    # WHN add a backward connection
    fsm.add_arc("B", "A", "OK")

    # THEN the graph has a eulerian circuit
    assert fsm.eulerian == Eulerian.CIRCUIT

    # WHEN add a forward edge again
    fsm.add_arc("A", "B", "ACK")

    # THEN the graph becomes a semi eulerian graph again
    assert fsm.eulerian == Eulerian.PATH


def test_eulerize():
    """test eularize graph"""
    # GIVEN
    input_data = {
        "A": {"B": {"label": "ab"}, "C": {"label": "ac"}, "D": {"label": "ad"}},
        "B": {"C": {"label": "bc"}, "D": {"label": "ad"}},
        "C": {"D": {"label": "cd"}},
        "D": {"A": {"label": "da"}},
    }
    fsm = FiniteStateMachine()
    fsm.load_from_dict(input_data)
    fsm.export_graph("fsm.svg", (0, 0, 600, 600), margin=100)

    # WHEN
    fsm.eulerize()

    # THEN
    assert fsm.eulerian != Eulerian.NONE
    fsm.export_graph("euler.svg", (0, 0, 600, 600), margin=100)
