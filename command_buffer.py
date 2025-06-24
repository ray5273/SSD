from typing import List, Union, Optional

from constants import DEFAULT_DATA
from bufferables import Bufferable, WriteBuffer, EraseBuffer
from nand import Nand
from buffer_driver import BufferDriver
import copy

DEFAULT_VALUE = "0x00000000"
ERASE_MAX_SIZE = 10

class CommandBuffer:
    def __init__(self, device: Nand):
        self._device = device
        self._driver = BufferDriver()
        self.buffers = self._driver.get_list_from_buffer_files()
        Bufferable.device = device

    @property
    def buffers(self):
        return self.bufferables_to_tuples(self._buffers)
        # return self._buffers

    @buffers.setter
    def buffers(self, datas: List[tuple]):
        self._buffers = self.tuples_to_bufferables(datas)
        # self._buffers = datas

    def tuples_to_bufferables(self, param_list: List[tuple]) -> List[Union[WriteBuffer, EraseBuffer]]:
        buffers = []
        for params in param_list:
            if params[0] == 'W':
                buffers.append(WriteBuffer(*params))
            elif params[0] == 'E':
                buffers.append(EraseBuffer(*params))
        return buffers

    def bufferables_to_tuples(self, buffers: List[Bufferable]) -> List[tuple]:
        return [x.to_tuple() for x in buffers ]

    def is_buffers_full(self):
        return len(self._buffers) == 5

    def get_data_in_buffer(self, address: int) -> Optional[str]:
        for buffer in reversed(self._buffers):
            if buffer.contains_address(address):
                return buffer.get_data(address)
        return None

    def add_buffer(self, buffer: Bufferable):
        if self.is_buffers_full():
            self.flush()
        self._buffers.append(buffer)
        self.optimize()
        self._driver.make_buffer_files_from_list(self.buffers)

    def ignore_write(self):
        size = len(self._buffers)
        for i in range(size - 1, 0, -1):
            right_buffer = self._buffers[i]
            # if right_buffer.is_write():
            #     continue
            for j in range(i - 1, -1, -1):
                left_write_buffer = self._buffers[j]
                if left_write_buffer.is_erase():
                    continue
                if right_buffer.contains_address( left_write_buffer.addr ):
                    left_write_buffer.need_to_ignore = True

        self._buffers = [ x for x in self._buffers if x.need_to_ignore == False]

    def ignore_erase(self, buffers: List[tuple]):
        size = len(buffers)
        buffers = self.tuples_to_bufferables(buffers)
        for i in range(0, size - 1):
            left_erase_buffer = buffers[i]
            if left_erase_buffer.is_write():
                continue
            for j in range(i + 1, size):
                right_write_buffer = buffers[j]
                if right_write_buffer.is_erase():
                    continue
                if left_erase_buffer.contains_address(right_write_buffer.addr):
                    left_erase_buffer.mark_overwritten(right_write_buffer.addr)

            if left_erase_buffer.is_all_overwritten():
                left_erase_buffer.need_to_ignore = True

        result_buffers = [ x for x in buffers if x.need_to_ignore == False]
        return self.bufferables_to_tuples(result_buffers)

    def divide_erase_range_by_max_size(self, erase_buffers: List[EraseBuffer]) -> List[EraseBuffer]:
        result = []
        for buffer in erase_buffers:
            start_address = buffer.start_addr
            erase_size = buffer.size
            while erase_size > ERASE_MAX_SIZE:

                result.append(EraseBuffer('E', start_address, ERASE_MAX_SIZE))
                erase_size -= ERASE_MAX_SIZE
                start_address += ERASE_MAX_SIZE
            result.append(EraseBuffer('E', start_address, erase_size))
        return result

    def merge_erase(self, buffers: List[tuple]):
        buffer_table = self.create_buffer_table(buffers)

        write_buffers = []
        erase_buffers = []

        is_erase_section = False
        erase_start = None
        erase_end = None
        for addr, buffer in enumerate(buffer_table):
            if buffer is None:
                if is_erase_section:
                    is_erase_section = False
                    erase_buffers.append( EraseBuffer('E', erase_start, erase_end-erase_start + 1 ))
            elif buffer.is_write():
                write_buffers.append(buffer)
            elif buffer.is_erase():
                if not is_erase_section:
                    is_erase_section = True
                    erase_start = addr
                erase_end = addr

        divided_erase_buffers = self.divide_erase_range_by_max_size(erase_buffers)
        result_buffers = divided_erase_buffers + write_buffers
        return self.bufferables_to_tuples(result_buffers)

    def create_buffer_table(self, buffers: List[tuple]) -> List[Union[WriteBuffer, EraseBuffer, None]]:
        buffers = self.tuples_to_bufferables(buffers)
        buffer_table = [None] * (self._device.lba_length + 1)
        for buffer in buffers:
            if buffer.is_write():
                buffer_table[buffer.addr] = buffer
            elif buffer.is_erase():
                for erase_addr in range(buffer.start_addr, buffer.end_addr + 1):
                    buffer_table[erase_addr] = buffer
        return buffer_table

    def optimize(self):
        # buffers = copy.deepcopy(self.buffers)
        self.ignore_write()
        ignore_erase_buffers = self.ignore_erase(self.buffers)
        merge_erase_buffers = self.merge_erase(ignore_erase_buffers)
        if len(self._buffers) > len(merge_erase_buffers):
            self.buffers = merge_erase_buffers

    def read(self, address: int) -> str:
        if data := self.get_data_in_buffer(address):
            return data
        return self._device.read(address)

    def write(self, address: int, wdata: str):
        if wdata == DEFAULT_DATA:
            self.erase(address, 1)
            return
        self.add_buffer( WriteBuffer('W', address, wdata))

    def erase(self, start_address: int, size: int):
        if size <= 0:
            return
        self.add_buffer( EraseBuffer('E', start_address, size))

    def flush(self):
        for buffer in self._buffers:
            buffer.execute()
        self._buffers = []

        self._driver.delete_buffer_files()
        self._driver.create_empty_files()
