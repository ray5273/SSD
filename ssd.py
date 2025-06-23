import sys

from commands.command import Command
from commands.erase_command import EraseSSDCommand
from commands.flush_command import FlushSSDCommand
from commands.read_command import ReadSSDCommand
from commands.unknown_command import UnknownSSDCommand
from commands.write_command import WriteSSDCommand

from file_output import FileOutput
from nand import Nand
from command_buffer import CommandBuffer

class SSD:
    LBA_LENGTH = 100
    ERROR_MSG = "ERROR"
    OUTPUT_FILE = "ssd_output.txt"

    def __init__(self, device):
        self._device = device
        self._out_writer = FileOutput(self.OUTPUT_FILE)
        self.result = ""
        self.commands = {
            Command.READ: ReadSSDCommand(self._device, self._out_writer),
            Command.WRITE: WriteSSDCommand(self._device, self._out_writer),
            Command.ERASE: EraseSSDCommand(self._device, self._out_writer),
            Command.FLUSH: FlushSSDCommand(self._device, self._out_writer)
        }

    def run(self, params: list) -> bool:
        if not params:
            self.write_error()
            return False

        command = self.commands.get(params[0], UnknownSSDCommand(self._out_writer))

        try:
            self.result = command.execute(params)
        except Exception:
            self.write_error()
            return False

        return True

    def write_error(self):
        self.result = self.ERROR_MSG
        self._out_writer.write(self.result)

FILE_PATH = "ssd_nand.txt"
LBA_LENGTH = 100

if __name__ == "__main__":
    nand = Nand(LBA_LENGTH, FILE_PATH)
    command_buffer = CommandBuffer(nand)
    ssd = SSD(command_buffer)

    ssd.run(sys.argv[1:])
