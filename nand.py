import os

DEFAULT_DATA = "0x00000000"


class Nand:
    def __init__(self, lba_length, data_file):
        self.data_file = data_file
        self.lba_length = lba_length
        self.default_data = DEFAULT_DATA

        if not os.path.exists(self.data_file):
            self.create_data_file()

    def create_data_file(self):
        with open(self.data_file, 'a', encoding='utf-8') as f:
            for index in range(self.lba_length):
                f.write(f"{self.default_data}\n")

    def read(self, address) -> str:
        with open(self.data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if address >= len(lines):
            raise Exception

        return lines[address].strip()

    def write(self, address, wdata):

        with open(self.data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if address >= len(lines):
            raise Exception

        lines[address] = wdata + '\n'

        with open(self.data_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def erase(self, start_address, size):
        if size == 0:
            return

        if start_address >= self.lba_length:
            raise Exception

        end_address = start_address + size - 1
        if end_address >= self.lba_length:
            raise Exception

        with open(self.data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for address in range(start_address, end_address + 1):
            lines[address] = self.default_data + '\n'

        with open(self.data_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return