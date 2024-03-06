import collections
import logging

from igraph import Graph, Edge

from ait.utils import Arrow, Eulerian, is_eulerian, eulerize
from ait.errors import UnknownState


class Hierholzer:

    def __init__(self, graph: Graph):
        self._matrix = []
        self._graph: Graph = graph.copy()
        self._track = []

    def dfs(self, graph: Graph, current: str, incoming_edge: str = ""):
        try:
            vertex = graph.vs.find(current)
            logging.debug("Visit vertex %s", current)
            while True:
                out_edges = vertex.out_edges()
                if not out_edges:
                    # push the vertex and the incoming edge into the stack when
                    # there is no outgoing edge
                    self._track.append((current, incoming_edge))
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

    def travel(self, source: str, self_circle=False):
        graph = self._graph.copy()
        if not self_circle:
            # delete self circle edge
            self_circuit = lambda edge: edge.source == edge.target
            graph.delete_edges(self_circuit)
        if is_eulerian(graph) == Eulerian.NONE:
            eulerize(graph)

        self._track.clear()
        self.dfs(graph, source)
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
