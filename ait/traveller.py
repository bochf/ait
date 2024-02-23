from typing import List
import collections


class Hierholzer:
    def __init__(self, matrix: List[List[str]]):
        self._matrix = matrix

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
