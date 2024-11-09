"""This module tests Hierholzer's algorithm"""

import logging
from igraph import Graph
from ait.graph_wrapper import Arrow

from ait.strategy.edge_cover import EdgeCover
from ait.strategy.node_cover import NodeCover
from ait.fsm_exporter import FsmExporter
from ait.graph_wrapper import GraphWrapper
from ait.strategy.edge_cover import eulerize
from ait.fsm_importer import FsmImporter


def _dump_graph(graph: GraphWrapper, filename: str):
    """
    Export data in a directed graph to a csv matrix and a svg file

    :param graph: the state graph
    :type graph: GraphWrapper
    :param filename: the filename to be used in csv and svg files
    :type filename: str
    """
    FsmExporter(graph).to_csv(f"logs/{filename}.csv")

    # add label to vertices and edges
    v_labels = {}
    for vertex in graph.graph.vs:
        name = vertex.attributes()["name"]
        v_labels[name] = {"label": name}
    graph.update_node_attr(v_labels)

    e_labels = {}
    for edge in graph.graph.es:
        name = edge.attributes()["name"]
        e_labels[name] = {"label": name}
    graph.update_edge_attr(e_labels)
    try:
        FsmExporter(graph).to_svg(f"logs/{filename}.svg", (0, 0, 500, 500))
    except AttributeError as exc:
        logging.warning("Export graph to svg is not supported because: %s", exc)


def test_edge_coverage():
    """Test  EdgeCover strategy"""
    # GIVEN
    input_data = {
        "A": {"0": "B", "1": "E"},
        "B": {"2": "C"},
        "C": {"3": "A", "4": "D"},
        "D": {"5": "A", "6": "C"},
        "E": {"7": "B", "8": "C"},
    }

    importer = FsmImporter()
    state_machine = importer.from_dicts(input_data)
    _dump_graph(state_machine, "test_traveller")

    stg = EdgeCover()

    # WHEN
    track = stg.travel(state_machine, "A")
    logging.info(stg.tracks)

    # THEN
    eulerize(state_machine.graph)  # make the graph Eulerian to compare the result
    expect_result = state_machine.arcs.copy()

    actual_result = []
    source = track[-1][0]
    for path in track[-2::-1]:
        actual_result.append(Arrow(source, path[0], path[1]))
        source = path[0]

    assert len(expect_result) == len(actual_result)
    expect_result.sort()
    actual_result.sort()
    for elem in list(zip(expect_result, actual_result)):
        assert elem[0] == elem[1]


def get_least_in_degree_vertex(graph: Graph) -> int:
    """
    Get the vertex with the least in-degree

    :param g: the graph
    :type g: Graph
    :return: vertex index
    :rtype: int
    """
    degree = graph.vs[0].degree(mode="in")
    lowest = 0
    for i in range(1, len(graph.vs)):
        tmp = graph.vs[i].degree(mode="in")
        if tmp == 0:
            return i
        if tmp < degree:
            degree = tmp
            lowest = i
    return lowest


def test_node_coverage():
    """Test  NodeCover strategy"""
    # GIVEN
    state_machine = GraphWrapper()
    while True:
        state_machine.graph = Graph.Erdos_Renyi(10, m=16, directed=True)
        if state_machine.graph.is_connected(mode="weak"):
            break
    state_machine.graph.vs["name"] = [
        "S_" + str(i) for i in range(len(state_machine.graph.vs))
    ]
    state_machine.graph.vs["label"] = [
        "S_" + str(i) for i in range(len(state_machine.graph.vs))
    ]
    state_machine.graph.es["name"] = [
        "E_" + str(i) for i in range(len(state_machine.graph.es))
    ]
    _dump_graph(state_machine, "test_traveller")

    stg = NodeCover()

    # WHEN
    stg.travel(state_machine, get_least_in_degree_vertex(state_machine.graph))
    logging.info("all paths: \n%s", stg.tracks)


def test_node_coverage_multi_root():
    """
    Test node coverage with multipl root vertices
    """
    # GIVEN
    creator = FsmImporter()
    state_machine = creator.from_csv("tests/data/multi_root.csv")
    _dump_graph(state_machine, "multi_root")

    # get all the root vertices
    roots = set(
        vertex.index
        for vertex in state_machine.graph.vs
        if vertex.degree(mode="in") == 0
    )
    traveller = NodeCover()

    # WHEN
    traveller.travel(state_machine, roots.pop())
    logging.info("all paths: \n%s", traveller.tracks)

    # THEN
    # The remaining roots should be unvisited
    assert not roots - traveller.unvisited_nodes
    assert not traveller.unvisited_nodes - roots


def test_node_coverage_real_data():
    """
    Test the node coverage with the matrix generated from arbiter
    """
    # GIVEN
    state_machine = FsmImporter().from_csv("tests/data/arbiter.csv")
    _dump_graph(state_machine, "arbiter")
    traveller = NodeCover()

    # WHEN
    traveller.travel(state_machine, 0)
    logging.info("all paths: \n%s", traveller.tracks)


def test_edge_coverage_real_data():
    """
    Test the edge coverage with the matrix generated from arbiter
    """
    # GIVEN
    state_machine = FsmImporter().from_csv("tests/data/arbiter.csv")
    _dump_graph(state_machine, "arbiter")
    traveller = EdgeCover()

    # WHEN
    traveller.travel(state_machine, 0)
    logging.info("all paths: \n%s", traveller.tracks)
