"""
This module defines directed graph related helper functions  
"""

import logging
from enum import Enum

from igraph import Graph

from ait.base import Arrow


class Eulerian(Enum):
    """
    The Eulerian property of a graph
    NONE: the graph is not a Eulerian graph
    CIRCUIT: the graph has a Eulerian cycle, can start from any vertex, walk
             through every edge one and only one time and go back the start
             vertex.
    PATH: the graph has a Eulerian path, can start from one vertex, walk
          through every edge one and only one time and finished at a different
          vertex.
    """

    NONE = 0  # non eulerian graph
    CIRCUIT = 1  # eulerian graph
    PATH = 2  # semi-eularian graph


def is_connected(graph: Graph) -> bool:
    """
    Check all the vertices are connected. If the graph is weak connected
    return true, we don't need bidirection connected.

    :return: true if the graph is connected
    :rtype: bool
    """
    return graph.is_connected(mode="weak")


def get_uneven_pair(graph) -> tuple[str, str]:
    """
    Get one hub and one sink vertices from the graph

    :return: pair of vertices name
    :rtype: tuple[str, str]
    """
    hub = ""  # in_degree < out_degree
    sink = ""  # in_degree > out_degree

    for vtx in graph.vs:
        diff = vtx.degree(mode="out") - vtx.degree(mode="in")
        if diff > 0:
            hub = vtx.attributes()["name"]
        elif diff < 0:
            sink = vtx.attributes()["name"]

        if hub and sink:  # stop search when both are found
            break

    return hub, sink


def is_eulerian(graph: Graph) -> Eulerian:
    """
    Check the graph is a semi-Eularian, Eularian graph or not

    :return: type of Eulerian
    :rtype: Eulerian
    """
    if not is_connected(graph):
        return Eulerian.NONE

    uneven_degrees = set()

    for vertex in graph.vs:
        logging.info(
            "vertex %s, degreee=%d, in_degree=%d, out_degree=%d",
            vertex.attributes()["name"],
            vertex.degree(),
            vertex.degree(mode="in"),
            vertex.degree(mode="out"),
        )
        diff = vertex.degree(mode="out") - vertex.degree(mode="in")
        if diff == 0:  # even vertex
            continue
        if diff > 1 or diff < -1:  # degree difference > 1
            return Eulerian.NONE
        if diff in uneven_degrees:  # more than 1 hub or sink vertex
            return Eulerian.NONE
        uneven_degrees.add(diff)
    if len(uneven_degrees) == 0:
        # all the vertex in and out dgrees are the same, has a circuit
        return Eulerian.CIRCUIT
    if len(uneven_degrees) == 2:
        # a path starts from the hub vertex ends at the sink vertex
        return Eulerian.PATH

    return Eulerian.NONE


def eulerize(graph: Graph) -> Eulerian:
    """
    Make a directed graph a Eulerian graph by duplicating existing edges
    between imbalanced vertices

    :param graph: the graph to be converted
    :type graph: Graph
    :return: the eulrian property of the result
    :rtype: Eulerian
    """
    # if a graph is already a eulerian graph, no-op
    eul = is_eulerian(graph)
    if eul != Eulerian.NONE:
        return eul

    # check a graph is eulerizable
    if not is_connected(graph):
        return Eulerian.NONE

    # eulerize a graph by repeating edges between uneven vertices
    while True:
        # get all the
        hub, sink = get_uneven_pair(graph)
        if not hub and not sink:
            logging.debug("No uneven vertex, the graph is a eulerian graph.")
            return Eulerian.CIRCUIT
        if not hub or not sink:
            logging.error(
                "Only has hub vertex %s or sink vertex %s, the graph is invalid.",
                hub,
                sink,
            )
            return Eulerian.NONE

        path = shortest_path(graph, sink, hub)
        if not path:
            # if no path from the sink vertex to the hub vertex, the graph is
            # - either a semi-eularian graph, it has a Euler path, the sink and
            #   hub vertices are the start and end points
            # - or not able to be converted to a Eulerian graph by adding existing
            #   edges.
            return is_eulerian(graph)

        # add arcs from the sink node to the hub node to make at least one node even
        duplicate_path(graph, path)


def duplicate_path(graph: Graph, path: list[Arrow]):
    """
    Add duplicated path in the graph

    :param graph: the graph to be manipulated
    :type graph: Graph
    :param path: the list of tuples of source, target and edge
    :type path: list[Arrow]
    """
    if not path:
        return

    try:
        v_from = graph.vs.find(path[0].tail)
        v_to = graph.vs.find(path[-1].head)
        repeat = min(
            v_from.degree(mode="in") - v_from.degree(mode="out"),
            v_to.degree(mode="out") - v_to.degree(mode="in"),
        )
        for _ in range(repeat):
            # copy the path until one of the vertex is balanced
            for arc in path:
                graph.add_edge(arc.tail, arc.head, name=arc.name)
    except ValueError as exc:
        logging.warning("Error occurred: %s", exc)


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
