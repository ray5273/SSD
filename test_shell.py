
import os
from unittest.mock import patch

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

def get_test_ssd_output_file(filename = "ssd_output.txt", data='0x99999999'):
    # 시스템 임시 디렉터리 경로
    tmp_dir = tempfile.gettempdir()
    # 내가 지정한 임시 파일명

    file_path = os.path.join(tmp_dir, filename)
    # 임시 파일 생성 및 쓰기
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)
    return file_path

def test_read_result_file():
    test_data = '0x99999999'
    file_path = get_test_ssd_output_file(data=test_data)
    assert shell.read_result_file(file_path) == test_data

def test_read_mock_with_valid_lba(mocker):
    mocker.patch('shell.call_system', return_value = 0)
    #temp output 파일 생성.
    test_data = '0x99ABCDEF'
    test_filename = get_test_ssd_output_file(data=test_data)
    with patch('builtins.print') as mock_print:
        shell.read(3, filename = test_filename)
        mock_print.assert_called_once_with("[READ] LBA 03 : 0x99ABCDEF")
