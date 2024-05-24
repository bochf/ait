"""
  This module implements a finite state machine generator.
  Based on a given INIT state and a list of predefined events, the state engine
  applies each event on the INIT state. If the transition creats a new state, 
  the engine will repeatedly apply each event on the new states until all the 
  state/event are executed.
"""

import logging

from ait.interface import State, Transition
from ait.interface import SUT
from ait.errors import UnknownEvent, UnknownState
from ait.graph_wrapper import Arrow, GraphWrapper
from ait.utils import shortest_path


class StateEngine:
    """StateEngine class"""

    def __init__(self, sut: SUT):
        self._matrix = {}
        self._state_graph = GraphWrapper()

        self._sut = sut
        self._env = sut.env.copy()
        self._init_state = sut.state
        self._add_state(self._init_state)

    @property
    def env(self) -> dict[str, any]:
        """
        The key/value pairs of the environment setting to be used to execute
        APIs on the system.


        :return: the environment variables list
        :rtype: dict
        """
        return self._env

    @property
    def matrix(self) -> dict[str, dict[str, State | dict[str, State]]]:
        """
        The matrix of the state machine
        The matrix is a M*N dictionary where M is the number of states, N is
        the number of events.
        Each row represents the results of different events on one source state,
        and each column represents the results of one event on different states.
        The result is a tuple of the target state and the expected output when
        an event happens in a source state.
        The row is indexed by the name of source state, and the column is
        indexed by the name of the event.
        For example

        .. code-block:: python

            martix = {
                'init_state': {
                    "source": state0,
                    "transitions": {
                        "event_name1": (state1, output1),
                        "event_name2": (state2, output2),
                        ...
                    }
                },
                ...
            }

        The 4-tuple of source state, event, target state and output consist a
        transition of the finite state machine.based on the finite, determined
        matrix of transition, we are able to generate test cases for the target
        SUT.
        """

        return self._matrix

    @property
    def state_graph(self) -> GraphWrapper:
        """
        Get state machine

        :return: the directed graph of the states and transitions
        :rtype: GraphWrapper
        """
        return self._state_graph

    def _is_mature_state(self, name: str) -> bool:
        try:
            trans = self.matrix[name]["transitions"]
            return not None in trans.values()
        except KeyError as exc:
            logging.warning("State % does not exist", name)
            raise UnknownState from exc

    def _get_immature_states(self) -> list[str]:
        return [name for name in self._matrix if not self._is_mature_state(name)]

    def _mature(self, name: str = "") -> bool:
        """
        Check a state or the entire matrix is matured.
        A matured state is a state without any undetermined transition.
        A matured matrix is a matrix without any immatured state.

        :param name: the name of the state to check, check the entire matrix if omitted
        :type name: str, optional
        :raises UnknownState: if the state name is not in the matrix
        :return: True if all the transitions are determined
        :rtype: bool
        """
        if name:
            return self._is_mature_state(name)

        for row in self._matrix.values():
            if None in row["transitions"].values():
                return False

        return True

    def _add_state(self, state: State):
        """Add a state and initialize the transitions to None if it is new

        :param new_state: the new state
        :type new_state: State
        """
        if not self._get_state(state.name):
            transitions = {name: None for name in self._sut.event_list}
            self._matrix[state.name] = {
                "source": state,
                "transitions": transitions,
            }
            logging.info("Add new state: %s", state)

            self._state_graph.add_node(state.name)

    def _get_state(self, state_name: str) -> State:
        """Get a state by name

        :param state_name: name of the state
        :type state_name: str
        :return: the state object if found in the state list, otherwise None
        :rtype: State
        """
        try:
            return self._matrix[state_name]["source"]
        except KeyError:
            return None

    def _set_transition(self, transition: Transition):
        """
        Set the transition from source state to target state on the event

        :param transition: the transition from source to target state and the event
        :type transition: Transition
        :raises RuntimeError: if the same event on the same source state gets different target state
        :raises UnknownEvent: if the given event is not in the list
        """
        self._add_state(transition.source)
        self._add_state(transition.target)

        source_name = transition.source.name
        event_name = transition.event.name
        trans = self._matrix[source_name]["transitions"]
        try:
            exist_result = trans[event_name]
            if not exist_result:
                trans[event_name] = (transition.target, transition.output)
                if transition.is_valid:
                    # add the transition into the state graph if both states are real
                    self._state_graph.add_arc(transition.arrow)
                logging.info("Add new transition %s", transition)
                return
            if exist_result[0] != transition.target:
                logging.error(
                    "ambiguate behavior, get different result %s vs %s when processing %s on %s",
                    exist_result.name,
                    transition.target.name,
                    event_name,
                    source_name,
                )
                raise RuntimeError(
                    f"ambiguate behavior: {event_name} on {source_name}"
                    f", target state {exist_result} vs {transition.target}"
                )
        except KeyError as exc:
            raise UnknownEvent(f"Invalid event {event_name}") from exc

    def _explore(self, current_state: State) -> State:
        """
        Explore possible transitions on a state by applying all the events on it.
        If any event triggers the target system state change, the function will
        recursively exploring the new state until get a mature state.
        The returned state might be the same as the original state if all the
        events are exercised or there is a circuit.

        :param current_state: the current state
        :type current_state: State
        :raises UnknownEvent: if the event in the event list of the matrix but
                              not in the state's dictionary
        :raises UnknownEvent: if the event is not in the matrix
        :return: a mature state where all the events are exercised.
        :rtype: State
        """
        if not isinstance(current_state, State):
            logging.warning("Wrong object %s", current_state)
            raise UnknownEvent

        if current_state.name not in self._matrix:
            logging.error("State %s does not exist", current_state.name)
            raise UnknownEvent(f"Invalid state {current_state.name}")

        if self._is_mature_state(current_state.name):
            return current_state

        for event in self._sut.event_list.values():
            try:
                if self._matrix[current_state.name]["transitions"][event.name]:
                    # the event on current state has been exercised, skip it
                    continue

                output = event.fire(self._sut, self._env)
                target_state = self._sut.state
                self._set_transition(
                    Transition(current_state, target_state, event, output)
                )
                if current_state != target_state:
                    # the target system goes to a new state by the event
                    # explore the transitions on the next state
                    logging.debug(
                        "State changed to %s when running %s on %s",
                        target_state.name,
                        event.name,
                        current_state.name,
                    )
                    return self._explore(target_state)
            except KeyError as exc:
                raise UnknownEvent(f"Invalid event {event.name}") from exc

        return current_state

    def evolve(self, state: State):
        """Build the state machine from a state

        :param current_state: the current state of the system
        :type current_state: State
        """
        current_state = state  # the state to start exploring

        generation = 0
        while not self._mature():
            # select a state to explore
            # if the current state is immature, explore the current state
            # otherwise find a immature state that needs least step to reach
            # then follow the path to get to the selected state and start
            # exploring
            logging.info(
                "Evolve the state machine iteration %d, from %s",
                generation,
                current_state,
            )
            source = self._go_to_nearest_immature_state(current_state.name)
            current_state = self._explore(self._get_state(source))
            generation += 1
            if generation > 100:
                logging.warning(
                    "The state machine is too complicated or something wrong."
                )

    def _go_to_nearest_immature_state(self, source: str) -> str:
        if not self._is_mature_state(source):
            return source

        path1 = list(
            range(len(self._matrix))
        )  # from source to the nearest immature state
        path2 = path1.copy()  # from initial state to the nearest immature state

        target = self._find_nearest_immature_state(source)
        if target:
            path1 = shortest_path(self._state_graph.graph, source, target)
        if source != self._init_state.name:
            # try start from initial state
            if not self._is_mature_state(self._init_state.name):
                self._sut.reset()
                return self._init_state.name

            target = self._find_nearest_immature_state(self._init_state.name)
            # there must be an immature state reachable from the initial state
            path2 = shortest_path(
                self._state_graph.graph, self._init_state.name, target
            )

        if len(path1) <= len(path2):
            # go from current state
            return self._execute_path(path1)

        self._sut.reset()  # go to initial state first
        return self._execute_path(path2)

    def _execute_path(self, path: list[Arrow]) -> str:
        if not path:
            return ""

        for arrow in path:
            try:
                event = self._sut.event_list[arrow.name]
                event.fire(self._sut, self._env)
            except IndexError as exc:
                logging.error("Unknow event %s on %s", arrow.name, arrow.tail)
                raise UnknownState from exc
            except AttributeError as exc:
                logging.error("Failed to execute path: %s, error=%s", path, exc)
                self._print_matrix()
                raise exc
        return path[-1].head

    def _find_nearest_immature_state(self, source: str) -> str:
        """
        Find the nearest immature state to a state.
        The closest state means a state that requires the minimal steps from
        the current state. This is to start testing the unvisited path in the
        least cost.

        :return: the nearest immature state from the source
                 empty if no immature state is reachable form the source
        :rtype: State
        """
        for name in self._state_graph.bfs(source):
            if not self._is_mature_state(name):
                return name

        return ""

    def _print_matrix(self):
        """dump the matrix for debugging purpose"""
        for source_name, transitions in self._matrix.items():
            for event_name, result in transitions["transitions"].items():
                if result:
                    target_name = result[0].name
                    logging.debug(
                        "%s -- %s -> %s", source_name, event_name, target_name
                    )
