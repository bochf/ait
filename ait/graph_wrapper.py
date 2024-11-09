"""
This module defines a finite state machine
"""

import logging
from dataclasses import dataclass

from igraph import Graph, Vertex, Edge

from ait.interface import Transition


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

    def __repr__(self) -> str:
        return self.__str__()

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
        self._graph: Graph = Graph(directed=True)
        # the states name/value pairs of the graph, read from csv file
        self._state_list: dict[str, str] = {}
        # the  events name/value pairs of the graph, read from csv file
        self._event_list: dict[str, str] = {}
        # the transition matrix of source state/event/target state, read from csv file
        self._transition_matrix: dict[str, dict[str, str]] = {}

    @property
    def graph(self) -> Graph:
        """
        Get the graph

        :return: graph
        :rtype: Graph
        """
        return self._graph

    @graph.setter
    def graph(self, value: Graph):
        """
        Set the internal graph object

        :param value: the new value
        :type value: Graph
        """
        self._graph = value

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
        return [edge_to_arrow(edge, self._graph) for edge in self._graph.es]

    def get_node(self, name: str) -> Vertex:
        """
        Get a state by name

        :param name: the name of the state
        :type name: str
        :return: the vertex if found, else None
        :rtype: Vertex
        """
        try:
            vertex = self._graph.vs.find(name)
            return vertex
        except ValueError:
            return None

    def add_node(self, name: str, detail: dict = None):
        """
        Add a state in the graph as a vertex, if a vertex with the same state
        name already exist, do nothing.

        :param name: the name of the node
        :type state: str
        """
        node = self.get_node(name)
        if node:
            value = node.attributes()["detail"]
            if value and value != detail:
                logging.error(
                    "A node with the same name but different value exists."
                    " name=%s, value=%s, new_value=%s",
                    name,
                    value,
                    detail,
                )
            else:
                return

        self._graph.add_vertex(name, detail=detail)
        logging.info("Add new vertex %s: %s", name, detail)

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
            edge_to_arrow(edge, self._graph)
            for edge in edges
            if not arrow.name or edge.attributes()["name"] == arrow.name
        ]

    def add_arc(self, arrow: Arrow, unique: bool = True, **kwargs):
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
        :param kwargs: optional details of an arrow
                       source_detail: the detail of the source state
                       target_detail: the detail of the target state
                       event_detail: the detail of the event
                       transition_result: the result of the transition
        :type kwargs: Any
        """
        if unique:
            # check the uniqueness of the transition
            if self.get_arcs(arrow):
                return

        self.add_node(arrow.tail, kwargs.pop("source_detail", ""))
        self.add_node(arrow.head, kwargs.pop("target_detail", ""))

        self._graph.add_edge(
            arrow.tail,
            arrow.head,
            name=arrow.name,
            detail=kwargs.pop("event_detail", ""),
            output=kwargs.pop("transition_result", {}),
        )
        logging.info("Add new edge %s", arrow)

    def bfs(self, name: str) -> list[str]:
        """
        Conducts a breadth first search (BFS) on the graph.

        :param name: the root vertex name
        :type name: str
        :return: list of vertices' name in order
        :rtype: list[str]
        """
        if not self.get_node(name):
            logging.error("Invalid state %s", name)
            return []

        vids = self._graph.bfs(name)[0]  # vertex ids visited in BFS order
        return [self._graph.vs[vid].attributes()["name"] for vid in vids]

    def update_node_attr(self, data: dict[str, dict[str, any]]):
        """
        Update nodes attributes for visualization

        :param data: the map of node name and attributes
        :type data: dict[str, dict[str, any]]
        """
        vertices = self._graph.vs
        for vertex in vertices:
            vertex_name = vertex.attributes()["name"]
            try:
                attrs = data[vertex_name]
                for key, value in attrs.items():
                    vertices[vertex.index][key] = value
            except KeyError:
                continue

    def update_edge_attr(self, data: dict[str, dict[str, any]]):
        """
        Update edges attributes for visualization

        :param data: the map of edge name and attributes
        :type data: dict[str, dict[str, any]]
        """
        edges = self._graph.es
        for edge in edges:
            edge_name = edge.attributes()["name"]
            try:
                attrs = data[edge_name]
                for key, value in attrs.items():
                    edges[edge.index][key] = value
            except KeyError:
                continue


def is_connected(graph: Graph) -> bool:
    """
    Check all the vertices are connected. If the graph is weak connected
    return true, we don't need bidirection connected.

    :return: true if the graph is connected
    :rtype: bool
    """
    return graph.is_connected(mode="weak")


def edge_to_arrow(edge: Edge, graph: Graph) -> Arrow:
    """
    Convert an edge to an arrow

    :param edge: the edge in a graph
    :type edge: Edge
    :param graph: the graph
    :type graph: Graph
    :return: the arrow with source, target and event name
    :rtype: Arrow
    """
    vertices = graph.vs
    return Arrow(
        vertices[edge.source].attributes()["name"],
        vertices[edge.target].attributes()["name"],
        edge.attributes()["name"],
    )
