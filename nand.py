import os
from typing import List
from constants import DEFAULT_DATA


class Nand:
    def __init__(self, lba_length, data_file):
        self.data_file = data_file
        self.lba_length = lba_length
        self.default_data = f"{DEFAULT_DATA}\n"

        if not os.path.exists(self.data_file):
            self.create_data_file()

    def create_data_file(self):
        lines = [ self.default_data for _ in range(self.lba_length)]
        self._write_lines(lines)

    def read(self, address: int) -> str:
        if self.is_out_of_range(address):
            raise Exception

        lines = self._read_lines()
        return lines[address].strip()

    def write(self, address: int, wdata: str):
        if self.is_out_of_range(address):
            raise Exception

        lines = self._read_lines()
        lines[address] = wdata + '\n'
        self._write_lines(lines)

    def erase(self, start_address: int, size: int):
        if size == 0:
            return

        if self.is_out_of_range(start_address):
            raise Exception

        end_address = start_address + size - 1
        if end_address >= self.lba_length:
            raise Exception

        lines = self._read_lines()
        for address in range(start_address, end_address + 1):
            lines[address] = self.default_data
        self._write_lines(lines)

    def is_out_of_range(self, address: int):
        if address < 0 or address >= self.lba_length:
            return True
        return False

    def _read_lines(self) -> List[str]:
        with open(self.data_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return lines

    def _write_lines(self, _lines: List[str]):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            f.writelines(_lines)
