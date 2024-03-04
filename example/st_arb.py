"""States of Arbiters"""

from ait.base import State


class ArbiterState(State):
    def __init__(self, name: str, value: dict):
        self._name = name
        self._label = name
        self._value = value
        self._valid = True
