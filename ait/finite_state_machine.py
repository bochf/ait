"""
This module defines a finite state machine
"""

import logging
import csv
from collections import namedtuple
from typing import List

import igraph as ig
from igraph import Graph, plot

from ait.base import Event, State


def convert_str_to_int_if_possible(value: str) -> int | str:
    """
    convert a string to an integer if possible

    :param value:
    :return:
    """
    try:
        return int(value)
    except ValueError:
        return value


class FiniteStateMachine:
    """
    Class of finite state machine (FSM)
    ===================================

    A finite state machine is consists of a finite number of states and the transitions among the
    states. Our implementation of the FSM is based on a directed graph, in which each vertex
    represents a state and each directed edge represents an event that triggers state transition.
    """

    def __init__(self, self_circuit=False):
        """initialize the object"""
        self._graph = Graph(directed=True)
        self._self_circuit = self_circuit
        self._matrix = []
        self._actions = []

    def read_csv(self, filename: str) -> None:
        """
        import the state machine matrix from a csv file
        the first line of the csv is "ori_state", "state_detail", event1, event2, ...
        starting from the 2nd row

        -  the 1st column represents the indexes of the states starts from 0

        -  the 2nd column is the explanation of the state

        -  the rest cells are the target state index when an event received at the original state

        look tests/example.csv for example

        :param filename: the csv filename
        """

        # read transitions from a csv file
        fields = []
        with open(filename, "r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            try:
                fields = reader.fieldnames
                self._actions = fields[2:]
            except StopIteration as exc:
                raise ValueError("empty cvs file") from exc

            logging.info("fields: %s", fields)
            for row in reader:
                self._matrix.append(
                    {
                        key: convert_str_to_int_if_possible(value)
                        for key, value in row.items()
                    }
                )
                logging.info("%s", self._matrix[-1])

            if not self._matrix:
                raise ValueError("empty transition")

    def get_state(self, name: str) -> State:
        """
        Get a state by name

        :param name: the name of the state
        :type name: str
        :return: the state object if exists, otherwise None
        :rtype: State
        """
        try:
            vertex = self._graph.vs.find(name)
            return vertex.attributes()["obj"]
        except ValueError:
            return None

    def add_state(self, state: State):
        """
        Add a state in the graph as a vertex, if a vertex with the same state
        name already exist, do nothing.

        :param state: the new state
        :type state: State
        """
        if not self.get_state(state.name):
            self._graph.add_vertex(
                name=state.name, label=state.label, obj=state, size=100
            )

    def get_transitions(
        self, source_name: str = "", target_name: str = "", event_name: str = ""
    ) -> list[ig.Edge]:
        eids = set(range(self._graph.ecount()))  # all the edge ids

        if source_name:
            try:
                vtx = self._graph.vs.find(source_name)
                eids.intersection_update(
                    {edge.index for edge in vtx.incident(mode="out")}
                )
            except ValueError:
                return []
        if target_name:
            try:
                vtx = self._graph.vs.find(target_name)
                eids.intersection_update(
                    {edge.index for edge in vtx.incident(mode="in")}
                )
            except ValueError:
                return []

        result = [self._graph.es[eid] for eid in eids]
        if not event_name:
            return result

        return [edge for edge in result if edge.attributes()["label"] == event_name]

    def add_transition(
        self, source: State, target: State, event: Event, unique: bool = True
    ):
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
        self.add_state(source)
        self.add_state(target)

        if unique:
            # check the uniqueness of the transition
            if self.get_transitions(source.name, target.name, event.name):
                return

        self._graph.add_edge(
            source.name,
            target.name,
            label=event.name,
            obj=event,
        )

    def build_graph(self) -> None:
        """construct graph from the matrix

        :raises ValueError: a ValueError exception will be raised if there are
            invalid transitions in the matrix
        """
        # construct graph from the matrix
        for tran in self._matrix:
            sid = tran["ori_state"]
            self._graph.add_vertex(
                name=f"S{sid:03d}", s_id=sid, label=tran["state_detail"], size=50
            )

        for tran in self._matrix:
            source = f"S{tran['ori_state']:03d}"
            for event in self._actions:
                if tran[event] < 0:
                    # no transition at state on event
                    continue

                target = f"S{tran[event]:03d}"
                if self._self_circuit or source != target:
                    try:
                        # add connection source -> event -> target
                        self._graph.add_edge(source, target, label=event)
                    except ig.InternalError as exc:
                        logging.error(
                            "Fail to transfer from %s to %s with event %s",
                            source,
                            target,
                            event,
                        )
                        raise ValueError(
                            f"invalid transition ({source}, {target}, {event}"
                        ) from exc

    def get_shortest_paths(self, v_from: str, v_to: list = None) -> list[ig.Edge]:
        """
        Calculates the shortest path from a source vertex to a target vertex in a graph.

        :param v_from: the source vertex of the path
        :param v_to: the target vertex of the path, default None indicating to
                     calculate paths to all the vertices
        :return: list of sequences of edges of the shortest path to all the
                 targets, sorted by length
        """
        result = self._graph.get_shortest_paths(v_from, v_to, output="epath")
        return sorted(result, key=len)

    def path_to_str(self, eids: list[int]) -> str:
        if not eids:
            return "NO PATH"

        source_vid = self._graph.es[eids[0]].source
        result = self._graph.vs[source_vid].attributes()["name"]
        for eid in eids:
            edge = self._graph.es[eid]
            target = self._graph.vs[edge.target]
            result += "--" + edge.attributes()["label"]
            result += "->" + target.attributes()["name"]
        return result

    def export_graph(self, filename: str, layout: str) -> None:
        """
        Generate a plotting of the graph data and save in a file using given layout
        :param filename: the file to store the plotting, support svg, png, pdf
        :param layout: the layout algorithm
        """
        plot(self._graph, target=filename, bbox=(0, 0, 1000, 1000), layout=layout)
