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



class TestSsdErase:
    def test_erase_1(self, ssd):
        addr = FIRST_ADDRESS
        wdata = "0x1234abcd"
        check_write_and_read(ssd, addr, wdata)
        erase_data(ssd, FIRST_ADDRESS, "1")
        assert read_data(ssd, FIRST_ADDRESS) == DEFAULT_DATA

    def test_erase_10(self, ssd):
        for i in range(10):
            addr = f"{i}"
            wdata = f"0x0000000{i}"
            write_data(ssd, addr, wdata)
        erase_data(ssd, FIRST_ADDRESS, "10")
        for i in range(10):
            addr = f"{i}"
            assert read_data(ssd, addr) == DEFAULT_DATA