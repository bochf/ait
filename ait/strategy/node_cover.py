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


def _max_subset(
    universal_set: set[int], subsets: list[list[int]]
) -> tuple[int, set[int]]:
    """
    Get the max subset for candidates

    :param universal_set: the whole set
    :type universal_set: set[int]
    :param subsets: list of subsets
    :type subsets: list[list[int]]
    :return: index of the subset and the complement set
    :rtype: tuple[int, set[int]]
    """
    if not universal_set:
        logging.warning("No unvisited vertex")
        return -1, universal_set

    if not subsets:
        logging.warning("No candidate path")
        return -1, universal_set

    index = 0
    missing = universal_set - set(subsets[0])
    for i in range(1, len(subsets)):
        diff = universal_set - set(subsets[i])
        if not diff:
            return i, diff
        if len(missing) > len(diff):
            index = i
            missing = diff
    return index, missing


class CandidatePath:
    def __init__(self, vid: int):
        self._vid = vid
        self._coverage = 0
        self._index = -1
        self._len = 0

    def __len__(self):
        return self._len

    def __gt__(self, other) -> bool:
        if not isinstance(other, CandidatePath):
            raise RuntimeError("Invalid object in comparison %s", other)

        if self.valid and other.valid:
            if self.coverage == other.coverage:
                return len(self) < len(other)
            return self.coverage > other.coverage

        return self.valid

    @property
    def vid(self) -> int:
        return self._vid

    @property
    def coverage(self) -> int:
        return self._coverage

    @property
    def index(self) -> int:
        return self._index

    @property
    def valid(self) -> bool:
        return self._index >= 0

    def build(self, universal_set: set[int], subsets: list[list[int]]):
        total = len(universal_set)
        if total == 0:
            logging.warning("No unvisited vertex")
            return

        if not subsets:
            logging.warning("No candidate path")
            return
        for i in range(len(subsets)):
            covered = len(universal_set.intersection(set(subsets[i])))
            if self._coverage < covered:
                self._index = i
                self._coverage = covered
                self._len = len(subsets[i])
            if covered == total:
                return


class NodeCover(Strategy):
    """
    DFS based directed graph traversal
    Start from a initial state to visit other states in the graph as many as
    posible using Depth-First-Search algorithm. Startover from the initial
    state again if one simple path finished and there are uncovered states.
    """
    def __init__(self, graph_wrapper: GraphWrapper):
        self._graph_wrapper = graph_wrapper
        self._graph = graph_wrapper.graph.copy()
        self._paths: list[list[Arrow]] = []
        self._unvisited_vids = set(range(len(self._graph.vs)))
        # cacheed simple paths for all the vertices
        # key is the vertex id, value is the list of vertex sequence represent
        # list of vertices on the simple path
        self._simple_paths_cache: dict[int, list[list[int]]] = {}

    def _get_simple_paths(self, vid: int) -> list[list[int]]:
        if vid not in self._simple_paths_cache:
            paths = sorted(self._graph.get_all_simple_paths(vid), key=len)
            if not paths:
                logging.debug("can't go to anywhere from the vertex %s", vid)
            self._simple_paths_cache[vid] = paths

        return self._simple_paths_cache[vid]

    def _save_path(self, vertices: list[int]):
        """
        Convert vertex sequence to a list of Arrows and save in self._paths

        :param vertices: vertex sequence of simple path
        :type vertices: list[int]
        """
        if len(vertices) < 2:
            logging.warning("No enough vertices: %s", vertices)
            return

        logging.debug(
            "the longest simple path from %s: %s, unvisited vertices: %s",
            vertices[0],
            vertices,
            self._unvisited_vids,
        )
        self._paths.append([])  # add a new row
        for i in range(len(vertices) - 1):
            source = vertices[i]
            target = vertices[i + 1]
            edges = self._graph.es.select(_between=[[source], [target]])
            if not edges:
                logging.error("No edge from %s to %s", source, target)
                return
            self._paths[-1].append(
                Arrow(
                    self._graph.vs[source].attributes()["name"],
                    self._graph.vs[target].attributes()["name"],
                    edges[0].attributes()["name"],
                )
            )

            if len(edges) > 1:
                # more than 1 connection between the nodes, delete the used
                # one to avoid duplicate path
                self._graph.delete_edges(edges[0].index)

    def _update_path(self, path: list[int]):
        if len(path) < 2:
            logging.warning("invalid path: %s", path)
            return

        self._unvisited_vids -= set(path)
        if not (self._paths and self._paths[-1][-1].head == path[0]):
            # if there is no existing path, or the last vertex of the current
            # path is different than the new path's first vertex, create a new
            # row
            self._paths.append([])
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            edges = self._graph.es.select(_between=[[source], [target]])
            if not edges:
                logging.error("No edge from %s to %s", source, target)
                return
            self._paths[-1].append(
                Arrow(
                    self._graph.vs[source].attributes()["name"],
                    self._graph.vs[target].attributes()["name"],
                    edges[0].attributes()["name"],
                )
            )

            if len(edges) > 1:
                # more than 1 connection between the nodes, delete the used
                # one to avoid duplicate path
                self._graph.delete_edges(edges[0].index)

    def _choose_path(self, start_vid, current_vid) -> list[int]:
        candidate1 = CandidatePath(start_vid)
        candidate2 = CandidatePath(current_vid)
        candidate1.build(self._unvisited_vids, self._get_simple_paths(start_vid))

        if start_vid != current_vid:
            candidate2.build(self._unvisited_vids, self._get_simple_paths(current_vid))

        if not (candidate1.valid or candidate2.valid):
            # neight candicate is valid
            logging.warning(
                "No new path available from vertex %s or vertex %s",
                start_vid,
                current_vid,
            )
            return []

        winner = candidate2
        if candidate1 > candidate2:
            winner = candidate1

        path = self._get_simple_paths(winner.index).pop()
        self._unvisited_vids -= path

    def travel(self, start: Union[str, int]):
        """
        DFS based directed graph traversal.

        :param graph_wrapper: the graph wrapper
        :type graph_wrapper: GraphWrapper
        :param start: the start state
        :type start: Union[str, int]
        """
        start_vid = self._graph.vs[start].index

        # get all simple paths from start vertex
        start_simple_paths = self._get_simple_paths(start_vid)
        # get the longest simple path from the start point
        path = start_simple_paths.pop(-1)
        self._unvisited_vids -= set(path)
        self._save_path(path)

        while self._unvisited_vids and path:
            left = len(self._unvisited_vids)

            end_vid = path[-1]  # the last vertex id of the simple path

            path = self._choose_path(start_vid, end_vid)

            if not path or left == len(self._unvisited_vids):
                logging.warning(
                    "can't reach all the vertices from %s, unvisited: %s",
                    start,
                    self._unvisited_vids,
                )
                return

            self._save_path(path)

    def dump_path(self) -> str:
        if not self._paths:
            return ""

        result = ""
        for path in self._paths:
            if not path:
                continue

            result += dump_path(path) + "\n"
        return result
