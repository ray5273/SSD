from .command import Command
from .command_interface import SSDCommandInterface


class FlushSSDCommand(SSDCommandInterface):
    def __init__(self, device, output_writer):
        super().__init__(device, output_writer, Command.FLUSH, 0)

    def is_valid_param(self, params: list) -> bool:
        return True

    def execute(self, params) -> str:
        self._device.flush()
        return ""
