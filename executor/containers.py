from typing import Dict, List

from tele2client.client import Tele2Client
from tele2client.containers import LotInfo


class TaskSummary(object):
    gigabyte_count: int
    minute_count: int
    sms_count: int

    def __init__(self, gigabyte_count: int = 0, minute_count: int = 0, sms_count: int = 0):
        self.gigabyte_count = gigabyte_count
        self.minute_count = minute_count
        self.sms_count = sms_count

    def increment(self, summary: 'TaskSummary'):
        self.gigabyte_count += summary.gigabyte_count
        self.minute_count += summary.minute_count
        self.sms_count += summary.sms_count

    def decrement(self, summary: 'TaskSummary'):
        self.gigabyte_count -= summary.gigabyte_count
        self.minute_count -= summary.minute_count
        self.sms_count -= summary.sms_count

    def set(self, summary: 'TaskSummary'):
        self.gigabyte_count = summary.gigabyte_count
        self.minute_count = summary.minute_count
        self.sms_count = summary.sms_count


class Task(object):
    tele2client: Tele2Client
    lots: List[LotInfo]  # Список активных лотов
    summary: TaskSummary
    sold_summary: TaskSummary

    def __init__(self, tele2client: Tele2Client, lots: List[LotInfo], summary: TaskSummary,
                 sold_summary: TaskSummary = TaskSummary()):
        self.tele2client = tele2client
        self.lots = lots
        self.summary = summary
        self.sold_summary = sold_summary


class Clients(object):
    _tele2clients = Dict[str, Tele2Client]

    def __init__(self):
        self._tele2clients = {}

    def add(self, tele2client: Tele2Client):
        self._tele2clients[tele2client.phone_number] = tele2client

    def has(self, phone_number: str) -> bool:
        return phone_number in self._tele2clients

    def get(self, phone_number: str) -> Tele2Client:
        return self._tele2clients[phone_number]
