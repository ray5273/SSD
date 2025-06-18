from file_output import FileOutput
from lba_validator import LBAValidator
from nand import Nand
import sys

class SSD:
    LBA_LENGTH = 100
    ERROR_MSG = "ERROR"
    READ_COMMAND = "R"
    WRITE_COMMAND = "W"
    OUTPUT_FILE = "ssd_output.txt"
    def __init__(self, device):
        self._device = device
        self._out_writer = FileOutput(self.OUTPUT_FILE)
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
        params = [param.strip() for param in params]

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
                self.result = ""
        except Exception as e:
            self.result = self.ERROR_MSG
            return False
        return True


FILE_PATH = "ssd_nand.txt"
LBA_LENGTH = 100

if __name__ == "__main__":

    nand = Nand(LBA_LENGTH, FILE_PATH)
    ssd = SSD(nand)

    ssd.run(sys.argv[1:])