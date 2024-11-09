"""Test Coverage Strategy Interface"""

from abc import ABC, abstractmethod
from typing import Union
import pprint
from ait.graph_wrapper import GraphWrapper


class Strategy(ABC):
    """
    Interface of a graph traversal strategy
    """

    def __init__(self):
        self._paths = []

    @abstractmethod
    def travel(self, state_machine: GraphWrapper, start: Union[str, int]):
        """
        graph traversal method

        :param graph_wrapper: the graph to visit
        :type graph_wrapper: GraphWrapper
        """
        pass

    @property
    def tracks(self) -> str:
        return pprint.pformat(self._paths)
