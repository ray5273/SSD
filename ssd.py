from file_output import FileOutput
from lba_validator import LBAValidator


class SSD:
    LBA_LENGTH = 100

    def __init__(self, device):
        self._device = device
        self._out_writer = FileOutput()
        self._last_result = None
        self._param_validator = LBAValidator(self.LBA_LENGTH)

    def run(self, params: list) -> bool:
        if not self._param_validator.is_valid(params):
            return False

        command, address = params[0], params[1]
        try:
            if command == "R":
                self._last_result = self._device.read(address)
                self._out_writer.write(self._last_result)
            if command == "W":
                value = params[2]
                self._device.write(address, value)
        except Exception as e:
            return False
        return True
