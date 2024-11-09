"""
Export the finit state machine data
"""

from csv import DictWriter
from igraph import plot

from ait.graph_wrapper import GraphWrapper


class FsmExporter:
    """
    Export data from the finit state machine
    """

    def __init__(self, state_machine: GraphWrapper):
        self._state_machine = state_machine

    def to_csv(self, filename: str, detail: bool = False) -> None:
        """
        Export state machine to csv files

        :param filename: the filename of the state transition matrix csv file,
                         the filename is in format <prefix>.csv,
                         the prefix will be used to store details of the state
                         machine if the argument detail is True.
                         states detail is saved in <prefix>_states.csv
                         events detail is saved in <prefix>_events.csv
                         transition output is saved in <prefix>_output.csv
        :type filename: str
        :param detail: export states, events and transitions output, defaults to False
        :type detail: bool, optional
        """
        state_transitions, state_list, event_list, transition_output = self.to_dict()
        self._write_transition_matrix_to_csv(filename, state_transitions)
        if detail:
            prefix = filename.removesuffix(".csv")
            self._write_detail_to_csv(prefix + "_states.csv", state_list)
            self._write_detail_to_csv(prefix + "_events.csv", event_list)
            self._write_transition_matrix_to_csv(
                prefix + "_output.csv", transition_output
            )

    def to_dict(
        self,
    ) -> tuple[
        dict[str, dict[str, str]],
        dict[str, dict],
        dict[str, dict],
        dict[str, dict[str, dict]],
    ]:
        """
        Export state machine to dictionaries

        :return: state transition matrix, states detail, events detail, transition output
        :rtype: tuple[
            dict[str, dict[str, str]],
            dict[str, dict],
            dict[str, dict],
            dict[str, dict[str, dict]]]
        """
        state_transitions: dict[str, dict[str, str]] = {}
        state_list: dict[str, dict] = {}
        event_list: dict[str, dict] = {}
        transition_output: dict[str, dict[str, dict]] = {}

        vs_list = self._state_machine.graph.vs
        es_list = self._state_machine.graph.es
        for vertex in vs_list:
            name = vertex.attributes()["name"]
            value = vertex.attributes().get("detail", "")
            state_list[name] = value
            if vertex.outdegree() > 0:
                state_transitions[name] = {}
                transition_output[name] = {}

        for edge in es_list:
            name = edge.attributes()["name"]
            value = edge.attributes().get("detail", "")
            output = edge.attributes().get("output", {})
            event_list[name] = value

            source = vs_list[edge.source].attributes()["name"]
            target = vs_list[edge.target].attributes()["name"]
            state_transitions[source][name] = target
            transition_output[source][name] = output

        return state_transitions, state_list, event_list, transition_output

    def to_svg(self, filename: str, show_self_circle: bool = True, **kwargs) -> None:
        """
        Generate a plotting of the graph data and save in a file

        :param filename: the output file name, support svg, pdf
        :type filename: str
        :param show_self_circle: show self circle in the graph or not, defaults to True
        :type show_self_circle: bool, optional
        :param kwargs: other parameters for the plot function
        :type kwargs: dict
        """
        graph = self._state_machine.graph.copy()
        if "vertex_label" not in kwargs:
            # if vetex_label is not specified
            kwargs["vertex_label"] = []
            for vtx in graph.vs:
                attr = vtx.attributes()
                # use the vertex's label or name as label
                kwargs["vertex_label"].append(attr.get("label", attr.get("name", "")))
        if "vertex_size" not in kwargs:
            # if vertex_size is not specified
            # set the size of the vertex based on the label
            max_size = 100
            min_size = 50
            kwargs["vertex_size"] = []
            for label in kwargs["vertex_label"]:
                actual_size = 10 * len(label)
                kwargs["vertex_size"].append(max(min_size, min(max_size, actual_size)))
        if "edge_label" not in kwargs:
            # if edge_label is not specified
            kwargs["edge_label"] = []
            self_circles = dict()
            edge_index = 0
            for edge in graph.es:
                attr = edge.attributes()
                label = attr.get("label", attr.get("name", ""))
                key = (edge.source, edge.target)
                # if the edge is a self loop, merge the lable
                if key[0] == key[1]:
                    if not show_self_circle:
                        continue
                    if key in self_circles:
                        # get the index of the edge first appears
                        first_edge = self_circles[key]
                        # append new lable to the first edge
                        kwargs["edge_label"][first_edge] += "/" + label
                        label = ""  # empty label for subsequent edges
                    else:
                        self_circles[key] = edge_index

                kwargs["edge_label"].append(label)
                edge_index += 1

            for edge_index in self_circles.values():
                # add "\n" at the end of the edge label to avoid overlapping with vertex
                kwargs["edge_label"][edge_index] += "\n" * 10

        if show_self_circle:
            plot(graph, target=filename, autocurve=True, **kwargs)
        else:
            graph.delete_edges(
                [edge.index for edge in graph.es if edge.source == edge.target]
            )
            plot(graph, target=filename, **kwargs)

    def _write_transition_matrix_to_csv(
        self, filename: str, matrix: dict[str, dict[str, str]]
    ) -> None:
        event_names = set()
        for edges in matrix.values():
            for event in edges.keys():
                event_names.add("E_" + event)

        fields = ["S_source"] + list(event_names)
        with open(filename, "w", encoding="utf-8", newline="") as csv:
            writer = DictWriter(csv, fieldnames=fields)
            writer.writeheader()
            for source, edges in matrix.items():
                row = {"S_source": source}
                for event, target in edges.items():  # add defined transitions
                    row["E_" + event] = target
                for key in event_names:  # add invalid transitions
                    if key not in row:
                        row[key] = ""
                writer.writerow(row)

    def _write_detail_to_csv(self, filename: str, detail: dict[str, str]) -> None:
        with open(filename, "w", encoding="utf-8", newline="") as csv:
            writer = DictWriter(csv, ["Name", "Detail"])
            writer.writeheader()

            for key, value in detail.items():
                writer.writerow(
                    {
                        "Name": key,
                        "Detail": value,
                    }
                )
