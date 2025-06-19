from enum import StrEnum

class Command(StrEnum):
    READ  = "R"
    WRITE = "W"
    ERASE = "E"
    UNKNOWN = "U"
