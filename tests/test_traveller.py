"""This module tests Hierholzer's algorithm"""

import logging
from ait.base import Arrow

from ait.traveller import Hierholzer
from ait.finite_state_machine import GraphWrapper
from ait.utils import eulerize
from tests.common import SAMPLE_DATA


def dump_fsm(fsm: GraphWrapper, filename: str):
    """
    Export the finite state machine to a csv matrix and a graph

    :param fsm: the finite state machine
    :type fsm: FiniteStateMachine
    :param filename: the filename to be used in csv and svg files
    :type filename: str
    """
    fsm.write_to_csv(f"logs/{filename}.csv")

    # add label to vertices and edges
    v_labels = {}
    for vertex in fsm.graph.vs:
        name = vertex.attributes()["name"]
        v_labels[name] = {"label": name}
    fsm.update_node_attr(v_labels)

    e_labels = {}
    for edge in fsm.graph.es:
        name = edge.attributes()["name"]
        e_labels[name] = {"label": name}
    fsm.update_edge_attr(e_labels)
    fsm.export_graph(f"logs/{filename}.svg", (0, 0, 500, 500))


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

    fsm = GraphWrapper()
    fsm.load_from_dict(input_data)
    dump_fsm(fsm, "test_traveller")

    hhz = Hierholzer(fsm.graph)

    # WHEN
    track = hhz.travel("A")
    logging.info(hhz.dump_path())

    # THEN
    eulerize(fsm.graph)  # make the graph Eulerian to compare the result
    expect_result = fsm.arcs.copy()

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
