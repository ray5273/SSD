import os.path
from unittest.mock import DEFAULT

import pytest


from ssd import SSD
from nand import Nand


LBA_LENGTH = 100
NAND_FILE = "test_ssd_nand.txt"
OUTPUT_FILE = "test_ssd_output.txt"
DEFAULT_DATA = "0x00000000"
WRITE_COMMAND = "W"
READ_COMMAND = "R"
ERROR_MESSAGE = "ERROR"
FIRST_ADDRESS = "0"
LAST_ADDRESS = f"{LBA_LENGTH-1}"

def remove_files():
    if os.path.exists(NAND_FILE):
        os.remove(NAND_FILE)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

def assert_output_file(expected):
    with open(OUTPUT_FILE, 'r') as f:
        content = f.read()
        assert content == expected

def check_write_and_read(_ssd, addr, wdata):
    _ssd.run([WRITE_COMMAND, addr, wdata])
    _ssd.run([READ_COMMAND, addr])
    assert_output_file(wdata)

@pytest.fixture
def clean_ssd():
    nand = Nand(LBA_LENGTH, NAND_FILE)
    remove_files()
    SSD.LBA_LENGTH = LBA_LENGTH
    SSD.NAND_FILE = NAND_FILE
    SSD.OUTPUT_FILE = OUTPUT_FILE
    return SSD(nand)

@pytest.fixture
def ssd_and_device(mocker):
    device = mocker.Mock()
    ssd = SSD(device)
    return (ssd, device)

class TestSsdWithMock:
    def test_read_command(self, ssd_and_device):
        """ read command 수행 시 device의 read 호출 되는지 """
        ssd, device = ssd_and_device
        ssd.run([READ_COMMAND, FIRST_ADDRESS])
        device.read.assert_called_with(int(FIRST_ADDRESS))

    def test_write_command(self, ssd_and_device):
        """ write comand 수행 시 device의 write 호출 되는지 """
        ssd, device = ssd_and_device
        ssd.run([WRITE_COMMAND, FIRST_ADDRESS, DEFAULT_DATA])
        device.write.assert_called_with(int(FIRST_ADDRESS), DEFAULT_DATA)

    def test_uninitialized_data(self, ssd_and_device):
        """ read 하여 default 값 읽히는지"""
        ssd, device = ssd_and_device
        device.read.return_value = DEFAULT_DATA
        ssd.run([READ_COMMAND, FIRST_ADDRESS])
        assert ssd.result == DEFAULT_DATA

    def test_write_data(self, ssd_and_device):
        """ write 한 data가 올바르게 읽히는지 """
        ssd, device = ssd_and_device
        addr = FIRST_ADDRESS
        data = "0x1234abcd"
        device.read.return_value = data
        ssd.run([WRITE_COMMAND, addr, data])
        ssd.run([READ_COMMAND, addr])
        assert ssd.result == data

    def test_read_minus_address(self, ssd_and_device):
        ssd, device = ssd_and_device
        ssd.run([READ_COMMAND, "-1"])
        assert ssd.result == ERROR_MESSAGE

    def test_write_minus_address(self, ssd_and_device):
        ssd, device = ssd_and_device
        ssd.run([WRITE_COMMAND, "-1", DEFAULT_DATA])
        assert ssd.result == ERROR_MESSAGE

    def test_read_out_of_bounds(self, ssd_and_device):
        """ addr 범위 밖 read 하는 경우 -> ERROR """
        ssd, device = ssd_and_device
        addr = "9999999"
        device.read.side_effect = Exception()
        ssd.run([READ_COMMAND, addr])
        assert ssd.result == ERROR_MESSAGE

    def test_write_out_of_bounds(self, ssd_and_device):
        """ addr 범위 밖 write 하는 경우 -> ERROR """
        ssd, device = ssd_and_device
        addr = "1000000"
        device.write.side_effect = Exception()
        ssd.run([WRITE_COMMAND, addr, DEFAULT_DATA])
        assert ssd.result == ERROR_MESSAGE

    def test_invalid_command(self, ssd_and_device):
        """ 정의되지 않은 command가 들어오는 경우 -> ERROR"""
        ssd, device = ssd_and_device
        ssd.run(["UNKNOWN_COMMAND", FIRST_ADDRESS])
        assert ssd.result == ERROR_MESSAGE

    def test_invalid_read_address(self, ssd_and_device):
        """ address 형식이 올바르지 않은 경우 read  -> ERROR """
        ssd, device = ssd_and_device
        ssd.run([READ_COMMAND, "address"])
        assert ssd.result == ERROR_MESSAGE

    def test_invalid_write_address(self, ssd_and_device):
        """ address 형식이 올바르지 않은 경우 write -> ERROR"""
        ssd, device = ssd_and_device
        ssd.run([WRITE_COMMAND, "address"])
        assert ssd.result == ERROR_MESSAGE

    def test_invalid_write_data(self, ssd_and_device):
        """ write data 형식이 hex가 아닐 때 -> ERROR """
        ssd, device = ssd_and_device
        ssd.run([WRITE_COMMAND, FIRST_ADDRESS, "invalid_data"])
        assert ssd.result == ERROR_MESSAGE

class TestSsd:
    @pytest.mark.skip
    def test_file_creation(self, clean_ssd):
        """
        SSD 객체 맨 처음 생성 후 file들이 생성 되었는지
        """
        assert os.path.exists(OUTPUT_FILE)

    @pytest.mark.skip
    def test_initial_nand_file(self, clean_ssd):
        """
        nand 파일 초기화가 잘 되었는지
        """
        with open(NAND_FILE, 'r') as f:
            lines = f.readlines()
            first_line = lines[0].strip()
            last_line = lines[-1].strip()
            assert first_line == f"0 {DEFAULT_DATA}"
            assert last_line == f"{LBA_LENGTH-1} {DEFAULT_DATA}"

    @pytest.mark.skip
    def test_initial_output_file(self, clean_ssd):
        """
        output 파일 초기화가 잘 되었는지
        """
        with open(OUTPUT_FILE, 'r') as f:
            content = f.read()
            assert content == ""

    @pytest.mark.skip
    def test_read_empty_data(self, clean_ssd):
        """
        0 번 주소, 마지막 주소 read 해서 0x00000000 읽히는 지 확인
        """
        clean_ssd.run([READ_COMMAND, "0"])
        assert_output_file(DEFAULT_DATA)
        clean_ssd.run([READ_COMMAND, f"{LBA_LENGTH-1}"])
        assert_output_file(DEFAULT_DATA)

    @pytest.mark.skip
    def test_write_data(self, clean_ssd):
        """
        0번 주소, 마지막 주소 write 해서 wdata가 읽히는 지 확인
        """
        check_write_and_read(clean_ssd, "0", "0x1234ABCD")
        check_write_and_read(clean_ssd, f"{LBA_LENGTH - 1}", "0xAAAA5555")

    @pytest.mark.skip
    def test_repeat_write_to_same_address(self, clean_ssd):
        """
        같은 주소에 write 반복
        """
        for wdata in ["0xABCD1234", "0xFFFFFFFF", "0xAAAAAAAA"]:
            check_write_and_read(clean_ssd, "10", wdata)

    @pytest.mark.skip
    def test_write_multiple_address(self, clean_ssd):
        addr_data_pairs = [
            ("10", "0xAAAA5555"),
            ("20", "0xBBBB4444")
        ]

        # Write to multiple addresses
        for addr, data in addr_data_pairs:
            clean_ssd.run([WRITE_COMMAND, addr, data])

        # Read and verify each address
        for addr, expected_data in addr_data_pairs:
            clean_ssd.run([READ_COMMAND, addr])
            assert_output_file(expected_data)


    @pytest.mark.skip
    def test_out_of_lba_range_read(self, clean_ssd):
        clean_ssd.run([READ_COMMAND, f"{LBA_LENGTH}"])
        assert_output_file(ERROR_MESSAGE)

    @pytest.mark.skip
    def test_out_of_lba_range_write(self, clean_ssd):
        clean_ssd.run([WRITE_COMMAND, "12345678", "0x000000000"])
        assert_output_file(ERROR_MESSAGE)

