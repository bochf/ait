"""Events of Arbiters"""

from ait.base import Event, SUT


class ArbiterEvent(Event):
    def fire(self, sut: SUT, args: dict) -> dict:
        return sut.process_request(self._build_request(args))


class CreateRoom(ArbiterEvent):
    def __init__(self):
        super().__init__("createRoom")

    def _build_request(self, args: dict) -> dict:
        request = {
            "createRoom": {
                "type": "transient",
                "creator": args["creator"],
                "participants": args["participants"],
            }
        }
        return request


class InviteUser(ArbiterEvent):
    def __init__(self):
        super().__init__("inviteUser")

    def _build_request(self, args: dict) -> dict:
        request = {
            "inviteUser": {
                "roomId": args["roomId"],
                "inviter": args["inviter"],
                "invitees": args["invitees"],
            }
        }
        return request


class Accept(ArbiterEvent):
    def __init__(self):
        super().__init__("accept")

    def _build_request(self, args: dict) -> dict:
        request = {
            "acknowledge": {
                "roomId": args["roomId"],
                "user": args["user"],
                "action": "accept",
            }
        }
        return request


class Decline(ArbiterEvent):
    def __init__(self):
        super().__init__("decline")

    def _build_request(self, args: dict) -> dict:
        request = {
            "acknowledge": {
                "roomId": args["roomId"],
                "user": args["user"],
                "action": "decline",
            }
        }
        return request


class RemoveUser(ArbiterEvent):
    def __init__(self):
        super().__init__("removeUser")

    def _build_request(self, args: dict) -> dict:
        request = {
            "removeUser": {
                "roomId": args["roomId"],
                "remover": args["user"],
                "removee": args["user"],
            }
        }
        return request


class Content(ArbiterEvent):
    def __init__(self):
        super().__init__("content")

    def _build_request(self, args: dict) -> dict:
        request = {
            "content": {
                "roomId": args["roomId"],
                "user": args["user"],
                "content": args["content"],
            }
        }
        return request


class Logoff(ArbiterEvent):
    def __init__(self):
        super().__init__("logoff")

    def _build_request(self, args: dict) -> dict:
        request = {"logoff": {"user": args["user"]}}
        return request
