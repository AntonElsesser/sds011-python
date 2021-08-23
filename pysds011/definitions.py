#!/usr/bin/env python3

""" Basic definitions for SDS011 """

import enum


@enum.unique
class WorkingMode(enum.Enum):
    """ Working modes """
    SLEEP_MODE = 0
    WORK_MODE = 1


@enum.unique
class ReportMode(enum.Enum):
    """ Report modes """
    REPORT_ACTIVE_MODE = 0
    REPORT_QUERY_MODE = 1


@enum.unique
class Modifier(enum.Enum):
    """ Modifier """
    GET = 0
    SET = 1


@enum.unique
class Frame(enum.Enum):
    """ Frame constans """
    HEADER = 170
    TAIL = 171


@enum.unique
class MessageType(enum.Enum):
    """ Message types """
    COMMAND = 180
    COMMAND_REPLY = 197
    DATA = 192


@enum.unique
class Command(enum.Enum):
    """ Commands """
    REPORT_MODE = 2
    QUERY_DATA = 4
    SET_DEVICE_ID = 5
    WORKING_MODE = 6
    GET_FIRMWARE = 7
    WORKING_PERIOD = 8
