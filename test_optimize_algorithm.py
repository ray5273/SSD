import pytest
from command_buffer import CommandBuffer
from buffer_driver import BufferDriver
from nand import Nand

FILE_PATH = "test_ssd_nand.txt"
LBA_LENGTH = 100
DEFAULT_VALUE = "0x00000000"
FIRST_ADDRESS = 0
LAST_ADDRESS = LBA_LENGTH - 1


@pytest.fixture
def command_buffer():
    nand = Nand(LBA_LENGTH, FILE_PATH)
    return CommandBuffer(nand)


def test_ignore_write(command_buffer):
    buffers = [('E', 0, 3), ('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('E', 0, 5)]
    new_buffers = command_buffer.ignore_write(buffers)
    assert new_buffers == [('E', 0, 3), ('E', 0, 5)]


def test_ignore_write2(command_buffer):
    buffers = [('W', 0, '0x12345678'), ('E', 0, 1), ('W', 1, '0x11111111'), ('E', 0, 5), ('W', 1, '0x11111111')]
    new_buffers = command_buffer.ignore_write(buffers)
    assert new_buffers == [('E', 0, 1), ('E', 0, 5), ('W', 1, '0x11111111')]


def test_ignore_erase(command_buffer):
    buffers = [('E', 0, 2), ('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('W', 2, '0x11111111')]
    new_buffers = command_buffer.ignore_erase(buffers)
    assert new_buffers == [('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('W', 2, '0x11111111')]


def test_ignore_erase2(command_buffer):
    buffers = [('E', 0, 2), ('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('E', 2, 2), ('W', 2, '0x11111111'),
               ('W', 3, '0x11111111')]
    new_buffers = command_buffer.ignore_erase(buffers)
    assert new_buffers == [('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('W', 2, '0x11111111'),
                           ('W', 3, '0x11111111')]


def test_merge_erase(command_buffer):
    buffers = [('E', 0, 2), ('E', 2, 2), ('W', 3, '0x11111111')]
    new_buffers = command_buffer.merge_erase(buffers)
    assert new_buffers == [('E', 0, 3), ('W', 3, '0x11111111')]


def test_merge_erase2(command_buffer):
    buffers = [('E', 0, 2), ('W', 2, '0x11111111'), ('W', 3, '0x11111111'), ('E', 4, 3), ('W', 7, '0x11111111')]
    new_buffers = command_buffer.merge_erase(buffers)
    assert new_buffers == [('E', 0, 7), ('W', 2, '0x11111111'), ('W', 3, '0x11111111'), ('W', 7, '0x11111111')]

def test_merge_erase3(command_buffer):
    buffers = [ ('E', 0, 2), ('E', 5, 3), ('E', 3, 3)]
    new_buffers = command_buffer.merge_erase(buffers)
    assert new_buffers == [('E', 0, 2), ('E', 3, 5)]

def test_total_optimize(command_buffer):
    command_buffer.buffers = [('W', 0, '0x11111111'), ('E', 1, 3), ('W', 4, '0x11111111'), ('E', 4, 7), ('W', 3, '0x11111111')]
    command_buffer.optimize()
    assert  command_buffer.buffers == [('E', 1, 10), ('W', 0, '0x11111111'), ('W', 3, '0x11111111')]


def test_total_optimize2(command_buffer):
    command_buffer.buffers = [('W', 0, '0x11111111'), ('E', 0, 3), ('W', 4, '0x11111111'), ('E', 6, 3), ('W', 3, '0x11111111'),
               ('W', 5, '0x11111111'), ('W', 1, '0x11111111'), ('W', 2, '0x11111111')]
    command_buffer.optimize()
    assert command_buffer.buffers == [('E', 0, 9),
                           ('W', 1, '0x11111111'),
                           ('W', 2, '0x11111111'),
                           ('W', 3, '0x11111111'),
                           ('W', 4, '0x11111111'),
                           ('W', 5, '0x11111111')]


def test_total_optimize3(command_buffer):
    command_buffer.buffers = [('W', 0, '0xA'), ('W', 0, '0xB')]
    command_buffer.optimize()
    assert command_buffer.buffers == [('W', 0, '0xB')]