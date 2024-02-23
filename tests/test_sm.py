"""
This moudle test the finite state machine
"""

import logging
from igraph import plot


from ait.finite_state_machine import FiniteStateMachine


def test_import():
    sm = FiniteStateMachine()
    sm.read_csv("tests/example.csv")
    sm.build_graph()
    paths = sm.get_shortest_paths("S000")
    for path in paths:
        if not path:
            continue

        logging.info("shortest path from S000 is %s", sm.path_to_str(path))

    layout_list = [
        "auto",
        "circle",
        "dh",
        "drl",
        "fr",
        "grid",
        "graphopt",
        "kk",
        "lgl",
        "mds",
        "random",
        "rt",
        "rt_circular",
        "star",
    ]

    for layout in layout_list:
        sm.export_graph(f"{layout}.svg", layout)
