"""
Node coverage
Covers all the nodes (states)
"""

import logging
from copy import deepcopy
from typing import Union
from igraph import Graph
from ait.errors import UnknownState
from ait.graph_wrapper import GraphWrapper, Arrow
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
    """
    A data struct stores a path of a vertex
    """

    def __init__(self, coverage: int = -1, path: list[int] = None):
        self._coverage = coverage  # number of unvisited nodes are covered by the path
        self._path = path or []  # the sequence of vertice
        self._length = (
            len(path) if path else -1
        )  # length of the path, -1 if path is None

    def __gt__(self, other) -> bool:
        if not isinstance(other, CandidatePath):
            return True

        if self.valid and other.valid:
            if self._coverage == other._coverage:
                return self._length < other._length
            return self._coverage > other._coverage

        return self.valid

    @property
    def path(self) -> list[int]:
        """
        the path
        """
        return self._path

    @property
    def valid(self) -> bool:
        """
        Check the candidate path is valid or not.
        A valid candidate path should have at least 1 vertex.

        :return: True if the path is valid
        :rtype: bool
        """
        return self._length >= 1


class NodeCover(Strategy):
    """
    DFS based directed graph traversal
    Start from a initial state to visit other states in the graph as many as
    posible using Depth-First-Search algorithm. Startover from the initial
    state again if one simple path finished and there are uncovered states.
    """

    def __init__(self):
        super().__init__()
        self._graph: Graph = None
        self._unvisited_vids: set[int] = set()
        self._current_vid = -1  # the last visited vertex id
        # cacheed simple paths for all the vertices
        # key is the vertex id, value is the list of vertex sequence represent
        # list of vertices on the simple path
        self._simple_paths_cache: dict[int, list[list[int]]] = {}

    def travel(self, state_machine: GraphWrapper, start: Union[str, int]):
        """
        DFS based directed graph traversal.

        :param state_machine: the state machine to visit
        :type state_machine: GraphWrapper
        :param start: the start state
        :type start: Union[str, int]
        """
        self._graph = deepcopy(state_machine.graph)
        self._unvisited_vids = set(range(len(self._graph.vs)))
        if isinstance(start, str):
            vertex = self._graph.vs.find(start)
            if not vertex:
                raise UnknownState(f"The state {start} is not in the state machine.")
            start_vid = vertex.index
        else:
            start_vid = start

        # get all simple paths from start vertex
        start_simple_paths = self._get_simple_paths(start_vid)
        # get the longest simple path from the start point
        path = start_simple_paths[-1]
        self._update_path(path)

        while self._unvisited_vids and path:
            left = len(self._unvisited_vids)

            logging.info("before choose path, unvisited: %s", self._unvisited_vids)
            path = self._choose_path(start_vid)
            logging.info("after choose path, unvisited: %s", self._unvisited_vids)

            if not path or left == len(self._unvisited_vids):
                logging.warning(
                    "Unreachable vertices %s from %s", self._unvisited_vids, start
                )
                return

    def _get_simple_paths(self, vid: int) -> list[list[int]]:
        """
        Get all the simple paths starting from a vertex to all the unvisited vertices.
        The simple path is a path without circuit.

        :param vid: the index of the start vertex
        :type vid: int
        :return: all the simple paths represent in list of sequence of vertice,
                 sorted in length of path
        :rtype: list[list[int]]
        """
        if vid in self._simple_paths_cache:
            return self._simple_paths_cache[vid]

        paths = sorted(
            self._graph.get_all_simple_paths(vid, to=self._unvisited_vids), key=len
        )
        logging.info(
            "get %d simple paths from %d to %s", len(paths), vid, self._unvisited_vids
        )
        if not paths:
            logging.debug("can't go to anywhere from the vertex %s", vid)
        self._simple_paths_cache[vid] = paths
        return paths

    def _update_path(self, path: list[int]):
        """
        Convert the sequence of vertice ids to arrows and store in the paths list

        :param path: a sequence of vertices id
        :type path: list[int]
        """
        if len(path) < 2:
            logging.warning("invalid path: %s", path)
            return

        logging.info("add new path: %s", path)
        self._unvisited_vids -= set(path)
        if self._current_vid != path[0]:
            # if there is no existing path, or the last vertex of the current
            # path is different than the new path's first vertex, create a new
            # row
            self._paths.append([])
        for source, target in zip(path[:-1], path[1:]):
            # go through each step
            edges = self._graph.es.select(_from=source, _to=target)
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

        # set the last visited vertex id to the end of the path
        self._current_vid = path[-1]

    def _choose_path(self, start_vid) -> list[int]:
        """
        Find a shortest path to cover unvisited vertices as many as possible.
        The new path is originated from either start_vid or the last visited
        vertex if available, whichever covers more unvisited vertices. The path
        from the last visited vertex has the prioirty if the coverage is the same.
        """
        logging.info("choosing path between %d and %d", start_vid, self._current_vid)
        candidate1 = self._elect(start_vid)
        candidate2 = CandidatePath()

        if self._current_vid not in [-1, start_vid]:
            self._get_simple_paths(self._current_vid)
            candidate2 = self._elect(self._current_vid)

        if not (candidate1.valid or candidate2.valid):
            # neight candicate is valid
            logging.warning(
                "No new path available from vertex %s or vertex %s",
                start_vid,
                self._current_vid,
            )
            return []

        winner = candidate2
        if candidate1 > candidate2:
            winner = candidate1

        self._update_path(winner.path)
        return winner.path

    @property
    def unvisited_nodes(self) -> set[int]:
        """
        Unvisited nodes

        :return: Unvisited nodes
        :rtype: set[int]
        """
        return self._unvisited_vids

    def _elect(self, vid: int) -> CandidatePath:
        """
        Choose the shortest path that covers most unvisited vertices from the given path list

        :param universal_set: unvisited vertices
        :type universal_set: set[int]
        :param subsets: list of vertices sequences, each vertices sequence represents a path
        :type subsets: list[list[int]]
        :return: the shorest path that covers most unvisited vertices
        :rtype: CandidatePath
        """
        total = len(self._unvisited_vids)
        if total == 0:
            logging.warning("No unvisited vertex")
            return CandidatePath()

        if not self._simple_paths_cache[vid]:
            return CandidatePath()

        # filter out the paths do have any unvisited vertex
        filtered_paths: list[list[int]] = []
        for path in self._simple_paths_cache[vid]:
            if self._unvisited_vids.intersection(set(path)):
                filtered_paths.append(path)
        self._simple_paths_cache[vid] = filtered_paths

        # find the shortest path covers most unvisited vertices
        coverage = -1
        temp_path = []
        for path in filtered_paths:
            covered = len(self._unvisited_vids.intersection(set(path)))
            if coverage < covered:
                coverage = covered
                temp_path = path
                logging.info(
                    "%d unvisited nodes %s are covered by new path %s",
                    coverage,
                    self._unvisited_vids,
                    temp_path,
                )
            if covered == total:
                break
        return CandidatePath(coverage, temp_path)
