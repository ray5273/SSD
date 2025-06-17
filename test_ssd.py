import os.path
import pytest

from SSD import SSD

LBA_LENGTH = 100
NAND_FILE = "test_ssd_nand.txt"
OUTPUT_FILE = "test_ssd_output.txt"
EMPTY_DATA = "0x00000000"


def remove_files():
    if os.path.exists(NAND_FILE):
        os.remove(NAND_FILE)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

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
