class Nand:
    def __init__(self, data_file, lba_length):
        self.data_file = data_file
        self.lba_length = lba_length

        with open(self.data_file, 'w', encoding='utf-8') as f:
            pass

        with open(self.data_file, 'a', encoding='utf-8') as f:
            for i in range(self.lba_length):
                f.write(f"{self.lba_length}\n")


    def read(self, address) -> str:


    def write(self, address, value):
        pass

