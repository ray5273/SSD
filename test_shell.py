
import os
import pytest
from pytest_mock import MockerFixture

import shell
import tempfile

def test_shell_read(mocker: MockerFixture):
    mocker.patch('shell.read', return_value='0x99999999')
    result = shell.read("3")
    assert result == "0x99999999"

def test_call_system():
    cmd = f'dir'
    assert shell.call_system(cmd) == 0

def test_read_result_file():
    TEST_DATA = '0x99999999'
    # 시스템 임시 디렉터리 경로
    tmp_dir = tempfile.gettempdir()
    # 내가 지정한 임시 파일명
    filename = "ssd_output.txt"
    file_path = os.path.join(tmp_dir, filename)
    # 임시 파일 생성 및 쓰기
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(TEST_DATA)

    assert shell.read_result_file(file_path) == TEST_DATA

@pytest.mark.skip
def test_read_with_valid_lba():
    ...