import pytest
from nand import Nand
from buffer_driver import BufferDriver
import copy

DEFAULT_VALUE = "0x00000000"
ERASE_MAX_SIZE = 10


class CommandBuffer:
    def __init__(self, device: Nand):
        self._device = device
        self._driver = BufferDriver()
        self._buffers = self._driver.get_list_from_buffer_files()

    def is_command_write(self, command: tuple):
        return command[0] == 'W'

    def is_command_erase(self, command: tuple):
        return command[0] == 'E'

    def get_op_from_command(self, command: tuple):
        return command[0]

    def get_lba_from_command(self, command: tuple):
        return command[1]

    def get_count_or_data(self, command: tuple):
        return command[2]

    @property
    def buffers(self):
        return self._buffers

    @buffers.setter
    def buffers(self, datas: list):
        self._buffers = datas

    def is_buffers_full(self):
        return len(self._buffers) == 5

    def is_contained_range(self, command: tuple, address):
        start_address = self.get_lba_from_command(command)
        if self.is_command_write(command):
            end_address = start_address
        else:
            end_address = start_address + self.get_count_or_data(command) - 1
        return start_address <= address <= end_address

    def is_exist_in_buffer(self, address):
        if len(self._buffers) == 0:
            return False

        for command in reversed(self._buffers):
            if self.is_contained_range(command, address):
                return True

        return False

    def get_data_in_buffer(self, address):
        for command in reversed(self._buffers):
            if self.is_contained_range(command, address):
                if self.is_command_erase(command):
                    return DEFAULT_VALUE
                else:
                    write_data = command[2]
                    return write_data
        return DEFAULT_VALUE

    def ignore_write(self, buffers):
        size = len(buffers)
        delete_index_set = set()
        for i in range(size - 1, 0, -1):
            command = buffers[i]
            lba = self.get_lba_from_command(command)
            count_or_data = self.get_count_or_data(command)
            if self.is_command_write(command):
                continue
            start_address = lba
            end_address = lba + count_or_data - 1
            for j in range(i - 1, -1, -1):
                command = buffers[j]
                lba_left = self.get_lba_from_command(command)
                if self.is_command_erase(command):
                    continue
                if start_address <= lba_left <= end_address:
                    delete_index_set.add(j)

        result_buffers = []
        for index, buffer in enumerate(buffers):
            if index in delete_index_set:
                continue
            result_buffers.append(buffer)
        return result_buffers

    def ignore_erase(self, buffers):
        size = len(buffers)
        delete_index_set = set()
        for i in range(0, size - 1):
            command = buffers[i]
            lba = self.get_lba_from_command(command)
            count_or_data = self.get_count_or_data(command)
            if self.is_command_write(command):
                continue
            start_address = lba
            end_address = lba + count_or_data - 1

            is_write = [False] * count_or_data

            for j in range(i + 1, size):
                command = buffers[j]
                lba_right = self.get_lba_from_command(command)
                if self.is_command_erase(command):
                    continue
                if start_address <= lba_right <= end_address:
                    is_write[lba_right - start_address] = True

            is_ignore_erase_possible = True
            for k in range(count_or_data):
                if is_write[k] is False:
                    is_ignore_erase_possible = False
                    break

            if is_ignore_erase_possible:
                delete_index_set.add(i)

        result_buffers = []
        for index, buffer in enumerate(buffers):
            if index in delete_index_set:
                continue
            result_buffers.append(buffer)
        return result_buffers

    def divide_erase_range_by_ten(self, erase_buffers):
        result = []
        for erase_command in erase_buffers:
            start_address = self.get_lba_from_command(erase_command)
            erase_size = self.get_count_or_data(erase_command)
            while erase_size > ERASE_MAX_SIZE:
                result.append(('E', start_address, ERASE_MAX_SIZE))
                erase_size -= ERASE_MAX_SIZE
                start_address += ERASE_MAX_SIZE
            result.append(('E', start_address, erase_size))
        return result

    def merge_erase(self, buffers):
        size = len(buffers)
        is_erase_or_write = [None] * (self._device.lba_length + 1)
        write_data = [None] * (self._device.lba_length + 1)
        for i in range(0, size):
            command = buffers[i]
            op = self.get_op_from_command(command)
            lba = self.get_lba_from_command(command)
            count_or_data = self.get_count_or_data(command)
            if self.is_command_write(command):
                is_erase_or_write[lba] = op
                write_data[lba] = count_or_data
            else:
                for k in range(0, count_or_data):
                    is_erase_or_write[lba + k] = op

        write_buffers = []
        erase_buffers = []
        index = 0
        while index < self._device.lba_length:
            if is_erase_or_write[index] == None:
                index += 1
                continue
            if is_erase_or_write[index] == 'W':
                write_buffers.append(('W', index, write_data[index]))
                index += 1
                continue
            continuous_end_index = index
            continuous_erase_end_index = index
            while is_erase_or_write[continuous_end_index] != None:
                if is_erase_or_write[continuous_end_index] == 'E':
                    continuous_erase_end_index = continuous_end_index
                else:
                    write_buffers.append(('W', continuous_end_index, write_data[continuous_end_index]))
                continuous_end_index += 1
            erase_buffers.append(('E', index, continuous_erase_end_index - index + 1))
            index = continuous_end_index
            index += 1

        divided_erase_buffers = self.divide_erase_range_by_ten(erase_buffers)
        result_buffers = divided_erase_buffers + write_buffers
        return result_buffers

    def optimize(self):
        buffers = copy.deepcopy(self._buffers)
        ignore_write_buffers = self.ignore_write(buffers)
        ignore_erase_buffers = self.ignore_erase(ignore_write_buffers)
        merge_erase_buffers = self.merge_erase(ignore_erase_buffers)
        if len(buffers) > len(merge_erase_buffers):
            self._buffers = merge_erase_buffers

    def read(self, address) -> str:
        if self.is_exist_in_buffer(address):
            return self.get_data_in_buffer(address)

        return self._device.read(address)

    def write(self, address, wdata):
        if wdata == DEFAULT_VALUE:
            self.erase(address, 1)
            return
        if self.is_buffers_full():
            self.flush()
            self._buffers = []
        self._buffers.append(('W', address, wdata))
        self.optimize()
        self._driver.make_buffer_files_from_list(self._buffers)

    def erase(self, start_address, size):
        if size <= 0:
            return
        if self.is_buffers_full():
            self.flush()
        self._buffers.append(('E', start_address, size))
        self.optimize()
        self._driver.make_buffer_files_from_list(self._buffers)

    def flush(self):
        for command in self._buffers:
            if self.is_command_write(command):
                self._device.write(command[1], command[2])
            elif self.is_command_erase(command):
                self._device.erase(command[1], command[2])

        self._driver.delete_buffer_files()
        self._driver.create_empty_files()
        self._buffers = []