from command import Command
from command_interface import SSDCommandInterface


class EraseSSDCommand(SSDCommandInterface):
    def __init__(self, device, output_writer):
        super().__init__(device, output_writer, Command.ERASE, 3)

    def is_valid_param(self, params: list) -> bool:
        if not self.common_param_validation(params):
            return False

        return True

    def execute(self, params) -> str:
        pass