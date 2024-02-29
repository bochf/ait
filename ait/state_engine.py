"""
  This module implements a finite state machine generator.
  Based on a given INIT state and a list of predefined events, the state engine
  applies each event on the INIT state. If the transition creats a new state, 
  the engine will repeatedly apply each event on the new states until all the 
  state/event are executed.
"""

import logging

from ait.base import State, SUT, InvalidState, Transition
from ait.errors import UnknownEvent, UnknownState
from ait.finite_state_machine import FiniteStateMachine, Arrow

INVALID_STATE = InvalidState()


class StateEngine:
    """StateEngine class"""

    def __init__(self, sut: SUT):
        self._matrix = {}
        self._fsm = FiniteStateMachine()

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
        The matrix is a dictionary where the keys are state names and the
        values are dictionaries containing event names and their corresponding
        target states. For example

        .. code-block:: python

            martix = {
                'init_state': {
                    "source": state0,
                    "transitions": {
                        "event_name1": state1,
                        "event_name2": state2,
                        ...
                    }
                },
                ...
            }

        """

        return self._matrix

    def _is_mature_state(self, name: str) -> bool:
        try:
            trans = self.matrix[name]["transitions"]
            return not None in trans.values()
        except KeyError as exc:
            logging.warning("State % does not exist", name)
            raise UnknownState from exc

    def _get_immature_states(self) -> list[str]:
        return [name for name in self._matrix if not self._is_mature_state(name)]

    def mature(self, name: str = "") -> bool:
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
        if not state.is_valid:
            return

        if not self.get_state(state.name):
            transitions = {name: None for name in self._sut.event_list}
            self._matrix[state.name] = {
                "source": state,
                "transitions": transitions,
            }
            logging.info("Add new state: %s", state)

            self._fsm.add_node(state.name)

    def get_state(self, state_name: str) -> State:
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

    def set_transition(self, transition: Transition):
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
        target_name = transition.target.name
        event_name = transition.event.name
        trans = self._matrix[source_name]["transitions"]
        try:
            old_state = trans[event_name]
            if not old_state:
                trans[event_name] = transition.target
                if transition.source.is_valid and transition.target.is_valid:
                    # add the transition in fsm if both states are real
                    self._fsm.add_arc(source_name, target_name, event_name)
                logging.info("Add new transition %s", transition)
                return
            if old_state != transition.target:
                logging.error(
                    "ambiguate behavior, get different result %s vs %s when processing %s on %s",
                    old_state.name,
                    target_name,
                    event_name,
                    source_name,
                )
                raise RuntimeError(
                    f"ambiguate behavior: {event_name} on {source_name}"
                    f", target state {old_state} vs {transition.target}"
                )
        except KeyError as exc:
            raise UnknownEvent(f"Invalid event {event_name}") from exc

    def explore(self, current_state: State) -> State:
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
        if not current_state.name in self._matrix:
            logging.error("State %s does not exist", current_state.name)
            raise UnknownEvent(f"Invalid state {current_state.name}")

        if self._is_mature_state(current_state.name):
            return current_state

        for event in self._sut.event_list.values():
            try:
                target_state = self._matrix[current_state.name]["transitions"][
                    event.name
                ]
                if target_state:
                    # the event on current state has been exercised, skip it
                    continue

                response = event.fire(self._sut, self._env)
                if "error" in response:
                    # an error is returned while processing the event on current state
                    self.set_transition(Transition(current_state, INVALID_STATE, event))
                else:
                    target_state = self._sut.state
                    self.set_transition(Transition(current_state, target_state, event))
                    if current_state != target_state:
                        # the target system goes to a new state by the event
                        # explore the transitions on the next state
                        return self.explore(target_state)
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
        while not self.mature():
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
            current_state = self.explore(self.get_state(source))
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
            path1 = self._fsm.shortest_path(source, target)
        if source != self._init_state.name:
            # try start from initial state
            target = self._find_nearest_immature_state(self._init_state.name)
            # there must be an immature state reachable from the initial state
            path2 = self._fsm.shortest_path(self._init_state.name, target)

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
        for name in self._fsm.bfs_vertex_name(source):
            if not self._is_mature_state(name):
                return name

        return ""

    def _print_matrix(self):
        """dump the matrix for debugging purpose"""
        for source_name, transitions in self._matrix.items():
            for event_name, target_state in transitions["transitions"].items():
                if target_state and target_state.is_valid:
                    logging.debug(
                        "%s -- %s -> %s", source_name, event_name, target_state.name
                    )
