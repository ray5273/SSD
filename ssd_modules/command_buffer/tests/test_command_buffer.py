import pytest

from ssd_modules.command_buffer.buffer_driver import BufferDriver
from ssd_modules.command_buffer.command_buffer import CommandBuffer
from ssd_modules.device.nand import Nand

FILE_PATH = "../../../command_buffer_tests/test_ssd_nand.txt"
LBA_LENGTH = 100
DEFAULT_VALUE = "0x00000000"
FIRST_ADDRESS = 0
LAST_ADDRESS = LBA_LENGTH - 1
WDATA = "0x1234AAAA"

@pytest.fixture
def cb_with_fake(mocker):
    _buffers = []
    def fake_delete():
        nonlocal _buffers
        _buffers = []

    def fake_create():
        nonlocal _buffers
        _buffers = []

    def get_buffers():
        nonlocal _buffers
        return _buffers

    def fake_make(_new_buf):
        nonlocal _buffers
        _buffers = _new_buf

    driver = mocker.Mock(spec=BufferDriver)
    driver.delete_buffer_files = mocker.Mock(side_effect=fake_delete)
    driver.create_empty_files = mocker.Mock(side_effect=fake_create)
    driver.get_list_from_buffer_files = mocker.Mock(side_effect=get_buffers)
    driver.make_buffer_files_from_list = mocker.Mock(side_effect=fake_make)
    device = mocker.Mock(spec=Nand)
    device.lba_length = LBA_LENGTH
    cb = CommandBuffer(device)
    cb._driver = driver
    cb.flush()
    return cb, driver, device

@pytest.fixture
def cb_and_device(mocker):
    device = mocker.Mock()
    cb = CommandBuffer(device)
    device.lba_length = LBA_LENGTH
    return cb, device


class TestCommandBufferWithMock:
    def test_fast_read_call(self, cb_and_device):
        cb, device = cb_and_device
        addr = 5
        wdata = "0x12345678"
        cb.write(addr, wdata)
        rdata = cb.read(addr)
        assert rdata == wdata
        device.read.assert_not_called()
        assert len(cb.buffers) == 1

    def test_flush(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        assert len(cb.buffers) == 0
        addr = 5
        wdata = "0xAAAAAAAA"
        cb.write(addr, wdata)
        cb.flush()
        assert len(cb.buffers) == 0

    def test_write_buffer_length(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        wdata = "0x12345678"
        expected = 1
        for i in range(1,10):
            cb.write(i, wdata)
            assert len(cb.buffers) == expected
            expected += 1
            if expected > 5:
                expected  -= 5

    def test_ignore_command(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        wdata = "0xBBBBBBBB"
        cb.erase(18, 3)
        cb.write(21, wdata)
        cb.erase(18, 5)
        assert len(cb.buffers) == 1

    def test_merge_erase(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.write(20, WDATA)
        cb.erase(10, 4)
        cb.erase(12, 3)
        assert len(cb.buffers) == 2

    def test_merge_big_erase(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.write(20, WDATA)
        cb.erase(5, 5)
        cb.erase(15, 5)
        cb.erase(10, 5)
        assert len(cb.buffers) == 3

    def test_merge_small_erase(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.erase(5, 3)
        cb.erase(8, 3)
        cb.erase(11, 3)
        assert len(cb.buffers) == 1
        assert cb.buffers == [('E', 5, 9)]
        cb.erase(14, 2)
        assert len(cb.buffers) == 2
        cb.write(10, WDATA)
        assert len(cb.buffers) == 3

    def test_write_erase_length(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.erase(5, 5)
        cb.write(10, WDATA)
        cb.erase(15, 5)
        cb.write(20, WDATA)
        cb.erase(25, 5)
        assert len(cb.buffers) == 5
        cb.write(30, WDATA)
        assert len(cb.buffers) == 1

    def test_read_erased_data(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.write(5, WDATA)
        cb.erase(5, 1)
        assert cb.read(5) == DEFAULT_VALUE


    def test_ignore_write(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        new_wdata = "0xDDDDDDDD"
        cb.write(5, WDATA)
        cb.write(10, WDATA)
        cb.write(5, new_wdata)
        assert cb.read(5) == new_wdata
        assert len(cb.buffers) == 2

    def test_erase_write_data(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.erase(5, 5)
        cb.write(8, WDATA)
        cb.erase(5, 5)
        assert len(cb.buffers) == 1

    def test_erase_backward(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        for idx in range(95, 100):
            cb.write(idx, WDATA)
        assert cb.read(99) == WDATA
        cb.erase(99, 1)
        cb.erase(98, 1)
        cb.erase(97, 1)
        cb.erase(96, 1)
        cb.erase(95, 1)
        assert cb.read(99) == DEFAULT_VALUE
        assert cb.buffers == [('E', 95, 5)]
        cb.erase(95, 5)
        cb.erase(90, 5)
        cb.erase(85, 5)
        cb.erase(80, 5)
        cb.erase(75, 5)
        assert len(cb.buffers) == 3

    def test_many_erase(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.flush()
        for addr in range(50, 85):
            cb.erase(addr, 1)
        assert len(cb.buffers) == 4
        assert cb.buffers == [
            ('E', 50, 10),
            ('E', 60, 10),
            ('E', 70, 10),
            ('E', 80, 5),
        ]