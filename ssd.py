from file_output import FileOutput
from lba_validator import LBAValidator


class SSD:
    LBA_LENGTH = 100
    ERROR_MSG = "ERROR"
    READ_COMMAND = "R"
    WRITE_COMMAND = "W"

    def __init__(self, device):
        self._device = device
        self._out_writer = FileOutput()
        self._last_result = None
        self._param_validator = LBAValidator(self.LBA_LENGTH)

    @property
    def result(self):
        return self._last_result

    @result.setter
    def result(self, value):
        self._out_writer.write(value)
        self._last_result = value

    def run(self, params: list) -> bool:
        if not self._param_validator.is_valid(params):
            self.result = self.ERROR_MSG
            return False

        command, address = params[0], int(params[1])
        try:
            if command == self.READ_COMMAND:
                self.result = self._device.read(address)
            if command == self.WRITE_COMMAND:
                value = params[2]
                self._device.write(address, value)
        except Exception as e:
            self.result = self.ERROR_MSG
            return False
        return True
