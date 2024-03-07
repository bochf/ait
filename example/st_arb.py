"""States of Arbiters"""

from ait.base import State


class ArbiterState(State):
    """class ArbiterState"""
    # pylint: disable=super-init-not-called
    def __init__(self, name: str, value: dict):
        self._name = name
        self._label = name
        self._value = value
        self._valid = True
