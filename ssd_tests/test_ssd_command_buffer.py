import pytest
from pytest_mock import MockerFixture

from ssd import SSD
from test_ssd_constants import *
from test_ssd_utils import *
import shutil

@pytest.fixture
def ssd_and_fake_cmd_buf(mocker: MockerFixture):
    buffer = list()
    mem = dict()
    def fake_append_write(addr, data):
        buffer.append(  ("W", addr, data) )
        mem[int(addr)] = data
    def fake_append_erase(start_addr , size):
        buffer.append( ("E", start_addr, size))
        for addr in range(start_addr, start_addr + size):
            mem[addr] = DEFAULT_DATA
    def fake_read(addr):
        return mem.get(int(addr))
    def fake_get_cnt():
        return len(buffer)

    def fake_flush():
        nonlocal buffer
        buffer = list()

    cmd_buf = mocker.Mock()
    cmd_buf.append_write = mocker.Mock(side_effect=fake_append_write)
    cmd_buf.append_erase = mocker.Mock(side_effect=fake_append_erase)
    cmd_buf.read = mocker.Mock(side_effect=fake_read)
    cmd_buf.get_count = mocker.Mock(side_effect=fake_get_cnt)
    cmd_buf.flush = mocker.Mock(side_effect=fake_flush)
    ssd = SSD(cmd_buf)
    return ssd, cmd_buf

@pytest.fixture
def cmd_buf_ssd():
    nand = Nand(LBA_LENGTH, NAND_FILE)
    if os.path.isdir(BUFFER_DIR):
        shutil.rmtree(BUFFER_DIR)
    cb = CommandBuffer(nand, BUFFER_DIR)
    return cb, SSD(cb)


class TestSsdCommandBufferWithFake:
    def test_command_buffer_count_when_write(self, ssd_and_fake_cmd_buf):
        ssd, cmd_buf = ssd_and_fake_cmd_buf
        addr = FIRST_ADDRESS
        data = "0x1234abcd"
        write_data(ssd, addr, data)
        assert cmd_buf.append_write.assert_called_with(int(addr), data)
        assert cmd_buf.get_count() == 1

    def test_command_buffer_count_when_erase(self, ssd_and_fake_cmd_buf):
        ssd, cmd_buf = ssd_and_fake_cmd_buf
        start_addr = FIRST_ADDRESS
        size = 10
        erase_data(ssd, start_addr, size)
        assert cmd_buf.append_erase.assert_called_with(int(start_addr), size)
        assert cmb_buf.get_count() == 1

    def test_command_buffer_flush(self, ssd_and_fake_cmd_buf):
        ssd, cmd_buf = ssd_and_fake_cmd_buf
        write_data(ssd, FIRST_ADDRESS, "0x12345678")
        assert cmd_buf.get_count() == 1
        flush_buffer(ssd)
        assert cmd_buf.assert_called_once()
        assert cmd_buf.get_count() == 0

    def test_zero_buffer_cnt_when_read(self, ssd_and_fake_cmd_buf):
        ssd, cmd_buf = ssd_and_fake_cmd_buf
        rdata = read_ssd_data(ssd, FIRST_ADDRESS)
        assert rdata == DEFAULT_DATA
        cmd_buf.get_count() == 0

    def test_buffer_full_when_write(self, ssd_and_fake_cmd_buf):
        ssd, cmd_buf = ssd_and_fake_cmd_buf
        data_list = ["0x01010101" for _ in range(5)]
        write_incr(ssd, FIRST_ADDRESS, data_list)
        assert cmd_buf.get_count() == 5

    def test_fast_read(self, ssd_and_fake_cmd_buf):
        ssd, cmd_buf = ssd_and_fake_cmd_buf
        wdata = "0x01010101"
        data_list = [wdata for _ in range(5)]
        write_incr(ssd, FIRST_ADDRESS, data_list)
        rdata = read_ssd_data(ssd, FIRST_ADDRESS)
        cmd_buf.read.called_with(FIRST_ADDRESS)
        assert rdata == wdata

    def test_read_not_buffered_data(self, ssd_and_fake_cmd_buf):
        ssd, cmd_buf = ssd_and_fake_cmd_buf
        wdata = "0x01010101"
        data_list = [wdata for _ in range(5)]
        write_incr(ssd, FIRST_ADDRESS, data_list)
        rdata = read_ssd_data(ssd, LAST_ADDRESS)
        cmd_buf.read.called_with(LAST_ADDRESS)
        assert rdata == DEFAULT_DATA


class TestSsdCommandBuffer:
    def test_write_buffer_cnt(self, cmd_buf_ssd):
        cb, ssd = cmd_buf_ssd
        wdata = "0x01010101"
        data_list = [wdata for _ in range(3)]
        write_incr(ssd, "10", data_list)
        assert cb.get_count() == 3

    def test_erase_buffer_cnt(self, cmd_buf_ssd):
        cb, ssd = cmd_buf_ssd
        addr_list = [10, 20, 30]
        for start_addr in addr_list:
            erase_data(ssd, start_addr, 1)
        assert cb.get_count() == len(addr_list)


    def test_read_buffer_cnt(self, cmd_buf_ssd):
        cb, ssd = cmd_buf_ssd
        read_incr(ssd, 0, 10)
        assert cb.get_count() == 0

    def test_read_data(self, cmd_buf_ssd):
        cb, ssd= cmd_buf_ssd
        wdata = "0x12345678"
        addr = 10
        write_data(ssd, addr, wdata)
        assert read_ssd_data(ssd, addr) == wdata