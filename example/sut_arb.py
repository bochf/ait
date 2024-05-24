"""Service Under Test simulating Arbiters"""

import logging

from ait.interface import SUT
from ait.interface import State, Event
from .evt_arb import (
    CreateRoom,
    InviteUser,
    Accept,
    Decline,
    RemoveUser,
    Content,
    Logoff,
)
from .st_arb import ArbiterState


class MockArbiter(SUT):
    """
    The mock class simulating Arbiter's behavior with 7 events,
    8 states and their transistions described below:

    .. csv-table::
        :file: arb.csv
        :header-rows: 1

    """

    states = {
        "no room": ArbiterState("no room", {"room": None, "users": []}),
        "in room": ArbiterState("in room", {"room": 0, "users": [0, 0]}),
        "invited": ArbiterState("invited", {"room": 0, "users": [0, 2]}),
        "rejected": ArbiterState("rejected", {"room": 0, "users": [0, 3]}),
        "removed": ArbiterState("removed", {"room": 0, "users": [0, 4]}),
        "pre-invited": ArbiterState("pre-invited", {"room": 0, "users": [0, 5]}),
        "in room 2": ArbiterState("in room 2", {"room": 0, "users": [4, 0]}),
        "invited 2": ArbiterState("invited 2", {"room": 0, "users": [4, 2]}),
    }

    events = {
        "createRoom": CreateRoom(),
        "inviteUser": InviteUser(),
        "accept": Accept(),
        "decline": Decline(),
        "content": Content(),
        "removeUser": RemoveUser(),
        "logoff": Logoff(),
    }
    transitions = {
        "no room": {"createRoom": "pre-invited", "logoff": "no room"},
        "in room": {
            "createRoom": "in room",
            "content": "in room",
            "removeUser": "removed",
            "logoff": "in room 2",
        },
        "invited": {
            "createRoom": "invited",
            "inviteUser": "invited",
            "accept": "in room",
            "decline": "rejected",
            "content": "invited",
            "removeUser": "removed",
            "logoff": "invited 2",
        },
        "rejected": {
            "createRoom": "pre-invited",
            "inviteUser": "invited",
            "content": "rejected",
            "logoff": "no room",
        },
        "removed": {
            "createRoom": "pre-invited",
            "inviteUser": "invited",
            "content": "removed",
            "removeUser": "removed",
            "logoff": "no room",
        },
        "pre-invited": {
            "createRoom": "pre-invited",
            "inviteUser": "invited",
            "content": "invited",
            "removeUser": "removed",
            "logoff": "no room",
        },
        "in room 2": {"createRoom": "in room", "logoff": "in room 2"},
        "invited 2": {"createRoom": "invited", "logoff": "invited 2"},
    }

    def __init__(self, options: dict):
        """
        Initialize the SUT
        """
        super().__init__(options)
        self._current_state = MockArbiter.states["no room"]

    def start(self) -> State:
        """
        Initialize the system.

        :return: the initial state
        :rtype: State
        """
        self._current_state = MockArbiter.states["no room"]
        logging.info("Start the service, current state=%s", self._current_state.name)
        return self._current_state

    def reset(self):
        """reset the system to the initial state"""
        self._current_state = MockArbiter.states["no room"]
        logging.info("Reset state to %s", self._current_state.name)

    @property
    def state(self) -> State:
        """The current state of the system"""
        return self._current_state

    @state.setter
    def state(self, value: State):
        """force set the system state to a new value, for test purpose"""
        self._current_state = value

    @property
    def event_list(self) -> dict[str, Event]:
        """The event list of the system"""
        return MockArbiter.events

    def process_request(self, request: dict) -> dict:
        """
        Process an request

        :param request: the request received
        :type dict: dict
        :return: result of the request processing
        :rtype: dict
        """
        try:
            source = self._current_state.name
            event = next(iter(request))
            if event == "acknowledge":
                event = request["acknowledge"]["action"]
            logging.info("Processing request %s, current state: %s", event, source)
            target = MockArbiter.transitions[source][event]
            self._current_state = MockArbiter.states[target]
            return {"success": True}
        except KeyError:
            logging.info(
                "Invalid request: %s, current state: %s", request, self._current_state
            )
            return {"success": False}
