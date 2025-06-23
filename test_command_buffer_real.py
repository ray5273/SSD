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


def test_read_command(command_buffer):
    command_buffer.write(1,'0x00001234')
    assert command_buffer.read(1) == '0x00001234'

def test_erase_read_command(command_buffer):
    command_buffer.write(2,'0x00001234')
    command_buffer.write(3,'0x00001234')
    command_buffer.write(1,'0x00001234')
    command_buffer.erase(1,5)
    assert command_buffer.read(1) == '0x00000000'
    assert command_buffer.read(2) == '0x00000000'
    assert command_buffer.read(3) == '0x00000000'
    assert command_buffer.read(4) == '0x00000000'
    assert command_buffer.read(5) == '0x00000000'


def test_flush(command_buffer):
    command_buffer.write(2,'0x00001234')
    command_buffer.write(3,'0x00001234')
    command_buffer.write(1,'0x00001234')
    command_buffer.write(4,'0x00001234')
    command_buffer.write(5,'0x00001234')
    command_buffer.write(6,'0x00001234')
    command_buffer.write(7,'0x00001234')
    command_buffer.write(8,'0x00001234')
    command_buffer.write(9,'0x00001234')
    assert command_buffer.read(1) == '0x00001234'
    assert command_buffer.read(2) == '0x00001234'
    assert command_buffer.read(3) == '0x00001234'
    assert command_buffer.read(4) == '0x00001234'
    assert command_buffer.read(5) == '0x00001234'
    assert command_buffer.read(6) == '0x00001234'
    assert command_buffer.read(7) == '0x00001234'
    assert command_buffer.read(8) == '0x00001234'
    assert command_buffer.read(9) == '0x00001234'
    command_buffer.flush()
    assert command_buffer.read(1) == '0x00001234'
    assert command_buffer.read(2) == '0x00001234'
    assert command_buffer.read(3) == '0x00001234'
    assert command_buffer.read(4) == '0x00001234'
    assert command_buffer.read(5) == '0x00001234'
    assert command_buffer.read(6) == '0x00001234'
    assert command_buffer.read(7) == '0x00001234'
    assert command_buffer.read(8) == '0x00001234'
    assert command_buffer.read(9) == '0x00001234'


def test_fast_read(command_buffer):
    command_buffer.write(3,'0x11111111')
    command_buffer.erase(3,1)
    assert command_buffer.read(3) == '0x00000000'