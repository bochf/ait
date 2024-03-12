"""
This module defines the interfaces of the finite state machine
  
.. code-block:: python
  
    class State
    class Event
    class SUT
"""

from abc import ABC, abstractmethod


class State(ABC):
    """
    Interface of State
    ==================

    A state is a deterministic situation of running system which is represented in a
    unique collection of properties.

    This interface defines properties and methods a State class should provide.
    """

    @abstractmethod
    def __eq__(self, __value: object) -> bool:
        """
        Compare two states

        :param __value: the other state to be compared
        :type __value: object
        :return: True if the values are the same
        :rtype: bool
        """

    @abstractmethod
    def __ne__(self, __value: object) -> bool:
        """
        Compare two states are different

        :param __value: the other state to be compared
        :type __value: object
        :return: Tue if the values are different
        :rtype: bool
        """

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

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """
        The state is valid or not.
        If the target state in a transient is invalid means the API returns error on source state.

        :return: the state is valid or not
        :rtype: bool
        """


class InvalidState(State):
    """Invalid state class"""

    def __str__(self) -> str:
        return "invalid state"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, InvalidState)

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
    @abstractmethod
    def name(self) -> str:
        """
        The unique name of the event

        :return: the name of the event
        :rtype: str
        """

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

    @property
    def env(self) -> dict:
        """The environment and configuration variables of the system"""
        return self._options

    @abstractmethod
    def start(self) -> State:
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

    @property
    @abstractmethod
    def event_list(self) -> dict[str, Event]:
        """The dictionary of event name and the event"""

    @abstractmethod
    def process_request(self, request: dict) -> dict:
        """
        Process an request

        :param request: the request received
        :type dict: dict
        :return: result of the request processing
        :rtype: dict
        """
