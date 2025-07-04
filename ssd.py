import sys

from ssd_modules.command_buffer.command_buffer import CommandBuffer
from ssd_modules.commands.command import Command
from ssd_modules.commands.command_interface import SSDCommandInterface
from ssd_modules.commands.erase_command import EraseSSDCommand
from ssd_modules.commands.flush_command import FlushSSDCommand
from ssd_modules.commands.read_command import ReadSSDCommand
from ssd_modules.commands.unknown_command import UnknownSSDCommand
from ssd_modules.commands.write_command import WriteSSDCommand
from ssd_modules.file_output.file_output import FileOutput
from ssd_modules.device.nand import Nand

COMMAND_CLASSES: dict[Command, type[SSDCommandInterface]] = {
    Command.READ: ReadSSDCommand,
    Command.WRITE: WriteSSDCommand,
    Command.ERASE: EraseSSDCommand,
    Command.FLUSH: FlushSSDCommand,
}


class SSD:
    LBA_LENGTH = 100
    ERROR_MSG = "ERROR"
    OUTPUT_FILE = "ssd_output.txt"

    def __init__(self, device):
        self._device = device
        self._out_writer = FileOutput(self.OUTPUT_FILE)
        self.result = ""
        self.commands: dict[Command, SSDCommandInterface] = {
            cmd: cls(self._device, self._out_writer) for cmd, cls in COMMAND_CLASSES.items()
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
