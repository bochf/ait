"""This module test the utils."""

from ait.graph_wrapper import GraphWrapper
from ait.strategy.edge_cover import Eulerian, eulerize, is_eulerian
from ait.graph_wrapper import is_connected
from ait.graph_wrapper import Arrow
from ait.fsm_importer import FsmImporter
from tests.common import SAMPLES


def test_connectivity():
    """test connectivity of a state machine"""
    # GIVEN
    state_graph = FsmImporter().from_dicts(SAMPLES["transitions"])
    assert is_connected(state_graph.graph)

    # WHEN add a new node
    state_graph.add_node("H")

    # THEN the new node does not connect to any other existing nodes
    assert not is_connected(state_graph.graph)


def test_eulerian():
    """test eulerian of a graph"""
    # GIVEN an empty graph
    state_graph = GraphWrapper()

    # THEN empty graph is not a eulerian graph
    assert is_eulerian(state_graph.graph) == Eulerian.NONE

    # WHEN add a node
    state_graph.add_node("A")

    # THEN the graph is a eulerian graph
    assert is_eulerian(state_graph.graph) == Eulerian.CIRCUIT

    # WHEN add another node
    state_graph.add_node("B")

    # THEN the graph is still not a eulerian graph be cause 2 nodes are not connected
    assert is_eulerian(state_graph.graph) == Eulerian.NONE

    # WHEN connecte the 2 nodes
    state_graph.add_arc(Arrow("A", "B", "INVITE"))

    # THEN the graph has a eulerian path A to B
    assert is_eulerian(state_graph.graph) == Eulerian.PATH

    # WHN add a backward connection
    state_graph.add_arc(Arrow("B", "A", "OK"))

    # THEN the graph has a eulerian circuit
    assert is_eulerian(state_graph.graph) == Eulerian.CIRCUIT

    # WHEN add a forward edge again
    state_graph.add_arc(Arrow("A", "B", "ACK"))

    # THEN the graph becomes a semi eulerian graph again
    assert is_eulerian(state_graph.graph) == Eulerian.PATH


def test_eulerize():
    """test eularize graph"""
    # GIVEN
    input_data = {
        "A": {"ab": "B", "ac": "C", "ad": "D"},
        "B": {"bc": "C", "bd": "D"},
        "C": {"cd": "D"},
        "D": {"da": "A"},
    }
    state_graph = FsmImporter().from_dicts(input_data)

    # WHEN
    eulerize(state_graph.graph)

    # THEN
    assert is_eulerian(state_graph.graph) == Eulerian.CIRCUIT
