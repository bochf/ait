"""
This module defines the basic data structurs of the finite state machine
  
.. code-block:: python
  
    class State
    class Event
    class Transition
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class State(ABC):
    """
    Interface of State
    ==================

    A state is a deterministic situation of running system which is represented in a
    unique collection of properties.

    This interface defines properties and methods a State class should provide.
    """

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, rhs: object) -> bool:
        """
        Compare two states

        :param rhs: the other state to be compared
        :type rhs: object
        :return: True if the values are the same
        :rtype: bool
        """
        pass

    @abstractmethod
    def __ne__(self, __value: object) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The unique state name in the system

        :return: the name of the state
        :rtype: str
        """

    @property
    @abstractmethod
    def value(self) -> dict:
        """The value of the state

        :return: a dictionary represents the state
        :rtype: Dict
        """
        pass

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """The state is valid or not.
        If the target state in a transient is invalid means the API returns error on source state.

        :return: the state is valid or not
        :rtype: bool
        """
        pass


class InvalidState(State):
    """Invalid state class"""

    # pylint: disable=super-init-not-called
    def __init__(self):
        """constructor"""

    def __str__(self) -> str:
        return "invalid state"

    def __eq__(self, rhs: object) -> bool:
        return isinstance(rhs, InvalidState)

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    @property
    def name(self) -> str:
        return "invalid"

    @property
    def value(self) -> dict:
        return {"value": "invalid"}

    @property
    def is_valid(self) -> bool:
        return False


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
    def fire(self, sut: object, args: dict) -> dict:
        """Fire the event on source state with arguments

        :param sut: the target system that will receive and process the event
        :type source: SUT
        :param args: arguments to build a request to the sut, the args might be
                     updated according to the response of the event processing
        :type args: dict
        :return: the result of the event processing.
        :rtype: dict
        """


@dataclass
class Arrow:
    """
    An arrow is a directed edge in the directed graph with an ordered pair of
    vertices and an arc connects them. The arrow's direction is from tail to
    head.
    """

    tail: str
    head: str
    name: str

    def __str__(self) -> str:
        return f"{self.tail}--{self.name}->{self.head}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Arrow):
            return False
        return (
            self.tail == other.tail
            and self.head == other.head
            and self.name == other.name
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Arrow):
            raise ValueError(f"Compare Arrow to {other.__class__}")
        if self.tail < other.tail:
            return True
        if self.tail > other.tail:
            return False

        # equal tail, compare head
        if self.head < other.head:
            return True
        if self.head > other.head:
            return False

        # equal tail and head, compare name
        if self.name < other.name:
            return True
        return False

    @property
    def end_points(self) -> list[str]:
        """return tail/head pair"""
        return [self.tail, self.head]
