"""
This module defines a finite state machine
"""

from dataclasses import dataclass
import logging
from csv import DictWriter, DictReader

from igraph import Graph, Edge, plot


@dataclass
class Arrow:
    """
    An arrow is a directed edge in the directed graph with an ordered pair of
    vertices and an arc connects them. The arrow's direction is from tail to
    head.
    """

    tail: str
    head: str
    name: str

    def __str__(self) -> str:
        return f"{self.tail}--{self.name}->{self.head}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Arrow):
            return False
        return (
            self.tail == other.tail
            and self.head == other.head
            and self.name == other.name
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Arrow):
            raise ValueError(f"Compare Arrow to {other.__class__}")
        if self.tail < other.tail:
            return True
        if self.tail > other.tail:
            return False

        # equal tail, compare head
        if self.head < other.head:
            return True
        if self.head > other.head:
            return False

        # equal tail and head, compare name
        if self.name < other.name:
            return True
        return False

    @property
    def end_points(self) -> list[str]:
        """return tail/head pair"""
        return [self.tail, self.head]


class GraphWrapper:
    """
    A wrapper class of igraph.Graph
    Implements and overrides some helper functions for accessing a directed
    graph by name.
    """

    def __init__(self):
        """constructor"""
        self._graph = Graph(directed=True)

    def _edge_to_arrow(self, edge: Edge) -> Arrow:
        vs = self._graph.vs
        return Arrow(
            vs[edge.source].attributes()["name"],
            vs[edge.target].attributes()["name"],
            edge.attributes()["name"],
        )

    @property
    def graph(self) -> Graph:
        """
        Get the graph

        :return: graph
        :rtype: Graph
        """
        return self._graph

    @property
    def nodes(self) -> list[str]:
        """
        Get all the vertices in the graph

        :return: list of vertices name
        :rtype: list[str]
        """
        return [vertex.attributes()["name"] for vertex in self._graph.vs]

    @property
    def arcs(self) -> list[Arrow]:
        """
        Get all the arrows in the graph

        :return: list of arrows
        :rtype: list[Arrow]
        """
        return [self._edge_to_arrow(edge) for edge in self._graph.es]

    def has_node(self, name: str) -> bool:
        """
        Get a state by name

        :param name: the name of the state
        :type name: str
        :return: true if exists, otherwise false
        :rtype: bool
        """
        try:
            self._graph.vs.find(name)
            return True
        except ValueError:
            return False

    def add_node(self, name: str):
        """
        Add a state in the graph as a vertex, if a vertex with the same state
        name already exist, do nothing.

        :param name: the name of the node
        :type state: str
        """
        if self.has_node(name):
            logging.warning("Skip duplicated vertex %s", name)
            return

        self._graph.add_vertex(name)
        logging.info("Add new vertex %s", name)

    def get_arcs(self, arrow: Arrow) -> list[Arrow]:
        """
        Get all edges start from the source to the target with the event name.
        If source is empty, the edges can start from any state
        If target is empty, the edges can end on any state
        If the event is empty, the edges can have any name

        :param source: the name of the source state
        :type source: str, optional
        :param target: the name of the target state
        :type target: str, optional
        :param event: the name of the event
        :type event: str, optional
        :return: list of arrows
        :rtype: list[Arrow]
        """
        eids = set(range(self._graph.ecount()))  # all the edge ids

        if arrow.tail:
            # filter by all the outgoing edges from the source
            try:
                vtx = self._graph.vs.find(name=arrow.tail)
                eids.intersection_update(
                    {edge.index for edge in vtx.incident(mode="out")}
                )
            except ValueError:
                return []
        if arrow.head:
            # filter by all the incoming edges to the target
            try:
                vtx = self._graph.vs.find(arrow.head)
                eids.intersection_update(
                    {edge.index for edge in vtx.incident(mode="in")}
                )
            except ValueError:
                return []

        edges = [self._graph.es[eid] for eid in eids]
        # filter by event name
        return [
            self._edge_to_arrow(edge)
            for edge in edges
            if not arrow.name or edge.attributes()["name"] == arrow.name
        ]

    def add_arc(self, arrow: Arrow, unique: bool = True):
        """
        Add a transition from source state to target state when event happens.
        The source and target state are stored in the graph as vertices and the
        event is a directed edge from the source to the target.

        :param transition: the tuple of a source state, a target state and the
            event triggers the transition.
        :type transition: Transition
        :param unique: keep the transition unique, defaults to True. if there
            is a transition with the same source/target/event, do nothing.
        :type unique: bool, optional
        """
        if unique:
            # check the uniqueness of the transition
            if self.get_arcs(arrow):
                return

        self.add_node(arrow.tail)
        self.add_node(arrow.head)

        self._graph.add_edge(arrow.tail, arrow.head, name=arrow.name)
        logging.info("Add new edge %s", arrow)

    def bfs(self, name: str) -> list[str]:
        """
        Conducts a breadth first search (BFS) on the graph.

        :param name: the root vertex name
        :type name: str
        :return: list of vertices' name in order
        :rtype: list[str]
        """
        if not self.has_node(name):
            logging.error("Invalid state %s", name)
            return []

        vids = self._graph.bfs(name)[0]  # vertex ids visited in BFS order
        return [self._graph.vs[vid].attributes()["name"] for vid in vids]

    def load_from_dict(self, data: dict[str, dict[str, dict]]):
        """
        Constructs a graph from a dict-of-dicts representation.

        Each key is a string and represent a vertex. Each value is a dict
        representing outgoing edges from that vertex. Each dict key is a
        string for a target vertex, such that an edge will be created between
        those two vertices. Strings are interpreted as vertex names. Each
        value is a dictionary of edge attributes for that edge.

        :param data: map of vertex name and the edges
        :type data: dict[str, dict[str, dict]]

        .. code-block::

            {
                'Alice':
                {
                    'Bob': {'weight': 1.5},
                    'David': {'weight': 2}
                }
            }

        """
        self._graph = Graph.DictDict(data, directed=True)

    def export_to_dict(self) -> dict[str, dict[str, dict]]:
        """
        Export the graph to a dict-of-dict data structure

        :return: _description_
        :rtype: dict[str, dict[str, dict]]
        """
        data = self._graph.to_dict_dict(use_vids=False, edge_attrs="name")
        return data

    def write_to_csv(self, filename):
        """
        Save the matrix to a csv file

        :param filename: the csv filename
        :type filename: str
        """
        with open(filename, "w", encoding="utf-8", newline="") as csvfile:
            edge_names = set(
                "E_" + str(edge.attributes()["name"]) for edge in self._graph.es
            )
            fields = ["S_source"] + list(edge_names)
            writer = DictWriter(csvfile, fieldnames=fields)

            writer.writeheader()
            for vertex in self._graph.vs:
                row = {"S_source": vertex.attributes()["name"]}
                for edge in vertex.out_edges():  # add defined transitions
                    key = "E_" + str(edge.attributes()["name"])
                    value = self._graph.vs[edge.target].attributes()["name"]
                    row[key] = value
                for key in edge_names:  # add invalid transitions
                    if key not in row:
                        row[key] = ""
                writer.writerow(row)

    def read_from_csv(self, filename):
        """
        Load the data from a csv file.
        The first line of the csv file is a string list stars with "S_source"
        followed by event names with prefix "E_".
        The first column of the csv file is the state names.
        The rest of the data is the target state name when an event happens
        at source state.

        :param filename: the csv filename
        :type filename: str
        """
        with open(filename, "r", encoding="utf-8", newline="") as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                source = row.pop("S_source")
                for edge, target in row.items():
                    if target:
                        self.add_arc(Arrow(source, target, edge[2:]))

    def update_node_attr(self, data: dict[str, dict[str, any]]):
        """
        Update nodes attributes for visualization

        :param data: the map of node name and attributes
        :type data: dict[str, dict[str, any]]
        """
        vs = self._graph.vs
        for vertex in vs:
            vertex_name = vertex.attributes()["name"]
            try:
                attrs = data[vertex_name]
                for key, value in attrs.items():
                    vs[vertex.index][key] = value
            except KeyError:
                continue

    def update_edge_attr(self, data: dict[str, dict[str, any]]):
        """
        Update edges attributes for visualization

        :param data: the map of edge name and attributes
        :type data: dict[str, dict[str, any]]
        """
        es = self._graph.es
        for edge in es:
            edge_name = edge.attributes()["name"]
            try:
                attrs = data[edge_name]
                for key, value in attrs.items():
                    es[edge.index][key] = value
            except KeyError:
                continue

    def export_graph(self, filename: str, show_self_circle: bool = True, **kwargs):
        """
        Generate a plotting of the graph data and save in a file


        :param filename: the output file name, support svg, pdf
        :type filename: str
        :param show_self_circle: show self circle in the graph or not, defaults to True
        :type show_self_circle: bool, optional
        """
        if show_self_circle:
            plot(self._graph, target=filename, **kwargs)
        else:
            g = self._graph.copy()
            g.delete_edges([edge.index for edge in g.es if edge.source == edge.target])
            plot(g, target=filename, **kwargs)


def is_connected(graph: Graph) -> bool:
    """
    Check all the vertices are connected. If the graph is weak connected
    return true, we don't need bidirection connected.

    :return: true if the graph is connected
    :rtype: bool
    """
    return graph.is_connected(mode="weak")
