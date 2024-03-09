"""
This module defines a finite state machine
"""

import logging
from csv import DictWriter, DictReader

import igraph as ig
from igraph import Graph, plot

from ait.base import Arrow

class FiniteStateMachine:
    """
    Class of finite state machine (FSM)
    ===================================

    A finite state machine is consists of a finite number of states and the transitions among the
    states. Our implementation of the FSM is based on a directed graph, in which each vertex
    represents a state and each directed edge represents an event that triggers state transition.
    """

    def __init__(self):
        """constructor"""
        self._graph = Graph(directed=True)

    def _edge_to_arrow(self, edge: ig.Edge) -> Arrow:
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
        Get all the vertices in the fsm

        :return: list of vertices name
        :rtype: list[str]
        """
        return [vertex.attributes()["name"] for vertex in self._graph.vs]

    @property
    def arcs(self) -> list[Arrow]:
        """
        Get all the arrows in the fsm

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

    def get_arcs(
        self, source: str = "", target: str = "", event: str = ""
    ) -> list[Arrow]:
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

        if source:
            # filter by all the outgoing edges from the source
            try:
                vtx = self._graph.vs.find(name=source)
                eids.intersection_update(
                    {edge.index for edge in vtx.incident(mode="out")}
                )
            except ValueError:
                return []
        if target:
            # filter by all the incoming edges to the target
            try:
                vtx = self._graph.vs.find(target)
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
            if not event or edge.attributes()["name"] == event
        ]

    def add_arc(self, source: str, target: str, event: str, unique: bool = True):
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
            if self.get_arcs(source, target, event):
                return

        self.add_node(source)
        self.add_node(target)

        self._graph.add_edge(source, target, name=event)
        logging.info("Add new edge %s--%s->%s", source, event, target)

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

    def write_to_csv(self, filename="fsm.csv"):
        """
        Save the matrix to a csv file

        :param filename: the csv filename
        :type filename: str, optional
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

    def read_from_csv(self, filename="fsm.csv"):
        """
        Load the data from a csv file.
        The first line of the csv file is a string list stars with "S_source"
        followed by event names with prefix "E_".
        The first column of the csv file is the state names.
        The rest of the data is the target state name when an event happens
        at source state.

        :param filename: the csv filename
        :type filename: str, optional
        """
        with open(filename, "r", encoding="utf-8", newline="") as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                source = row.pop("S_source")
                for edge, target in row.items():
                    if target:
                        self.add_arc(source, target, edge[2:])

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

    def export_graph(
        self,
        filename: str = None,
        bbox: tuple = (0, 0, 1000, 1000),
        show_self_circle: bool = True,
        **kwargs,
    ) -> None:
        """
        Generate a plotting of the graph data and save in a file using given layout
        :param filename: the file to store the plotting, support svg, png, pdf
        :param layout: the layout algorithm
        """
        if show_self_circle:
            plot(self._graph, target=filename, bbox=bbox, **kwargs)
        else:
            g = self._graph.copy()
            g.delete_edges([edge.index for edge in g.es if edge.source == edge.target])
            plot(g, target=filename, bbox=bbox, **kwargs)
