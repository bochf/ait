"""Test Coverage Strategy Interface"""

from abc import ABC, abstractmethod

from ait.graph_wrapper import GraphWrapper


class Strategy(ABC):
    @abstractmethod
    def travel(self, graph_wrapper: GraphWrapper, start: str = "", end: str = ""):
        """
        graph traversal method

        :param graph_wrapper: the graph to visit
        :type graph_wrapper: GraphWrapper
        """
