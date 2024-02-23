"""
This module defines common data structures and constants for testing

Consider a simple system consisting with 5 events, 4 states and their transistions described below:

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

from enum import Enum
from ait.base import Event, State, InvalidState


class TestState(State):
    """The subclass inherited from State for testing"""

    def __init__(self, name: str, value: dict):
        super().__init__()
        self.fetch_state(name=name, value=value)

    def fetch_state(self, **kwargs):
        self._name = kwargs["name"]
        self._label = self._name
        self._value = kwargs["value"]
        self._valid = True


# constants
STATES = {
    "Start": TestState("Start", {"state": 0}),
    "Running": TestState("Running", {"state": 1}),
    "Paused": TestState("Paused", {"state": 2}),
    "Stopped": TestState("Stopped", {"state": 3}),
}

TRANSITION_TABLE = {
    "Start": {
        "source": STATES["Start"],
        "transitions": {"Initialize": STATES["Running"], "Reset": STATES["Start"]},
    },
    "Running": {
        "source": STATES["Running"],
        "transitions": {"Pause": STATES["Paused"], "Stop": STATES["Stopped"]},
    },
    "Paused": {
        "source": STATES["Paused"],
        "transitions": {"Resume": STATES["Running"], "Stop": STATES["Stopped"]},
    },
    "Stopped": {"source": STATES["Stopped"], "transitions": {"Reset": STATES["Start"]}},
}


class TestEvent(Event):
    """The subclass inherited from Event for testing"""

    def __init__(self, name: str):
        super().__init__(name)

    def fire(self, source: State, args: dict) -> tuple[State, dict]:
        """Process an event on the source state"""
        try:
            target_state = TRANSITION_TABLE[source.name]["transitions"][self.name]
            return target_state, {"return_code": 0}
        except KeyError:
            return InvalidState(), {"return_code": -1}


EVENT_TYPE = Enum("EventType", ["Initialize", "Reset", "Pause", "Stop", "Resume"])
EVENTS = [TestEvent(et.name) for et in EVENT_TYPE]
