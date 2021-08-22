#!/usr/bin/env python3

import enum

@enum.unique
class WorkingMode(enum.Enum):
    SLEEP_MODE = 0
    WORK_MODE = 1
    
@enum.unique
class ReportMode(enum.Enum):
    REPORT_ACTIVE_MODE = 0
    REPORT_QUERY_MODE = 1
    
@enum.unique
class Modifier(enum.Enum):
    GET = 0
    SET = 1  
    
@enum.unique
class Frame(enum.Enum):
    HEADER = 170
    TAIL = 171
    
@enum.unique
class MessageType(enum.Enum):
    COMMAND = 180
    COMMAND_REPLY = 197
    DATA = 192

@enum.unique
class Command(enum.Enum):
    REPORT_MODE  = 2
    QUERY_DATA  = 4
    SET_DEVICE_ID  = 5
    WORKING_MODE   = 6
    GET_FIRMWARE   = 7
    WORKING_PERIOD = 8