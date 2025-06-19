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


def read_nand_data(_ssd, addr):
    _ssd.run([READ_COMMAND, addr])
    return read_output_file()

def read_ssd_data(_ssd, addr):
    _ssd.run([READ_COMMAND, addr])
    return _ssd.result

def write_data(_ssd, addr, data):
    _ssd.run([WRITE_COMMAND, addr, data])

def erase_data(_ssd, addr, size):
    _ssd.run([ERASE_COMMAND, addr, size])

def write_incr(_ssd, start_addr, data_list):
    for addr, data in enumerate(data_list, start = int(start_addr)):
        write_data(_ssd, f"{addr}", data)

def read_incr(_ssd, start_addr, size):
    start_addr = int(start_addr)
    for addr in range(start_addr, start_addr+size):
        yield read_ssd_data(_ssd, f"{addr}")

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

@pytest.fixture
def fake_ssd_and_device(mocker):
    mem = [DEFAULT_DATA for _ in range(LBA_LENGTH)]
    def fake_write(addr, data):
        mem[addr] = data
    def fake_read(addr):
        return mem[addr]

    def fake_erase(start_addr, size):
        for addr in range(start_addr, start_addr + size):
            mem[addr] = DEFAULT_DATA

    device = mocker.Mock(spec=Nand)
    device.write = mocker.Mock(side_effect=fake_write)
    device.read = mocker.Mock(side_effect=fake_read)
    device.erase = mocker.Mock(side_effect=fake_erase)
    ssd = SSD(device)
    return (ssd, device)
