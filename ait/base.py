"""
This module defines the basic data structurs of the finite state machine
  
.. code-block:: python
  
    class State
    class Event
    class Transition
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class SUT:  # pylint: disable=too-few-public-methods
    """forward delaration"""


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

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)


class InvalidState(State):
    """Invalid state class"""

    def __init__(self):
        """constructor"""
        self._name = "invalid"
        self._label = "invalid"
        self._valid = False
        self._value = {}

    def __str__(self) -> str:
        return "invalid state"


class Event(ABC):
    """
    Interface of Event
    ==================

    The events are the outside data sent to the SUT. Each event has a unique
    name. The events can be fired to the SUT and get a result back.
    """

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
    def fire(self, sut: SUT, args: dict) -> dict:
        """Fire the event on source state with arguments

        :param sut: the target system that will receive and process the event
        :type source: SUT
        :param args: arguments to build a request to the sut, the args might be
                     updated according to the response of the event processing
        :type args: dict
        :return: target state and the result of the event processing.
          if the API returns error, the state must be an invalid state
        :rtype: tuple[State, dict]
        """


@dataclass
class Transition:
    """
    A transition is a tuple of the source state, target state, and the event
     that triggers the transition. It represents a directed edge in a graph.
    """

    source: State
    target: State
    event: Event

    def __str__(self) -> str:
        return f"{self.source.name}--{self.event.name}->{self.target.name}"
