from .command import Command
from .command_interface import SSDCommandInterface


class UnknownSSDCommand(SSDCommandInterface):
    def __init__(self, output_writer):
        super().__init__(None, output_writer, Command.UNKNOWN, 0)

    def is_valid_param(self, params: list) -> bool:
        return False

    def execute(self, params) -> str:
        self.result = self.ERROR_MSG
        return self.result