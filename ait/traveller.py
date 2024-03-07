"""
This module implement Hierholzer'a algorithm for Eulerian graph traversal
"""

import logging

from igraph import Graph, Edge

from ait.utils import Eulerian, is_eulerian, eulerize
from ait.errors import UnknownState


class Hierholzer:
    """
    Hierholzer algorithm traversing a directed Eulerian graph
    """

    def __init__(self, graph: Graph):
        self._graph: Graph = graph
        self._path = []

    def dfs(self, graph: Graph, current: str, incoming_edge: str = ""):
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
            logging.debug("Visit vertex %s", current)
            while True:
                out_edges = vertex.out_edges()
                if not out_edges:
                    # push the vertex and the incoming edge into the stack when
                    # there is no outgoing edge
                    self._path.append((current, incoming_edge))
                    break

                edge = out_edges[0]
                # move to the adjacent vertex and delete the edge
                adjacent = graph.vs[edge.target].attributes()["name"]
                edge_name = edge.attributes()["name"]
                graph.delete_edges(edge.index)
                self.dfs(graph, adjacent, edge_name)
        except ValueError as exc:
            logging.error("Error %s", exc)
            raise UnknownState from exc

    def travel(self, source: str, self_circle=False) -> list[tuple[str, str]]:
        """
        Traverse a graph using Hierholzer's algorithm.
        If the graph is not a Eulerian graph, add edges to make it eulerian.

        :param source: the start point
        :type source: str
        :param self_circle: include self circuit or not, defaults to False
        :type self_circle: bool, optional
        :return: list of vertex and edge pairs
        :rtype: list[tuple[str, str]]
        """

        graph = self._graph.copy()
        if not self_circle:
            # delete self circle edge
            def self_circuit(edge: Edge) -> bool:
                return edge.source == edge.target

            graph.delete_edges(self_circuit)
        if is_eulerian(graph) == Eulerian.NONE:
            eulerize(graph)

        self._path.clear()
        self.dfs(graph, source)
        return self._path

    def dump_path(self) -> str:
        if not self._path:
            return ""

        result = self._path[-1][0]
        for target, edge in self._path[-2::-1]:
            result += "--" + edge + "->" + target
        return result
