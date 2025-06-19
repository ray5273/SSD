import pytest
from test_ssd_constants import *
from test_ssd_utils import *

class TestSsdEraseWithMock:
    @pytest.mark.parametrize( ("addr", "size"), [
        (FIRST_ADDRESS, "1"),
        (LAST_ADDRESS, "1"),
        (FIRST_ADDRESS, "10")
    ])
    def test_erase_1_call(self, ssd_and_device, addr, size):
        ssd, device = ssd_and_device
        ssd.run([ERASE_COMMAND, addr, size])
        device.erase.assert_called_with(int(addr), int(1))

    def test_erase_0(self, ssd_and_device):
        ssd, device = ssd_and_device
        erase_data(ssd, FIRST_ADDRESS, "0")
        device.erase.assert_not_called()
        assert ssd.result == OKAY_MESSAGE

    def test_invalid_erase_size(self, ssd_and_device):
        ssd, device = ssd_and_device
        ssd.run([ERASE_COMMAND, FIRST_ADDRESS, "11"])
        assert ssd.result == ERROR_MESSAGE

    def test_erase_out_of_bounds(self, ssd_and_device):
        ssd, device = ssd_and_device
        ssd.run([ERASE_COMMAND, LAST_ADDRESS, "2"])
        assert ssd.result == ERROR_MESSAGE

    def test_erase_invalid_address(self, ssd_and_device):
        ssd, device = ssd_and_device
        ssd.run([ERASE_COMMAND, "-1", "2"])
        assert ssd.result == ERROR_MESSAGE

class TestSsdEraseWithFake:
    def test_erase_1(self, fake_ssd_and_device):
        ssd, device = fake_ssd_and_device
        ssd.run([WRITE_COMMAND, FIRST_ADDRESS, "0x1234abcd"])
        ssd.run([ERASE_COMMAND, FIRST_ADDRESS, "1"])
        ssd.run([READ_COMMAND, FIRST_ADDRESS])
        assert ssd.result == DEFAULT_DATA

    def test_erase_10(self, fake_ssd_and_device):
        ssd, device = fake_ssd_and_device
        size = 10
        data_list = [ f"0x0000000{x}" for x in range(size)]
        write_incr(ssd, FIRST_ADDRESS, data_list)
        for wdata, rdata in zip(data_list, read_incr(ssd, FIRST_ADDRESS, size)):
            assert wdata == rdata
        erase_data(ssd, FIRST_ADDRESS, size)
        for rdata in read_incr(ssd, FIRST_ADDRESS, size):
            assert rdata == DEFAULT_DATA


class TestSsdErase:
    def test_erase_1(self, ssd):
        addr = FIRST_ADDRESS
        wdata = "0x1234abcd"
        check_write_and_read(ssd, addr, wdata)
        erase_data(ssd, FIRST_ADDRESS, "1")
        assert read_nand_data(ssd, FIRST_ADDRESS) == DEFAULT_DATA

    def test_erase_10(self, ssd):
        for i in range(10):
            addr = f"{i}"
            wdata = f"0x0000000{i}"
            write_data(ssd, addr, wdata)
        erase_data(ssd, FIRST_ADDRESS, "10")
        for i in range(10):
            addr = f"{i}"
            assert read_nand_data(ssd, addr) == DEFAULT_DATA