from typing import NamedTuple

from tele2client import event, client


class InputRemains(NamedTuple):
    internet: int
    voice: int
    sms: int


class InputUserRemains(NamedTuple):
    chat_id: int
    user_id: int
    remains: InputRemains


class UserData(object):
    __slots__ = ('tele2client', 'sms_waiter')

    tele2client: client.Tele2Client
    sms_waiter: event.ValueWaiter

    def __init__(self, tele2client: client.Tele2Client = None, sms_waiter: event.ValueWaiter = None):
        self.tele2client = tele2client
        self.sms_waiter = sms_waiter

    def update(self, tele2client: client.Tele2Client = None, sms_waiter: event.ValueWaiter = None):
        if tele2client is not None:
            self.tele2client = tele2client
        if sms_waiter is not None:
            self.sms_waiter = sms_waiter
