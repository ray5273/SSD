import pytest
from pygments.lexers.comal import Comal80Lexer

from buffer_driver import BufferDriver
from command_buffer import CommandBuffer
from nand import Nand

FILE_PATH = "test_ssd_nand.txt"
LBA_LENGTH = 100
DEFAULT_VALUE = "0x00000000"
FIRST_ADDRESS = 0
LAST_ADDRESS = LBA_LENGTH - 1


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
    # device = Nand(LBA_LENGTH, FILE_PATH)
    device = mocker.Mock(spec=Nand)
    device.lba_length = LBA_LENGTH
    cb = CommandBuffer(device)
    cb._driver = driver

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
        cb.flush()
        assert len(cb.buffers) == 0
        addr = 5
        wdata = "0xAAAAAAAA"
        cb.write(addr, wdata)
        cb.flush()
        assert len(cb.buffers) == 0

    def test_write_buffer_length(self, cb_with_fake):
        cb, driver, device = cb_with_fake
        cb.flush()
        wdata = "0x12345678"
        expected = 1
        for i in range(1,10):
            cb.write(i, wdata)
            assert len(cb.buffers) == expected
            expected += 1
            if expected > 5:
                expected  -= 5




