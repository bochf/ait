import logging

from ait.traveller import Hierholzer
from ait.finite_state_machine import FiniteStateMachine


def test_euler_path():
    input_data = {
        "A": {"B": {"name": "1"}, "C": {"name": "2"}},
        "B": {"D": {"name": "3"}},
        "C": {"D": {"name": "4"}},
        "D": {"E": {"name": "5"}, "F": {"name": "6"}},
        "E": {"G": {"name": "7"}},
        "F": {"G": {"name": "8"}},
        "G": {"A": {"name": "9"}},
    }
    fsm = FiniteStateMachine()
    fsm.load_from_dict(input_data)
    fsm.write_to_csv("logs/fsm.csv")

    hhz = Hierholzer(fsm.graph)

    v_labels = {name: {"label": name} for name in input_data}
    fsm.update_node_attr(v_labels)
    e_labels = {}
    for value in input_data.values():
        for edge in value.values():
            name = edge["name"]
            e_labels[name] = {"label": name}
    fsm.update_edge_attr(e_labels)
    fsm.export_graph("logs/fsm.svg", (0, 0, 500, 500))

    track = hhz.travel("A")
