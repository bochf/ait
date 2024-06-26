"""This module tests Hierholzer's algorithm"""

import logging
from igraph import Graph
from ait.graph_wrapper import Arrow

from ait.strategy.edge_cover import EdgeCover
from ait.strategy.node_cover import NodeCover
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


def test_edge_coverage():
    """Test  EdgeCover strategy"""
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

    stg = EdgeCover()

    # WHEN
    track = stg.travel(state_graph, "A")
    logging.info(stg.dump_path())

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
    for elem in list(zip(expect_result, actual_result)):
        assert elem[0] == elem[1]


def get_least_in_degree_vertex(g: Graph) -> int:
    """
    Get the vertex with the least in-degree

    :param g: the graph
    :type g: Graph
    :return: vertex index
    :rtype: int
    """
    degree = g.vs[0].degree(mode="in")
    lowest = 0
    for i in range(1, len(g.vs)):
        tmp = g.vs[i].degree(mode="in")
        if tmp == 0:
            return i
        if tmp < degree:
            degree = tmp
            lowest = i
    return lowest


def test_node_coverage():
    """Test  NodeCover strategy"""
    # GIVEN
    state_graph = GraphWrapper()
    while True:
        state_graph._graph = Graph.Erdos_Renyi(10, m=16, directed=True)
        if state_graph._graph.is_connected(mode="weak"):
            break
    state_graph._graph.vs["name"] = [
        "S_" + str(i) for i in range(len(state_graph._graph.vs))
    ]
    state_graph._graph.vs["label"] = [
        "S_" + str(i) for i in range(len(state_graph._graph.vs))
    ]
    state_graph._graph.es["name"] = [
        "E_" + str(i) for i in range(len(state_graph._graph.es))
    ]
    _dump_graph(state_graph, "test_traveller")

    stg = NodeCover(state_graph)

    # WHEN
    stg.travel(get_least_in_degree_vertex(state_graph.graph))
    logging.info("all paths: \n%s", stg.dump_path())
