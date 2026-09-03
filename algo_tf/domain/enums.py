from __future__ import annotations

from enum import StrEnum


class Mode(StrEnum):
    REPLAY = "REPLAY"
    PAPER = "PAPER"
    SHADOW = "SHADOW"
    LIMITED_LIVE = "LIMITED_LIVE"
    LIVE = "LIVE"


class Action(StrEnum):
    WAIT = "WAIT"
    ENTER = "ENTER"
    SCALE_IN = "SCALE_IN"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    CANCEL_REPLACE = "CANCEL_REPLACE"
    PAUSE = "PAUSE"
    HALT = "HALT"


class Direction(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


class AssetClass(StrEnum):
    ETF = "ETF"
    EQUITY = "EQUITY"
    OPTION = "OPTION"


class OrderType(StrEnum):
    LIMIT = "LIMIT"


class TimeInForce(StrEnum):
    DAY = "DAY"
    IOC = "IOC"
