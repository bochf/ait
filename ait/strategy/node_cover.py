"""
Node coverage
Covers all the nodes (states)
"""

import logging
from typing import Union

from igraph import Graph

from ait.graph_wrapper import GraphWrapper, Arrow
from ait.utils import dump_path
from ait.strategy.strategy import Strategy


def _max_subset(whole_set: set[int], sub_sets: list[list[int]]) -> tuple[int, set[int]]:
    """
    Get the max subset for candidates

    :param whole_set: the whole set
    :type whole_set: set[int]
    :param sub_sets: list of sub sets
    :type sub_sets: list[list[int]]
    :return: index of the sub set and whole set - sub set
    :rtype: tuple[int, set[int]]
    """
    index = 0
    missing = whole_set - set(sub_sets[0])
    for i in range(1, len(sub_sets)):
        diff = whole_set - set(sub_sets[i])
        if not diff:
            return i, diff
        if len(missing) > len(diff):
            index = i
            missing = diff
    return index, missing


class NodeCover(Strategy):
    """
    DFS based directed graph traversal
    Start from a initial state to visit other states in the graph as many as
    posible using Depth-First-Search algorithm. Startover from the initial
    state again if one simple path finished and there are uncovered states.
    """
    def __init__(self):
        self._paths: list[list[Arrow]] = []

    def _vertices_to_path(self, graph: Graph, vertices: list[int]):
        """
        Convert vertex sequence to a list of Arrows and save in self._paths

        :param graph: the graph
        :type graph: Graph
        :param vertices: vertex sequence of simple path
        :type vertices: list[int]
        """
        if len(vertices) < 2:
            logging.warning("No enough vertices: %s", vertices)
            return

        self._paths.append([])  # add a new row
        for i in range(len(vertices) - 1):
            source = vertices[i]
            target = vertices[i + 1]
            edges = graph.es.select(_between=[[source], [target]])
            if not edges:
                logging.error("No edge from %s to %s", source, target)
                return
            self._paths[-1].append(
                Arrow(
                    graph.vs[source].attributes()["name"],
                    graph.vs[target].attributes()["name"],
                    edges[0].attributes()["name"],
                )
            )

            if len(edges) > 1:
                # more than 1 connection between the nodes, delete the used
                # one to avoid duplicate path
                graph.delete_edges(edges[0].index)

    def travel(self, graph_wrapper: GraphWrapper, start: Union[str, int]):
        """
        DFS based directed graph traversal.

        :param graph_wrapper: the graph wrapper
        :type graph_wrapper: GraphWrapper
        :param start: the start state
        :type start: Union[str, int]
        """
        graph = graph_wrapper.graph.copy()

        # get all simple paths from start vertex
        paths = sorted(graph.get_all_simple_paths(start), key=len)
        if not paths:
            logging.warning("no simple path from the %s to others", start)
            return

        path = paths.pop(-1)
        remaining = set(range(len(graph.vs))) - set(path)
        self._vertices_to_path(graph, path)
        logging.debug(
            "the longest simple path from %s: %s, uncovered vertices: %s",
            start,
            path,
            remaining,
        )
        while remaining and path:
            left = len(remaining)
            index, remaining = _max_subset(remaining, paths)
            if left == len(remaining):
                logging.warning(
                    "can't reach all the vertices from %s, uncovered: %s",
                    start,
                    remaining,
                )
                return

            path = paths.pop(index)
            self._vertices_to_path(graph, path)
            logging.debug(
                "the longest simple path from %s: %s, uncovered vertices: %s",
                start,
                path,
                remaining,
            )

    def dump_path(self) -> str:
        if not self._paths:
            return ""

        result = ""
        for path in self._paths:
            if not path:
                continue

            result += dump_path(path) + "\n"
        return result
