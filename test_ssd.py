import os.path
import pytest

from ssd import SSD

LBA_LENGTH = 100
NAND_FILE = "test_ssd_nand.txt"
OUTPUT_FILE = "test_ssd_output.txt"
EMPTY_DATA = "0x00000000"
WRITE_COMMAND = "W"
READ_COMMAND = "R"




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
    remove_files()
    SSD.LBA_LENGTH = LBA_LENGTH
    SSD.NAND_FILE = NAND_FILE
    SSD.OUTPUT_FILE = OUTPUT_FILE
    return SSD()

def test_file_creation(clean_ssd):
    """
    SSD 객체 맨 처음 생성 후 file들이 생성 되었는지
    """
    assert os.path.exists(NAND_FILE)
    assert os.path.exists(OUTPUT_FILE)

def test_initial_nand_file(clean_ssd):
    """
    nand 파일 초기화가 잘 되었는지
    """
    with open(NAND_FILE, 'r') as f:
        lines = f.readlines()
        first_line = lines[0].strip()
        last_line = lines[-1].strip()
        assert first_line == f"0 {EMPTY_DATA}"
        assert last_line == f"{LBA_LENGTH-1} {EMPTY_DATA}"

def test_initial_output_file(clean_ssd):
    """
    output 파일 초기화가 잘 되었는지
    """
    with open(OUTPUT_FILE, 'r') as f:
        content = f.read()
        assert content == ""

@pytest.mark.skip
def test_read_empty_data(clean_ssd):
    """
    0 번 주소, 마지막 주소 read 해서 0x00000000 읽히는 지 확인
    """
    clean_ssd.run([READ_COMMAND, "0"])
    assert_output_file(EMPTY_DATA)
    clean_ssd.run([READ_COMMAND, f"{LBA_LENGTH-1}"])
    assert_output_file(EMPTY_DATA)

@pytest.mark.skip
def test_write_data(clean_ssd):
    """
    0번 주소, 마지막 주소 write 해서 wdata가 읽히는 지 확인
    """
    check_write_and_read(clean_ssd, "0", "0x1234ABCD")
    check_write_and_read(clean_ssd, f"{LBA_LENGTH - 1}", "0xAAAA5555")