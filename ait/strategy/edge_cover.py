"""
This module implement an Eular walk of a connected directed graph based on the
Hierholzer'a algorithm. If the graph is not an Eularian graph, repeat some
existing edges to make it Eularian, i.e. allow walking through some edges more
than once.
"""

from enum import Enum
import logging
import random

from igraph import Graph, Edge

from ait.graph_wrapper import Arrow, GraphWrapper, is_connected
from ait.utils import shortest_path
from ait.errors import UnknownState
from ait.strategy.strategy import Strategy


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


class EdgeCover(Strategy):
    """
    Hierholzer algorithm traversing a directed Eulerian graph
    """

    def __init__(self, self_circle=False):
        super().__init__()
        self._self_circle = self_circle

    def travel(self, state_machine: GraphWrapper, start: str) -> list[tuple[str, str]]:
        """
        Traverse a graph using Hierholzer's algorithm.
        If the graph is not a Eulerian graph, add edges to make it eulerian.

        :param start: the start point
        :type start: str
        :param self_circle: include self circuit or not, defaults to False
        :type self_circle: bool, optional
        :return: list of vertex and edge pairs
        :rtype: list[tuple[str, str]]
        """

        graph = state_machine.graph.copy()
        if not self._self_circle:
            # delete self circle edge
            def self_circuit(edge: Edge) -> bool:
                return edge.source == edge.target

            graph.delete_edges(self_circuit)
        if is_eulerian(graph) == Eulerian.NONE:
            eulerize(graph)

        self._paths.clear()
        self._dfs(graph, start)
        self._paths.reverse()
        return self._paths

    def _dfs(self, graph: Graph, current: str, incoming_edge: str = ""):
        """
        Depth First Search
        Start from current vertex, choose the first outgoing edge to traverse
        to the adjacent vertex and delete the edge. Call the dfs method on the
        new vertex until the vertex has no outgoing edge. Push the edge and
        the vertex into the stack. Continue the search on the next edge of the
        predecessor vertex until all no edge left.

        :param graph: the graph to traverse
        :type graph: Graph
        :param current: name of current vertex
        :type current: str
        :param incoming_edge: the edge points to this vertex
        :type incoming_edge: str, optional
        :raises UnknownState: if the vertex does not exist
        """
        try:
            vertex = graph.vs.find(current)
            # logging.debug("Visit vertex %s", current)
            while True:
                out_edges = vertex.out_edges()
                if not out_edges:
                    # push the vertex and the incoming edge into the stack when
                    # there is no outgoing edge
                    self._paths.append((current, incoming_edge))
                    break

                # edge = out_edges[0]
                edge = random.choice(out_edges)
                # move to the adjacent vertex and delete the edge
                adjacent = graph.vs[edge.target].attributes()["name"]
                edge_name = edge.attributes()["name"]
                graph.delete_edges(edge.index)
                self._dfs(graph, adjacent, edge_name)
        except ValueError as exc:
            logging.error("Error %s", exc)
            raise UnknownState from exc
