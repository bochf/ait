"""This module tests Hierholzer's algorithm"""

import logging
from ait.graph_wrapper import Arrow

from ait.strategy.edge_cover import EdgeCover
from ait.graph_wrapper import GraphWrapper
from ait.strategy.edge_cover import eulerize


def _dump_graph(graph: GraphWrapper, filename: str):
    """
    Export data in a directed graph to a csv matrix and a svg file

    :param graph: the state graph
    :type graph: GraphWrapper
    :param filename: the filename to be used in csv and svg files
    :type filename: str
    """
    graph.write_to_csv(f"logs/{filename}.csv")

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
    graph.export_graph(f"logs/{filename}.svg", (0, 0, 500, 500))


def test_euler_path():
    """Test  Hierholzer's algorithm"""
    # GIVEN
    input_data = {
        "A": {"B": {"name": "1"}, "E": {"name": "2"}},
        "B": {"C": {"name": "3"}},
        "C": {"A": {"name": "4"}, "D": {"name": "5"}},
        "D": {"A": {"name": "6"}, "C": {"name": "7"}},
        "E": {"B": {"name": "8"}, "C": {"name": "9"}},
    }

    state_graph = GraphWrapper()
    state_graph.load_from_dict(input_data)
    _dump_graph(state_graph, "test_traveller")

    hhz = EdgeCover()

    # WHEN
    track = hhz.travel(state_graph, "A")
    logging.info(hhz.dump_path())

    # THEN
    eulerize(state_graph.graph)  # make the graph Eulerian to compare the result
    expect_result = state_graph.arcs.copy()

    actual_result = []
    source = track[-1][0]
    for path in track[-2::-1]:
        actual_result.append(Arrow(source, path[0], path[1]))
        source = path[0]

    assert len(expect_result) == len(actual_result)
    expect_result.sort()
    actual_result.sort()
    for i in range(len(actual_result)):
        assert expect_result[i] == actual_result[i]
