import os


class Nand:
    def __init__(self, lba_length, data_file):
        self.data_file = data_file
        self.lba_length = lba_length
        self.default_value = "0x00000000"

    def create_data_file(self):
        with open(self.data_file, 'a', encoding='utf-8') as f:
            for i in range(self.lba_length):
                f.write(f"{self.default_value}\n")

    def read(self, address) -> str:
        if not os.path.exists(self.data_file):
            self.create_data_file()

        with open(self.data_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=0):
                if i == address:
                    value = line.strip()
                    return value
        raise Exception

    def write(self, address, wdata):
        if not os.path.exists(self.data_file):
            self.create_data_file()

        with open(self.data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if address <= len(lines):
            lines[address] = wdata + '\n'
            with open(self.data_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        else:
            raise Exception
