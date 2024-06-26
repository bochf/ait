"""
This module defines the target system for testing

- TestState
- TestEvent
- TestApp

"""

import logging

from ait.interface import Event, State
from ait.interface import SUT


SAMPLE_DATA = {
    "A": {"B": {"name": "1"}, "C": {"name": "2"}},
    "B": {"D": {"name": "3"}},
    "C": {"D": {"name": "4"}},
    "D": {"E": {"name": "5"}, "F": {"name": "6"}},
    "E": {"G": {"name": "7"}},
    "F": {"G": {"name": "8"}},
}


class TestState(State):
    """The subclass inherited from State for testing"""

    # pylint: disable=super-init-not-called
    def __init__(self, name: str, value: dict):
        self._name = name
        self._label = name
        self._value = value

    def __str__(self) -> str:
        return f"name={self.name}, value={self.value}"

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, TestState):
            return False
        return self.value == rhs.value

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> dict:
        return self._value

    @property
    def is_valid(self) -> bool:
        return True


class TestEvent(Event):
    """The subclass inherited from Event for testing"""

    def __init__(self, event_name: str):
        self._name = event_name

    @property
    def name(self) -> str:
        return self._name

    def _build_request(self, args: dict) -> dict:
        """
        build a request

        :param args: the arguments for building a request
        :type args: dict
        :return: the request
        :rtype: dict
        """
        return {"name": self.name}

    def fire(self, sut: SUT) -> dict:
        """Fire the event on source state with arguments

        :param sut: the target system that will receive and process the event
        :type source: SUT
        :param args: arguments to build a request to the sut
        :type args: dict
        :return: target state and the result of the event processing.
          if the API returns error, the state must be an invalid state
        :rtype: tuple[State, dict]
        """
        request = self._build_request(sut.env)
        result = sut.process_request(request)
        return result


class TestApp(SUT):
    """
    The similuated application to be tested onsisting with 5 events,
    4 states and their transistions described below:

    .. code-block:: python

        state_transitions = {
            "Start": {
                "Initialize": "Running",
                "Reset": "Start"
            },
            "Running": {
                "Pause": "Paused",
                "Stop": "Stopped"
            },
            "Paused": {
                "Resume": "Running",
                "Stop": "Stopped"
            },
            "Stopped": {
                "Reset": "Start"
            }
        }

    .. code-block:: none

           ┌──Reset ─┐
           │         │
           │     ┌───▼───┐
           └─────┤ Start ◄─────────────┐
                 └───┬───┘             │
                     │                 │
                   Init              Reset
                     │                 │
                 ┌───▼───┐        ┌────┴────┐
           ┌─────►Running├──Stop──► Stopped │
           │     └───┬───┘        └────▲────┘
           │         │                 │
        Resume     Pause               │
           │         │                 │
           │     ┌───▼───┐             │
           └─────┤Paused ├───Stop──────┘
                 └───────┘

    """

    state_list = {
        name: TestState(name, {"state": name})
        for name in ["Start", "Running", "Paused", "Stopped"]
    }

    transition_table = {
        "Start": {"Initialize": "Running", "Reset": "Start"},
        "Running": {"Pause": "Paused", "Stop": "Stopped"},
        "Paused": {"Resume": "Running", "Stop": "Stopped"},
        "Stopped": {"Reset": "Start"},
    }

    def __init__(self):
        """
        Initialize the SUT
        """
        super().__init__({})
        self._event_list = {
            name: TestEvent(name)
            for name in ["Initialize", "Reset", "Pause", "Stop", "Resume"]
        }
        self._current_state = TestApp.state_list["Start"]

    def start(self) -> State:
        """
        Initialize the system.

        :return: the initial state
        :rtype: State
        """
        self._current_state = TestApp.state_list["Start"]
        return self._current_state

    def reset(self):
        """reset the system to the initial state"""
        self._current_state = TestApp.state_list["Start"]

    @property
    def state(self) -> State:
        """The current state of the system"""
        return self._current_state

    @state.setter
    def state(self, value):
        """force set the system state to a new value, for test purpose"""
        self._current_state = value

    @property
    def event_list(self) -> dict[str, Event]:
        """The event list of the system"""
        return self._event_list

    def process_request(self, request: dict, **kwargs) -> dict:
        """
        Process an request

        :param request: the request received
        :type dict: dict
        :return: result of the request processing
        :rtype: dict
        """
        try:
            target = TestApp.transition_table[self._current_state.name][request["name"]]
            self._current_state = TestApp.state_list[target]
            return {"success": 0}
        except KeyError:
            logging.info(
                "Invalid request: %s, current state: %s", request, self._current_state
            )
            return {"error": -1}
