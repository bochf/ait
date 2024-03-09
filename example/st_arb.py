"""States of Arbiters"""

from ait.base import State


class ArbiterState(State):
    """class ArbiterState"""

    # pylint: disable=super-init-not-called
    def __init__(self, name: str, value: dict):
        self._name = name
        self._value = value

    def __str__(self) -> str:
        return f"name={self.name}, value={self.value}"

    def __eq__(self, __value) -> bool:
        if not isinstance(__value, ArbiterState):
            return False
        return self.value == __value.value

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> dict:
        return self._value

    @property
    def is_valid(self) -> bool:
        return True
