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
    ssd_file_name = "ssd_nand.txt"
    output_file_name = "ssd_output.txt"
    LBA_LENGTH = 100

    def __init__(self):
        self.ssd_file = self.init_ssd_nand_file()
        self.output_file = self.init_sdd_output_file()

    def init_ssd_nand_file(self):
        ...

    def init_sdd_output_file(self):
        ...


    def run(self, argv):
        if argv[0] == "R":
            cmd = ReadCommand(argv[1:])
        elif argv[0] == "W":
            cmd = WriteCommand(argv[1:])
        cmd.execute()


if __name__ == "__main__":
    SSD().run(sys.argv[1:])