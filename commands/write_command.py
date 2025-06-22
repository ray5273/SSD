from .command import Command
from .command_interface import SSDCommandInterface


class WriteSSDCommand(SSDCommandInterface):
    VALUE_LENGTH = 10

    def __init__(self, device, output_writer):
        super().__init__(device, output_writer, Command.WRITE, 3)


    def is_valid_param(self, params: list) -> bool:
        if not self.common_param_validation(params):
            return False

        value = params[2]
        if len(value) != self.VALUE_LENGTH:
            return False

        try:
            _ = int(value, 16)
        except ValueError:
            return False

        return True

    def execute(self, params) -> str:
        if not self.is_valid_param(params):
            self.result = self.ERROR_MSG
        else:
            try:
                address, value = int(params[1]), params[2]
                self._device.write(address, value)
                self.result = ""
            except Exception:
                self.result = self.ERROR_MSG

        return self.result