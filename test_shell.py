
import os
from unittest.mock import patch

import pytest
import os
import tempfile

from shell import help, shell
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

def test_write(mocker):
    # temp output 파일 생성.
    test_data = '0x99ABCDEF'
    test_filename = get_test_ssd_output_file(data=test_data)
    with patch('builtins.print') as mock_print:
        mocker.patch('shell.call_system', return_value=0)
        shell.write(3, '0x99ABCDEF', test_filename)
        expected_calls = [
            mocker.call('[READ] LBA 03 : 0x99ABCDEF'),
            mocker.call('[WRITE] Done')
        ]
        mock_print.assert_has_calls(expected_calls)


def test_write_with_invalid_lba(mocker):
    test_data = '0x99ABCDEF'
    with patch('builtins.print') as mock_print:
        mocker.patch('shell.call_system', return_value=0)
        shell.write(999, test_data)
        expected_calls = [
            mocker.call('INVALID COMMAND : INVALID LBA')
        ]
        mock_print.assert_has_calls(expected_calls)

def test_write_with_invalid_data(mocker):
    #data 길이가 자릿수 초과
    test_data = '0x99ABCDEFAAAA'
    with patch('builtins.print') as mock_print:
        mocker.patch('shell.call_system', return_value=0)
        shell.write(99, test_data)
        expected_calls = [
            mocker.call('INVALID COMMAND : DATA')
        ]
        mock_print.assert_has_calls(expected_calls)

    #data 범위 초과
    test_data = '0x99ABCDXX'
    with patch('builtins.print') as mock_print:
        mocker.patch('shell.call_system', return_value=0)
        shell.write(99, test_data)
        expected_calls = [
            mocker.call('INVALID COMMAND : DATA')
        ]
        mock_print.assert_has_calls(expected_calls)


def test_shell_help(capsys):
    inputs = [
        "help",       # help() 호출
        "exit"        # 종료
    ]

    with patch("builtins.input", side_effect=inputs):
        shell()

    output = capsys.readouterr().out

    assert "팀명" in output
    assert "팀장" in output
    assert "read" in output
    assert "write" in output
    assert "fullread" in output
    assert "fullwrite" in output
