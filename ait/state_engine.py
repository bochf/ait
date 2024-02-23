"""
  This module implements a finite state machine generator.
  Based on a given INIT state and a list of predefined events, the state engine
  applies each event on the INIT state. If the transition creats a new state, 
  the engine will repeatedly apply each event on the new states until all the 
  state/event are executed.
"""

import logging

from ait.base import State, Event
from ait.finite_state_machine import FiniteStateMachine


class StateEngine:
    """StateEngine class"""

    def __init__(self, init_state: State, events: list[Event], options: dict = None):
        self._env = options
        self._events = events
        self._matrix = {}
        self._fsm = FiniteStateMachine()
        self._add_new_state(init_state)

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

    @property
    def completed(self) -> bool:
        """check all the state/event are executed

        :return: True if all the transitions are executed
        :rtype: bool
        """
        for row in self._matrix.values():
            for target in row["transitions"].values():
                if not target:
                    return False

        return True

    def _add_new_state(self, new_state: State):
        """Add a new state and initialize the transitions of the new state

        :param new_state: the new state
        :type new_state: State
        """
        if not self.get_state(new_state.name):
            transitions = {event.name: None for event in self._events}
            self._matrix[new_state.name] = {
                "source": new_state,
                "transitions": transitions,
            }
            logging.info("Add new state: %s", new_state)

            self._fsm.add_state(new_state)

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

    def get_transition(self, state_name: str, event_name: str) -> State:
        """Get target state when an event happens on the source state

        :param source: the source state name
        :type source: str
        :param event: the event name
        :type event: str
        :return: _description_
        :rtype: State
        """
        try:
            return self._matrix[state_name]["transitions"][event_name]
        except KeyError:
            return None

    def set_transition(self, source: State, target: State, event: Event):
        """Set the transition from source state to target state on the event

        :param source: the source state
        :type source: State
        :param target: the target state
        :type target: State
        :param event: the event
        :type event: Event
        """
        if source.name not in self._matrix:
            self._add_new_state(source)

        trans = self._matrix[source.name]["transitions"]
        old_state = trans[event.name]
        if old_state:
            assert old_state == target, (
                f"ambiguate behavior: {event.name} on {source.name}, target "
                f"state {old_state} vs {target}"
            )
        else:
            trans[event.name] = target
            logging.info(
                "Add new transition source=%s, target=%s, event=%s",
                source,
                target,
                event.name,
            )

    def evolve(self, current_state: State):
        """Build the state machine from a state

        :param current_state: the current state of the system
        :type current_state: State
        """
        if self.completed:
            return  # stop evolving if there is no empty transition

        self._print_matrix()
        # try to fill the transitions for the current state
        for event in self._events:
            if self.get_transition(current_state.name, event.name):
                continue

            target_state, response = event.fire(current_state, self._env)
            self.set_transition(current_state, target_state, event)

            if not target_state.is_valid:
                # the system rejected the event, current state is not changed
                continue

            if current_state == target_state:
                continue

            # if the state changed, test the system on the new state
            self.evolve(target_state)
            break

    def _find_nearest_incomplete_state(self) -> State:
        """
        Find the nearest incomplete state to the current state.
        The incomplete state is a state has not exercise all the events.
        The closest state means a state that requires the minimal steps from
        the current state. This is to start testing the unvisited path in the
        least cost.

        :return: the new state to be tested which has at least one empty path.
        :rtype: State
        """

    def _print_matrix(self):
        """dump the matrix for debugging purpose"""
        for source_name, transitions in self._matrix.items():
            for event_name, target_state in transitions["transitions"].items():
                if target_state and target_state.is_valid:
                    logging.debug(
                        "%s -- %s -> %s", source_name, event_name, target_state.name
                    )
