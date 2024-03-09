"""Events of Arbiters"""

from ait.base import Event
from ait.sut import SUT


class ArbiterEvent(Event):
    """class ArbiterEvent"""
    def fire(self, sut: SUT, args: dict) -> dict:
        """
        event fire, send request to the sut

        :param sut: the arbiter service accessor
        :type sut: SUT
        :param args: event parameters
        :type args: dict
        :return: event process result
        :rtype: dict
        """
        return sut.process_request(self._build_request(args))


class CreateRoom(ArbiterEvent):
    """createRoom event"""
    def __init__(self):
        super().__init__("createRoom")

    def _build_request(self, args: dict) -> dict:
        """
        build createRoom request

        :param args: the parameters needed to build the request, includes:
                     creator: str
                     participants: list[str]
        :type args: dict
        :return: the request
        :rtype: dict
        """
        request = {
            "createRoom": {
                "type": "transient",
                "creator": args["creator"],
                "participants": args["participants"],
            }
        }
        return request


class InviteUser(ArbiterEvent):
    """inviteUser event"""
    def __init__(self):
        super().__init__("inviteUser")

    def _build_request(self, args: dict) -> dict:
        """
        build inviteUser request

        :param args: the parameters needed to build the request, includes:
                     roomId: str
                     inviter: str
                     invitees: list[str]
        :type args: dict
        :return: the request
        :rtype: dict
        """
        request = {
            "inviteUser": {
                "roomId": args["roomId"],
                "inviter": args["inviter"],
                "invitees": args["invitees"],
            }
        }
        return request


class Accept(ArbiterEvent):
    """acknowledge event with action type accept"""
    def __init__(self):
        super().__init__("accept")

    def _build_request(self, args: dict) -> dict:
        """
        build accept event

        :param args: the parameters needed to build the request, includes:
                     roomId: str
                     user: str
        :type args: dict
        :return: the request
        :rtype: dict
        """
        request = {
            "acknowledge": {
                "roomId": args["roomId"],
                "user": args["user"],
                "action": "accept",
            }
        }
        return request


class Decline(ArbiterEvent):
    """acknowledge event with action type decline"""
    def __init__(self):
        super().__init__("decline")

    def _build_request(self, args: dict) -> dict:
        """
        build decline event

        :param args: the parameters needed to build the request, includes:
                     roomId: str
                     user: str
        :type args: dict
        :return: the request
        :rtype: dict
        """
        request = {
            "acknowledge": {
                "roomId": args["roomId"],
                "user": args["user"],
                "action": "decline",
            }
        }
        return request


class RemoveUser(ArbiterEvent):
    """removeUser event"""
    def __init__(self):
        super().__init__("removeUser")

    def _build_request(self, args: dict) -> dict:
        """
        build removeUser event

        :param args: the parameters needed to build the request, includes:
                     roomId: str
                     user: str
        :type args: dict
        :return: the request
        :rtype: dict
        """
        request = {
            "removeUser": {
                "roomId": args["roomId"],
                "remover": args["user"],
                "removee": args["user"],
            }
        }
        return request


class Content(ArbiterEvent):
    """content event"""
    def __init__(self):
        super().__init__("content")

    def _build_request(self, args: dict) -> dict:
        """
        build content event

        :param args: the parameters needed to build the request, includes:
                     roomId: str
                     user: str
                     content: str
        :type args: dict
        :return: the request
        :rtype: dict
        """
        request = {
            "content": {
                "roomId": args["roomId"],
                "user": args["user"],
                "content": args["content"],
            }
        }
        return request


class Logoff(ArbiterEvent):
    """userLogoff event"""
    def __init__(self):
        super().__init__("logoff")

    def _build_request(self, args: dict) -> dict:
        """
        build userLogoff event

        :param args: the parameters needed to build the request, includes:
                     user: str
        :type args: dict
        :return: the request
        :rtype: dict
        """
        request = {"logoff": {"user": args["user"]}}
        return request
