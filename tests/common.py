"""
This module defines the target system for testing

- TestState
- TestEvent
- TestApp

"""

import logging

from ait.interface import Event, State
from ait.interface import SUT


SAMPLES = {
    "states": {key: key.lower() for key in "ABCDEFG"},
    "events": {str(key): str(key + 100) for key in range(8)},
    "transitions": {
        "A": {"0": "B", "1": "C"},
        "B": {"2": "D"},
        "C": {"3": "D"},
        "D": {"4": "E", "5": "F"},
        "E": {"6": "G"},
        "F": {"7": "G"},
    },
    "output": {
        "A": {"0": '{"rc": 0}', "1": '{"rc", 1}'},
        "B": {"2": '{"rc": 2}'},
        "C": {"3": '{"rc": 3}'},
        "D": {"4": '{"rc": 4}', "5": '{"rc": -1}'},
        "E": {"6": '{"rc": -2, "ext_event": {"name": "ext", "value": "event"}}'},
        "F": {"7": ""},
    },
}


class StateTest(State):
    """The subclass inherited from State for testing"""

    def __str__(self) -> str:
        return f"name={self.name}, value={self.value}"

    def __repr__(self) -> str:
        return f"name={self.name}, value={self.value}"

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, StateTest):
            return False
        return self.value == rhs.value

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    @property
    def is_valid(self) -> bool:
        return True


class EventTest(Event):
    """The subclass inherited from Event for testing"""

    def __init__(self, event_name: str):
        super().__init__(event_name, {"name": event_name})

    def __str__(self) -> str:
        return f"name={self.name}, value={self.value}"

    def __repr__(self) -> str:
        return f"name={self.name}, value={self.value}"

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
        self.value = {"request": request}
        result = sut.process_request(request)
        return result


class AppTest(SUT):
    """
    The similuated application to be tested onsisting with 5 events,
    4 states and their transistions described below:

    .. code-block:: python

        state_transitions = {
            "Idle": {
                "Initialize": "Running",
                "Reset": "Idle"
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
                "Reset": "Idle"
            }
        }

    .. code-block:: none

           ┌──Reset ─┐
           │         │
           │     ┌───▼───┐
           └─────┤ Idle  ◄─────────────┐
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
        name: StateTest(name, {"state": name})
        for name in ["Idle", "Running", "Paused", "Stopped"]
    }

    transition_table = {
        "Idle": {"Initialize": "Running", "Reset": "Idle"},
        "Running": {"Pause": "Paused", "Stop": "Stopped"},
        "Paused": {"Resume": "Running", "Stop": "Stopped"},
        "Stopped": {"Reset": "Idle"},
    }

    def __init__(self):
        """
        Initialize the SUT
        """
        super().__init__({})
        self._current_state = AppTest.state_list["Idle"]

    def start(self) -> State:
        """
        Initialize the system.

        :return: the initial state
        :rtype: State
        """
        self._current_state = AppTest.state_list["Idle"]
        return self._current_state

    def reset(self):
        """reset the system to the initial state"""
        self._current_state = AppTest.state_list["Idle"]

    @property
    def state(self) -> State:
        """The current state of the system"""
        return self._current_state

    @state.setter
    def state(self, value):
        """force set the system state to a new value, for test purpose"""
        self._current_state = value

    def process_request(self, request: dict, **kwargs) -> dict:
        """
        Process an request

        :param request: the request received
        :type dict: dict
        :return: result of the request processing
        :rtype: dict
        """
        try:
            target = AppTest.transition_table[self._current_state.name][request["name"]]
            self._current_state = AppTest.state_list[target]
            return {"success": 0}
        except KeyError:
            logging.info(
                "Invalid request: %s, current state: %s", request, self._current_state
            )
            return {"error": -1}
