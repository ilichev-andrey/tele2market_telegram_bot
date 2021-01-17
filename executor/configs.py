from typing import NamedTuple


class Price(NamedTuple):
    count: int
    cost: int


class MinLotPrice(NamedTuple):
    gigabyte: Price
    minutes: Price
    sms: Price


class LotManagerConfig(NamedTuple):
    internet_life_time_minutes: int
    voice_life_time_minutes: int
    sms_life_time_minutes: int
    prices: MinLotPrice


class TaskManagerConfig(NamedTuple):
    interval_seconds: int
    lot_manager_config: LotManagerConfig
