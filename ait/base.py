"""
This module defines the basic data structurs of the finite state machine
  
.. code-block:: python
  
    class State
    class Event
    class Transition
"""

from abc import ABC, abstractmethod
from collections import namedtuple


class State(ABC):
    """
    Interface of State
    ==================

    A state is a deterministic situation of running system which is represented in a
    unique collection of properties.

    This interface defines properties and methods a State class should provide.
    """

    def __init__(self) -> None:
        self._name: str
        self._label: str
        self._valid: bool
        self._value: dict

    def __str__(self) -> str:
        return f"name = {self._name}, label = {self._label}, value = {self._value}"

    @property
    def name(self) -> str:
        """State name used in the graph

        :return: the name of the state
        :rtype: str
        """
        return self._name

    @property
    def label(self) -> str:
        """State lable used in the graph

        :return: the detail of the state
        :rtype: str
        """
        return self._label

    @property
    def is_valid(self) -> bool:
        """The state is valid or not.
        If the target state in a transient is invalid means the API returns error on source state.

        :return: the state is valid or not
        :rtype: bool
        """
        return self._valid

    @property
    def value(self) -> dict:
        """The value of the state

        :return: a dictionary represents the state
        :rtype: Dict
        """
        return self._value

    def __eq__(self, rhs: object) -> bool:
        """compare two states

        :param rhs: the other state to be compared
        :type rhs: object
        :return: True if the values are the same
        :rtype: bool
        """
        if not isinstance(rhs, State):
            return False
        return self.value == rhs.value

    @abstractmethod
    def fetch_state(self, **kwargs):
        """abstract method of fetching current state"""


class InvalidState(State):
    """Invalid state class"""

    def __init__(self):
        """constructor"""
        super().__init__()
        self.fetch_state()

    def __str__(self) -> str:
        return "invalid state"

    def fetch_state(self, **kwargs):
        self._name = ""
        self._label = ""
        self._valid = False
        self._value = {}


class SUT(ABC):
    """
    System/Service Under Test
    =========================

    The SUT is the system/service/application to be tested. It should provide
    a set of APIs to be executed by the testing program as well as a set of
    visible states.
    """

    def __init__(self, options: dict):
        """
        constructor

        :param options: name/value pairs to setup the system
        :type options: dict
        """
        self._options = options

    @abstractmethod
    def initialize(self) -> State:
        """
        Initialize the system.

        :return: the initial state
        :rtype: State
        """

    @abstractmethod
    def reset(self):
        """reset the system to the initial state"""

    @property
    @abstractmethod
    def state(self) -> State:
        """The current state of the system"""

    @abstractmethod
    def process_request(self, request: dict) -> dict:
        """
        Process an request

        :param request: the request received
        :type dict: dict
        :return: result of the request processing
        :rtype: dict
        """


class Event(ABC):
    """Event interface"""

    def __init__(self, name: str):
        """constructor

        :param name: name of the event
        :type name: str
        """
        self._name = name

    @abstractmethod
    def _build_request(self, args: dict) -> dict:
        """
        build a request

        :param args: the arguments for building a request
        :type args: dict
        :return: the request
        :rtype: dict
        """

    @property
    def name(self) -> str:
        """name of the event

        :return: the name of the event
        :rtype: str
        """
        return self._name

    @abstractmethod
    def fire(self, sut: SUT, args: dict) -> tuple[State, dict]:
        """Fire the event on source state with arguments

        :param sut: the target system that will receive and process the event
        :type source: SUT
        :param args: arguments to build a request to the sut
        :type args: dict
        :return: target state and the result of the event processing.
          if the API returns error, the state must be an invalid state
        :rtype: tuple[State, dict]
        """
