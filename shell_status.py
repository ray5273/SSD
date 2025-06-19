
from enum import Enum

class SHELL_STATUS(Enum):
    SUCCESS = 0
    INVALID_COMMAND = 1
    INVALID_PARAMETER = 2
    NO_INPUT = 3
    EXIT = 99


