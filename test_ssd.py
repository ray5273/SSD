import os.path
import pytest

from SSD import SSD

LBA_LENGTH = 100
NAND_FILE = "test_ssd_nand.txt"
OUTPUT_FILE = "test_ssd_output.txt"


def create_ssd():
    SSD.LBA_LENGTH = LBA_LENGTH
    SSD.NAND_FILE = NAND_FILE
    SSD.OUTPUT_FILE = OUTPUT_FILE
    return SSD()

def test_file_creation():
    """
    SSD 객체 맨 처음 생성 후 file들이 생성 되었는지
    """
    if os.path.exists(NAND_FILE):
        os.remove(NAND_FILE)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    SSD = create_ssd()

    assert os.path.exists(NAND_FILE)
    assert os.path.exists(OUTPUT_FILE)

def test_initial_nand_file():
    """
    nand 파일 초기화가 잘 되었는지
    """
    pass
