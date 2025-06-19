from .command import Command
from .command_interface import SSDCommandInterface


class ReadSSDCommand(SSDCommandInterface):
    def __init__(self, device, output_writer):
        super().__init__(device, output_writer, Command.READ, 2)

    def is_valid_param(self, params: list) -> bool:
        return self.common_param_validation(params)

    def execute(self, params) -> str:
        if not self.is_valid_param(params):
            self.result = self.ERROR_MSG
        else:
            address = int(params[1])
            self.result = self._device.read(address)
        return self.result
