"""This module test the utils."""

from ait.finite_state_machine import FiniteStateMachine
from ait.utils import Eulerian, is_eulerian, is_connected, eulerize
from tests.common import SAMPLE_DATA


def test_connectivity():
    """test connectivity of a state machine"""
    # GIVEN
    fsm = FiniteStateMachine()

    # THEN
    assert not is_connected(fsm.graph)

    # WHEN
    fsm.load_from_dict(SAMPLE_DATA)

    # THEN the graph is connected
    assert is_connected(fsm.graph)

    # WHEN add a new node
    fsm.add_node("H")

    # THEN the new node does not connect to any other existing nodes
    assert not is_connected(fsm.graph)


def test_eulerian():
    """test eulerian of a graph"""
    # GIVEN an empty graph
    fsm = FiniteStateMachine()

    # THEN empty graph is not a eulerian graph
    assert is_eulerian(fsm.graph) == Eulerian.NONE

    # WHEN add a node
    fsm.add_node("A")

    # THEN the graph is a eulerian graph
    assert is_eulerian(fsm.graph) == Eulerian.CIRCUIT

    # WHEN add another node
    fsm.add_node("B")

    # THEN the graph is still not a eulerian graph be cause 2 nodes are not connected
    assert is_eulerian(fsm.graph) == Eulerian.NONE

    # WHEN connecte the 2 nodes
    fsm.add_arc("A", "B", "INVITE")

    # THEN the graph has a eulerian path A to B
    assert is_eulerian(fsm.graph) == Eulerian.PATH

    # WHN add a backward connection
    fsm.add_arc("B", "A", "OK")

    # THEN the graph has a eulerian circuit
    assert is_eulerian(fsm.graph) == Eulerian.CIRCUIT

    # WHEN add a forward edge again
    fsm.add_arc("A", "B", "ACK")

    # THEN the graph becomes a semi eulerian graph again
    assert is_eulerian(fsm.graph) == Eulerian.PATH


def test_eulerize():
    """test eularize graph"""
    # GIVEN
    input_data = {
        "A": {"B": {"name": "ab"}, "C": {"name": "ac"}, "D": {"name": "ad"}},
        "B": {"C": {"name": "bc"}, "D": {"name": "ad"}},
        "C": {"D": {"name": "cd"}},
        "D": {"A": {"name": "da"}},
    }
    fsm = FiniteStateMachine()
    fsm.load_from_dict(input_data)
    fsm.export_graph("fsm.svg", (0, 0, 600, 600), margin=100)

    # WHEN
    eulerize(fsm.graph)

    # THEN
    assert is_eulerian(fsm.graph) != Eulerian.NONE
    fsm.export_graph("euler.svg", (0, 0, 600, 600), margin=100)
