"""
This module defines directed graph related helper functions  
"""

import logging

from igraph import Graph

from ait.graph_wrapper import Arrow


def shortest_path(graph: Graph, source: str, target: str) -> list[Arrow]:
    """
    Get the shortest path between the source and target

    :param source: the name of the source state
    :type source: str
    :param target: the name of the target state
    :type target: str
    :return: list of arrows
    :rtype: list[Arrow]
    """
    path = graph.get_shortest_path(source, target, output="epath")
    if not path:
        logging.warning("No path from %s to %s", source, target)
        return []

    result = []
    vs = graph.vs
    for eid in path:
        edge = graph.es[eid]
        result.append(
            Arrow(
                vs[edge.source].attributes()["name"],
                vs[edge.target].attributes()["name"],
                edge.attributes()["name"],
            )
        )

    return result
