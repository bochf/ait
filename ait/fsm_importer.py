"""
Import data into a finit state machine
"""

from csv import DictReader

from ait.graph_wrapper import GraphWrapper, Arrow


class FsmImporter:
    """
    Create a finit state machine
    """

    def __init__(self):
        # the states name/value pairs of the graph, read from csv file
        self._state_list: dict[str, str] = {}
        # the  events name/value pairs of the graph, read from csv file
        self._event_list: dict[str, str] = {}
        # the transition matrix of source state/event/target state, read from csv file
        self._state_transitions: dict[str, dict[str, str]] = {}
        # the matrix of the transition result, map of (source state, event) to result
        self._transition_results: dict[str, dict[str, str]] = {}

    def from_csv(
        self,
        state_transitions: str,
        states: str = None,
        events: str = None,
        transition_results: str = None,
    ) -> GraphWrapper:
        """
        Load the state machine from CSV files.

        The state transition file is required. The first line of the state_transitions
        is the header line that starts with `S_source` followed by event names
        with the prefix `E_`. The first column of the state_transitions is the state names.
        The rest of the data is the target state name when an event happens
        at the source state.

        .. csv-table::
            :file: ../tests/data/example_transitions.csv
            :header-rows: 1

        The states and events are optional, which describe the details of the states
        and events. The format of the states and events are as follows:

        `The first column is the name of the state or event`

        `The second column is the detail of the state or event`

        .. csv-table::
            :file: ../tests/data/example_states.csv
            :header-rows: 1

        The name of the states and events must be consistent with the transition matrix.

        The transition result is optional. It has the similar format as the transition
        matrix.

        .. csv-table::
            :file: ../tests/data/example_output.csv
            :header-rows: 1

        :param state_transitions: the file name of the transition matrix
        :type state_transitions: str
        :param states: the file name of the states detail
        :type states: str, optional
        :param events: the file name of the events detail
        :type events: str, optional
        :return: the state machine
        :rtype: GraphWrapper
        """
        state_transitions = self._populate_state_transition(state_transitions)
        state_list = self._populate_details(states)
        event_list = self._populate_details(events)
        transition_results = self._populate_transition_results(transition_results)

        # Build the graph object form the transition matrix
        return self.from_dicts(
            state_transitions,
            state_list,
            event_list,
            transition_results,
        )

    def from_dicts(
        self,
        state_transitions: dict[str, dict[str, str]],
        state_list: dict[str, str] = None,
        event_list: dict[str, str] = None,
        transition_results: dict[str, dict[str, str]] = None,
    ) -> GraphWrapper:
        """
        Load the state machine from dictionaries

        :param state_transitions: the state transition data, a map of source
                                  state to a map of event to target state. For
                                  example:

        .. code-block:: python

            {
                "A": {"0": "B", "1": "C"},
                "B": {"2": "D"},
                "C": {"3": "D"},
                "D": {"4": "E", "5": "F"},
                "E": {"6": "G"},
                "F": {"7": "G"},
            }

        :type state_transitions: dict[str, dict[str, str]]
        :param state_list: the description of the states, a map of state name
                           and value, defaults to None
        :type state_list: dict[str, str], optional
        :param event_list: the description of the events, a map of event name
                           and value, defaults to None
        :type event_list: dict[str, str], optional
        :param transition_results: the transition result data, a map of source
                                state to a map of event to transition output,
                                defaults to None
        :type transition_results: dict[str, dict[str, str]], optional
        :return: the state machine
        :rtype: GraphWrapper
        """
        fsm = GraphWrapper()
        for source, transitions in state_transitions.items():
            results = transition_results.get(source, {}) if transition_results else {}
            for event, target in transitions.items():
                fsm.add_arc(
                    Arrow(source, target, event),
                    source_detail=state_list.get(source, "") if state_list else "",
                    target_detail=state_list.get(target, "") if state_list else "",
                    event_detail=event_list.get(event, "") if event_list else "",
                    transition_result=results.get(event, {}),
                )
        return fsm

    def _populate_state_transition(self, filename: str) -> dict[str, dict[str, str]]:
        if not isinstance(filename, str):
            raise ValueError(f"invalid argument filename: {filename}")

        result: dict[str, dict[str, str]] = {}

        with open(filename, "r", encoding="utf-8", newline="") as csv:
            reader = DictReader(csv)
            for row in reader:
                source = row.pop("S_source")
                if source in result:
                    # duplicate source state
                    raise ValueError(f"duplicated source event {source}")

                result[source] = {}
                for key, value in row.items():
                    event_name = key[2:]
                    if value:
                        result[source][event_name] = value

        return result

    def _populate_details(self, filename: str) -> dict[str, str]:
        if not filename:
            return {}

        if not isinstance(filename, str):
            raise ValueError(f"invalid argument filename: {filename}")

        result = {}
        with open(filename, "r", encoding="utf-8", newline="") as csv:
            # the file has 2 columns, name and value
            reader = DictReader(csv)
            for row in reader:
                assert len(row) == 2
                result[row["Name"]] = row["Detail"]

        return result

    def _populate_transition_results(self, filename: str) -> dict[str, dict[str, str]]:
        """
        The first column of the transition result is the state names.
        The rest of the data is the output when an event happens at source state.
        """
        if not filename:
            return {}

        if not isinstance(filename, str):
            raise ValueError(f"invalid argument filename: {filename}")

        result: dict[str, dict[str, str]] = {}
        with open(filename, "r", encoding="utf-8", newline="") as csv:
            reader = DictReader(csv)
            for row in reader:
                source = row.pop("S_source")
                result[source] = {}
                for edge, output in row.items():
                    event_name = edge[2:]
                    result[source][event_name] = output

        return result
