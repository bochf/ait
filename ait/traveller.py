import collections
import logging

from igraph import Graph

from ait.utils import Arrow, Eulerian, is_eulerian, eulerize
from ait.errors import UnknownState


class Hierholzer:

    def __init__(self, graph: Graph):
        self._matrix = []
        self._graph: Graph = graph.copy()
        self._track = []

    def dfs(self, current: str):
        try:
            logging.debug("Visit vertex %s", current)
            vertex = self._graph.vs.find(current)
            out_edges = vertex.out_edges()
            while out_edges:
                edge = out_edges[0]
                # move to the adjacent vertex and delete the edge
                adjacent = self._graph.vs[edge.target].attributes()["name"]
                arrow = Arrow(current, adjacent, edge.attributes()["name"])
                logging.debug("Visit edge %s", arrow)
                self._track.append(arrow)
                self._graph.delete_edges(edge.index)
                self.dfs(adjacent)
                out_edges = vertex.out_edges()
        except ValueError as exc:
            logging.error("Error %s", exc)
            raise UnknownState from exc

    def travel(self, source: str):
        if is_eulerian(self._graph) == Eulerian.NONE:
            eulerize(self._graph)

        self._track.clear()
        self.dfs(source)
        return self._track

    def find_itinerary(self):
        def dfs(cur, graph, res):
            while graph[cur]:  # traversal all edges
                dfs(graph[cur].pop(), graph, res)  # visit and delete
            if not graph[cur]:  # push the vertex into the stack
                res.append(cur)

        # build the graph
        my_graph = collections.defaultdict(list)
        for start, end in sorted(self._matrix)[::-1]:
            my_graph[start].append(end)
        my_res = []
        dfs(self._matrix[0][0], my_graph, my_res)

        return my_res[::-1]  # reverse order
