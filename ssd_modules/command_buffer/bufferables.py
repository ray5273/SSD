from abc import abstractmethod, ABC
from constants import DEFAULT_DATA

class Bufferable(ABC):
    device = None
    def __init__(self):
        self.need_to_ignore = False

    @classmethod
    def is_write(cls):
        return False

    @classmethod
    def is_erase(cls):
        return False

    @abstractmethod
    def contains_address(self, addr):
        ...

    @abstractmethod
    def get_data(self, addr):
        ...

    @abstractmethod
    def to_tuple(self):
        ...

    @abstractmethod
    def execute(self):
        ...


class WriteBuffer(Bufferable):
    def __init__(self, cmd, addr, data):
        super().__init__()
        self.addr = addr
        self.data = data

    @classmethod
    def is_write(cls):
        return True

    def contains_address(self, addr):
        return addr == self.addr

    def get_data(self, addr):
        return self.data

    def to_tuple(self):
        return ('W', self.addr, self.data)

    def execute(self):
        self.device.write(self.addr, self.data)


class EraseBuffer(Bufferable):
    def __init__(self, cmd, start_addr, size):
        super().__init__()
        self.start_addr = start_addr
        self.size = size
        self.end_addr = start_addr + size -1
        self.overwrite_table = [ False ] * size

    @classmethod
    def is_erase(cls):
        return True

    def mark_overwritten(self, addr):
        self.overwrite_table[addr - self.start_addr] = True

    def is_all_overwritten(self):
        return all(self.overwrite_table)

    def contains_address(self, addr):
        return self.start_addr <= addr <= self.end_addr

    def get_data(self, addr):

        return DEFAULT_DATA

    def execute(self):
        self.device.erase(self.start_addr, self.size)

    def to_tuple(self):
        return ('E', self.start_addr, self.size)

