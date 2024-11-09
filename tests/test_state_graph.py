"""
This moudle test FiniteStateMachine
"""

from ait.graph_wrapper import GraphWrapper, Arrow
from ait.fsm_importer import FsmImporter
from ait.fsm_exporter import FsmExporter
from tests.common import SAMPLES


def verify_graph(state_graph: GraphWrapper, nodes: list[str], arrows: list[Arrow]):
    """verify a graph wrapper is as expected"""
    assert len(state_graph.nodes) == len(nodes)
    assert len(state_graph.arcs) == len(arrows)

    for name in nodes:
        assert state_graph.get_node(name)

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
    state_graph = FsmImporter().from_dicts(
        SAMPLES["transitions"], SAMPLES["states"], SAMPLES["events"], SAMPLES["output"]
    )

    # WHEN
    transitions, states, events, output = FsmExporter(state_graph).to_dict()

    # THEN
    assert SAMPLES["transitions"] == transitions
    assert SAMPLES["states"] == states
    assert SAMPLES["events"] == events
    assert SAMPLES["output"] == output


def test_export_to_csv():
    """test export data from graph wrpper to a csv file"""
    # GIVEN
    state_graph = FsmImporter().from_dicts(
        SAMPLES["transitions"], SAMPLES["states"], SAMPLES["events"], SAMPLES["output"]
    )
    FsmExporter(state_graph).to_csv("logs/test_export_state_graph.csv", detail=True)

    # WHEN
    sg2 = FsmImporter().from_csv(
        "logs/test_export_state_graph.csv",
        "logs/test_export_state_graph_states.csv",
        "logs/test_export_state_graph_events.csv",
        "logs/test_export_state_graph_output.csv",
    )
    transitions, states, events, output = FsmExporter(sg2).to_dict()

    # THEN
    assert SAMPLES["transitions"] == transitions
    assert SAMPLES["states"] == states
    assert SAMPLES["events"] == events
    assert SAMPLES["output"] == output
