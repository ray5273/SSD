import os
import sys
from abc import ABC, abstractmethod

class ICommand(ABC):
    def __init__(self, argv, input_fh, output_fh):
        self.validate_command(argv)

    @abstractmethod
    def validate_command(self):
        ...

    @abstractmethod
    def execute(self):
        ...

    def is_hex(self, data):
        ...

class ReadCommand(ICommand):
    ...

class WriteCommand(ICommand):
    ...


class SSD:
    NAND_FILE = "ssd_nand.txt"
    OUTPUT_FILE = "ssd_output.txt"
    LBA_LENGTH = 100

    def __init__(self):
        self.init_ssd_nand_file()
        self.init_sdd_output_file()

    def init_ssd_nand_file(self):
        if not os.path.exists(self.NAND_FILE):
            with open(self.NAND_FILE, "w") as f:
                f.write("")
            for lba in range(self.LBA_LENGTH):
                # WriteCommand(self.NAND_FILE, self.output_file, lba, 0x00000000).execute()
                pass

    def init_sdd_output_file(self):
        if not os.path.exists(self.OUTPUT_FILE):
            with open(self.OUTPUT_FILE, "w") as f:
                f.write("")

    def run(self, argv):
        if argv[0] == "R":
            cmd = ReadCommand(argv[1:])
        elif argv[0] == "W":
            cmd = WriteCommand(argv[1:])
        cmd.execute()


if __name__ == "__main__":
    SSD().run(sys.argv[1:])