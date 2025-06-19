import os
import pytest

from nand import Nand
from ssd import SSD
from test_ssd_constants import *

def remove_files():
    if os.path.exists(NAND_FILE):
        os.remove(NAND_FILE)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

def read_output_file():
    with open(OUTPUT_FILE, 'r') as f:
        return f.read()

def assert_output_file(expected):
    assert read_output_file() == expected


def check_write_and_read(_ssd, addr, wdata):
    _ssd.run([WRITE_COMMAND, addr, wdata])
    _ssd.run([READ_COMMAND, addr])
    assert_output_file(wdata)


def read_data(_ssd, addr):
    _ssd.run([READ_COMMAND, addr])
    return read_output_file()

def write_data(_ssd, addr, data):
    _ssd.run([WRITE_COMMAND, addr, data])

def erase_data(_ssd, addr, size):
    _ssd.run([ERASE_COMMAND, addr, size])


@pytest.fixture
def ssd():
    remove_files()
    nand = Nand(LBA_LENGTH, NAND_FILE)
    SSD.LBA_LENGTH = LBA_LENGTH
    SSD.OUTPUT_FILE = OUTPUT_FILE
    return SSD(nand)

@pytest.fixture
def ssd_and_device(mocker):
    device = mocker.Mock()
    ssd = SSD(device)
    return (ssd, device)