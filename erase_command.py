from command import Command
from command_interface import SSDCommandInterface


class EraseSSDCommand(SSDCommandInterface):
    MAX_ERASE_SIZE = 10

    def __init__(self, device, output_writer):
        super().__init__(device, output_writer, Command.ERASE, 3)

    def is_valid_param(self, params: list) -> bool:
        if not self.common_param_validation(params):
            return False
        address, size = params[1], params[2]
        if not size.isdigit():
            return False

        address, size = int(address), int(size)
        if size > self.MAX_ERASE_SIZE:
            return False

        if address + size -1 >= self._lba_length:
            return False
        return True

    def execute(self, params) -> str:
        if not self.is_valid_param(params):
            self.result = self.ERROR_MSG
        else:
            address, size = int(params[1]), int(params[2])
            if size == 0:
                self.result = ""
            else:
                self.result = self._device.erase(address, size)

        return self.result