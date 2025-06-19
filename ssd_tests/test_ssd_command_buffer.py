import pytest
from pytest_mock import MockerFixture

from ssd import SSD
from test_ssd_constants import *
from test_ssd_utils import *


@pytest.fixture
def ssd_and_cmd_buf(mocker: MockerFixture):
    buffer = list()
    mem = dict()
    def fake_append_write(addr, data):
        buffer.append(  ("W", addr, data) )
    def fake_append_erase(start_addr , size):
        buffer.append( ("E", start_addr, size))
    def fake_read(addr):
        ...
    def fake_get_cnt():
        return len(buffer)

    def fake_flush():
        nonlocal buffer
        buffer = list()

    cmd_buf = mocker.Mock()
    cmd_buf.append_write = mocker.Mock(side_effect=fake_append_write)
    cmd_buf.append_erase = mocker.Mock(side_effect=fake_append_erase)
    cmd_buf.fake_read = mocker.Mock(side_effect=fake_read)
    cmd_buf.get_count = mocker.Mock(side_effect=fake_get_cnt)
    cmd_buf.flush = mocker.Mock(side_effect=fake_flush)
    ssd = SSD(cmd_buf)
    return ssd, cmd_buf


class TestSsdCommandBufferWithFake:
    def test_command_buffer_count_when_write(self, ssd_and_cmd_buf):
        ssd, cmd_buf = ssd_and_cmd_buf
        addr = FIRST_ADDRESS
        data = "0x1234abcd"
        write_data(ssd, addr, data)
        assert cmd_buf.append_write.assert_called_with(int(addr), data)
        assert cmd_buf.get_count() == 1

    def test_command_buffer_count_when_erase(self, ssd_and_cmd_buf):
        ssd, cmd_buf = ssd_and_cmd_buf
        start_addr = FIRST_ADDRESS
        size = 10
        erase_data(ssd, start_addr, size)
        assert cmd_buf.append_erase.assert_called_with(int(start_addr), size)
        assert cmb_buf.get_count() == 1

    def test_command_buffer_flush(self, ssd_and_cmd_buf):
        ssd, cmd_buf = ssd_and_cmd_buf
        write_data(ssd, FIRST_ADDRESS, "0x12345678")
        assert cmd_buf.get_count() == 1
        ssd.run("F")
        assert cmd_buf.get_count() == 0