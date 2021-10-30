# Console.cpp
def PrintMessage(string: object, /) -> None:
    """PrintMessage(string) -- Print a message to the output"""


def PrintLog(string: object, /) -> None:
    """PrintLog(string) -- Print a log message to the output"""


def PrintError(string: object, /) -> None:
    """PrintError(string) -- Print an error message to the output"""


def PrintWarning(arg0: object, /) -> None:
    """PrintWarning -- Print a warning to the output"""


def SetStatus(arg0: str, arg1: str, arg2: int, /) -> None:
    """Set the status for either Log, Msg, Wrn or Error for an observer"""


def GetStatus(arg0: str, arg1: str, /) -> None | int:
    """Get the status for either Log, Msg, Wrn or Error for an observer"""
