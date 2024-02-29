"""This module defines exceptions"""


class UnknownState(Exception):
    """Raised when the state name does not exist"""


class UnknownEvent(Exception):
    """Raised when the event name does not exist"""
