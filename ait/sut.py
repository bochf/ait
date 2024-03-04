"""
This module defines the interface of SUT (System Under Test)
"""

from abc import ABC, abstractmethod

from ait.base import State, Event


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
