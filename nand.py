class Nand:
    def __init__(self, lba_length, data_file):
        self.data_file = data_file
        self.lba_length = lba_length
        self.default_value = "0x00000000"

        with open(self.data_file, 'w', encoding='utf-8') as f:
            pass

        with open(self.data_file, 'a', encoding='utf-8') as f:
            for i in range(lba_length):
                f.write(f"{self.default_value}\n")


    def read(self, address) -> str:
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=0):
                print(i, line)
                if i == address:
                    value = line.strip()
                    if value == 0:
                        return 'ERROR'
                    else:
                        return value
        return 'ERROR'

    def write(self, address, value):
        pass

