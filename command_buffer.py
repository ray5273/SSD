import pytest
from nand import Nand
from buffer_driver import BufferDriver

DEFAULT_VALUE = "0x00000000"


class CommandBuffer:
    def __init__(self, device: Nand):
        self._device = device
        self._driver = BufferDriver()

    def is_contained_range(self, command: tuple, address):
        start_address = command[1]
        end_address = command[2]
        if command[0] == 'W':
            end_address = start_address
        return start_address <= address and address <= end_address

    def is_exist_in_buffer(self, buffers, address):
        if len(buffers) == 0:
            return False

        for command in reversed(buffers):
            if self.is_contained_range(command, address):
                return True

        return False

    def get_data_in_buffer(self, buffers, address):
        for command in reversed(buffers):
            if self.is_contained_range(command, address):
                if command[0] == 'E':
                    return DEFAULT_VALUE
                else:
                    write_data = command[2]
                    return write_data
        return DEFAULT_VALUE

    def ignore_write(self, buffers):
        size = len(buffers)
        delete_index_set = set()
        for i in range(size - 1, 0, -1):
            commands = buffers[i]
            command = commands[0]
            lba = commands[1]
            count_or_data = commands[2]
            if command == "W":
                continue
            start_address = lba
            end_address = lba + count_or_data - 1
            for j in range(i - 1, -1, -1):
                commands = buffers[j]
                command_left = commands[0]
                lba_left = commands[1]
                if command_left == "E":
                    continue
                if lba_left >= start_address and lba_left <= end_address:
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
            commands = buffers[i]
            command = commands[0]
            lba = commands[1]
            count_or_data = commands[2]
            if command == "W":
                continue
            start_address = lba
            end_address = lba + count_or_data - 1

            is_write = [False] * count_or_data

            for j in range(i + 1, size):
                commands = buffers[j]
                command_right = commands[0]
                lba_right = commands[1]
                if command_right == "E":
                    continue
                if lba_right >= start_address and lba_right <= end_address:
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

    def merge_erase(self):
        pass

    def optimize(self, buffers):
        return buffers

    def read(self, address) -> str:
        buffers = self._driver.get_list_from_buffer_files()
        if self.is_exist_in_buffer(buffers, address):
            return self.get_data_in_buffer(buffers, address)

        return self._device.read(address)

    def write(self, address, wdata):
        if wdata == "0x00000000":
            self.erase(address, 1)
        buffers = self._driver.get_list_from_buffer_files()
        if len(buffers) == 5:
            self.flush()
            buffers = []
        buffers.append(('W', address, wdata))
        buffers = self.optimize(buffers)
        self._driver.make_buffer_files_from_list(buffers)

    def erase(self, start_address, size):
        if size <= 0:
            return
        buffers = self._driver.get_list_from_buffer_files()
        if len(buffers) == 5:
            self.flush()
            buffers = []
        buffers.append(('E', start_address, size))
        buffers = self.optimize(buffers)
        self._driver.make_buffer_files_from_list(buffers)

    def flush(self):
        buffers = self._driver.get_list_from_buffer_files()

        for command in buffers:
            if command[0] == 'W':
                self._device.write(command[1], command[2])
            elif command[0] == 'E':
                self._device.erase(command[1], command[2])

        self._driver.delete_buffer_files()
        self._driver.create_empty_files()
