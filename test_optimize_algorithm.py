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
    command_buffer.buffers = buffers
    command_buffer.ignore_write()
    assert command_buffer.buffers == [('E', 0, 3), ('E', 0, 5)]


def test_ignore_write2(command_buffer):
    buffers = [('W', 0, '0x12345678'), ('E', 0, 1), ('W', 1, '0x11111111'), ('E', 0, 5), ('W', 1, '0x11111111')]
    command_buffer.buffers = buffers
    command_buffer.ignore_write()
    assert command_buffer.buffers == [('E', 0, 1), ('E', 0, 5), ('W', 1, '0x11111111')]


def test_ignore_erase(command_buffer):
    buffers = [('E', 0, 2), ('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('W', 2, '0x11111111')]
    command_buffer.buffers = buffers
    command_buffer.ignore_erase()
    assert command_buffer.buffers == [('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('W', 2, '0x11111111')]


def test_ignore_erase2(command_buffer):
    buffers = [('E', 0, 2), ('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('E', 2, 2), ('W', 2, '0x11111111'),
               ('W', 3, '0x11111111')]
    command_buffer.buffers = buffers
    command_buffer.ignore_erase()
    assert command_buffer.buffers == [('W', 0, '0x12345678'), ('W', 1, '0x11111111'), ('W', 2, '0x11111111'),
                           ('W', 3, '0x11111111')]


def test_merge_erase(command_buffer):
    command_buffer.buffers = [('E', 0, 2), ('E', 2, 2), ('W', 3, '0x11111111')]
    command_buffer.merge_erase()
    assert command_buffer.buffers == [('E', 0, 3), ('W', 3, '0x11111111')]


def test_merge_erase2(command_buffer):
    command_buffer.buffers = [('E', 0, 2), ('W', 2, '0x11111111'), ('W', 3, '0x11111111'), ('E', 4, 3), ('W', 7, '0x11111111')]
    command_buffer.merge_erase()
    assert command_buffer.buffers == [('E', 0, 7), ('W', 2, '0x11111111'), ('W', 3, '0x11111111'), ('W', 7, '0x11111111')]

def test_merge_erase3(command_buffer):
    command_buffer.buffers = [ ('E', 0, 2), ('E', 5, 3), ('E', 3, 3)]
    command_buffer.merge_erase()
    assert command_buffer.buffers == [('E', 0, 2), ('E', 3, 5)]

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


def test_buffer_length(command_buffer):
    wdata = "0x12345678"
    command_buffer.flush()
    command_buffer.write( 5, wdata)
    command_buffer.write( 10, wdata)
    command_buffer.write( 15, wdata)
    command_buffer.write( 20, wdata)
    command_buffer.write( 25, wdata)
    command_buffer.write( 35, wdata)
    assert len(command_buffer.buffers) == 1

def test_divide_by_ten(command_buffer):
    command_buffer.buffers = [('E', 10, 6), ('E', 16, 5)]
    command_buffer.optimize()
    assert command_buffer.buffers == [('E', 10, 10), ('E', 20, 1)]

def test_divide_by_ten_2(command_buffer):
    command_buffer.buffers = [('E', 10, 8), ('E', 18, 8),('E',26,3),('W',26,'0x11111111'),('E',29,1)]
    command_buffer.optimize()
    assert command_buffer.buffers == [('E', 10, 10), ('E', 20, 10),('W',26,'0x11111111')]