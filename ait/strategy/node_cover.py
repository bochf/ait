"""
Node coverage
Covers all the nodes (states)
"""

import logging

from ait.graph_wrapper import GraphWrapper, Arrow
from ait.strategy.strategy import Strategy


class NodeCover(Strategy):
    def __init__(self):
        self._paths: list[list[Arrow]] = []

    def dfs(self, graph: Graph, source: str):
        visited: set[str] = {str} # visited vertices list
    def travel(self, graph_wrapper: GraphWrapper, start: str):
        """
        depth first search on a graph, start from the initial vertex of the
        graph, visit each vertex at least once

        :param graph_wrapper: the graph
        :type graph_wrapper: GraphWrapper
        :param start: the initial state name of the graph
        :type start: str
        """
        graph = graph_wrapper.graph
        paths = graph.get_all_shortest_paths(start)
        for path in paths:
            logging.info("shortest path from %s: %s", start, path)
