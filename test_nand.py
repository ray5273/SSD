import pytest

from nand import Nand

FILE_PATH = "test_ssd_nand.txt"
LBA_LENGTH = 100
DEFAULT_VALUE = "0x00000000"
FIRST_ADDRESS = 0
LAST_ADDRESS = LBA_LENGTH - 1

@pytest.fixture
def nand():
    return Nand(LBA_LENGTH, FILE_PATH)

def test_nand_read_uninitialized_data_at_start_address(nand):
    assert nand.read(FIRST_ADDRESS) == DEFAULT_VALUE

def test_nand_read_uninitialized_data_at_last_address(nand):
    assert nand.read(LAST_ADDRESS) == DEFAULT_VALUE

def test_nand_write_first_address(nand):
    addr = FIRST_ADDRESS + 1
    wdata = "0x1234abcd"
    nand.write(addr, wdata)
    assert nand.read(addr) == wdata

def test_nand_write_last_address(nand):
    addr = LAST_ADDRESS - 1
    wdata = "0x1f1f1f1f"
    nand.write(addr, wdata)
    assert nand.read(addr) == wdata

def test_nand_read_out_of_bounds(nand):
    addr = 999999
    with pytest.raises(Exception):
        nand.read(addr)

def test_nand_write_out_of_bounds(nand):
    addr = 1000000
    wdata = "0x00000000"
    with pytest.raises(Exception):
        nand.write(addr, wdata)

def test_nand_write_at_bound(nand):
    addr = LAST_ADDRESS + 1
    wdata = "0x1234abcd"
    with pytest.raises(Exception):
        nand.write(addr, wdata)