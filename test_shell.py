import os
import random
import tempfile
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

import shell
from shell import MAX_LBA


def test_shell_read(mocker: MockerFixture):
    mocker.patch('shell.read', return_value='0x99999999')
    result = shell.read("3")
    assert result == "0x99999999"


def test_call_system():
    cmd = f'dir'
    assert shell.call_system(cmd) == 0


def get_test_ssd_output_file(filename="ssd_output.txt", data='0x00000000'):
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
    mocker.patch('shell.call_system', return_value=0)
    # temp output 파일 생성.
    test_data = '0x99ABCDEF'
    test_filename = get_test_ssd_output_file(data=test_data)
    mock_logger = mocker.patch('shell.LOGGER.print_log')
    shell.read(3, filename=test_filename)
    mock_logger.assert_called_once_with("[READ] LBA 03 : 0x99ABCDEF")


def test_write(mocker):
    # temp output 파일 생성.
    test_data = '0x99ABCDEF'
    test_filename = get_test_ssd_output_file(data=test_data)
    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치
    mocker.patch('shell.call_system', return_value=0)
    shell.write(3, '0x99ABCDEF', test_filename)
    expected_calls = [
        mocker.call('[READ] LBA 03 : 0x99ABCDEF'),
        mocker.call('[WRITE] Done')
    ]
    mock_logger.assert_has_calls(expected_calls)


def test_shell_help(capsys):
    inputs = [
        "help",  # help() 호출
        "exit"  # 종료
    ]

    with patch("builtins.input", side_effect=inputs):
        shell.shell()

    output = capsys.readouterr().out

    assert "팀명" in output
    assert "팀장" in output
    assert "read" in output
    assert "write" in output
    assert "fullread" in output
    assert "fullwrite" in output


def test_fullwrite_success(mocker):
    # Given : write() 함수를 mocking함.
    # test_data에 data를 담아줌
    mock_write = mocker.patch("shell.write")
    test_data = "0xABCD"

    # When : fullwrite(data)를 실행
    shell.fullwrite(test_data)

    # Then : MAX_LBA 만큼 write()가 실행되어야함.
    assert mock_write.call_count == MAX_LBA

    # Then : 각 호출의 파라미터 확인, lba와 test_data가 parameter로 잘 들어갔는지 확인
    expected_lba = 0
    for args_lba, call in enumerate(mock_write.call_args_list):
        assert args_lba == expected_lba  # lba가 0~99 순서대로 들어가는지
        assert call.args[1] == test_data  # data가 올바른지
        expected_lba += 1


@pytest.mark.repeat(100)
def test_fullwrite_error_on_random_write(mocker):
    # Given : fullwrite()의 내부 read() 실행의 랜덤 순서(0 ~ MAX_LBA - 1) 에서 RuntimeError를 발생시킴
    error_lba = random.randint(0, MAX_LBA - 1)

    def side_effect(lba, data):
        if lba == error_lba:
            raise RuntimeError("write error")

    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치
    mocker.patch("shell.write", side_effect=side_effect)

    # When: fullwrite()를 실행하면
    shell.fullwrite("0xABCD")

    # Then: fullwrite 에러 발생 print가 확인되어야함.
    mock_logger.assert_any_call("fullwrite 에러 발생")


def test_fullread_success(mocker):
    # Given : read() 함수 동작을 mocking함.
    mock_read = mocker.patch("shell.read")

    # When : fullread()를 실행
    shell.fullread()

    # Then : MAX_LBA만큼 read()가 실행되어야함.
    assert mock_read.call_count == MAX_LBA

    # Then : 각 lba가 각 순서대로 호출이 되는지 확인
    expected_lba = 0
    for args_lba, call in enumerate(mock_read.call_args_list):
        assert args_lba == expected_lba
        expected_lba += 1


@pytest.mark.repeat(100)
def test_fullread_error_on_random_read(mocker):
    # Given : fullread()의 내부 read() 실행의 랜덤 순서(0 ~ MAX_LBA - 1) 에서 RuntimeError를 발생시킴
    error_lba = random.randint(0, MAX_LBA - 1)

    def side_effect(lba):
        if lba == error_lba:
            raise RuntimeError("write error")

    mocker.patch("shell.read", side_effect=side_effect)
    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치
    # When: fullread()를 실행하면
    shell.fullread()
    # Then: fullread 에러 발생 print가 확인되어야함.
    mock_logger.assert_any_call("fullread 에러 발생")


def test_TestScript1(mocker):
    mock_ssd = {}
    def mock_write(lba, data):
        mock_ssd[lba] = data
    def mock_read(lba):
        return mock_ssd[lba]
    mocker.patch('shell.call_system', return_value=0)
    mocker.patch('shell.write', side_effect = mock_write)
    mocker.patch('shell.read', side_effect=mock_read)
    assert shell.full_write_and_read_compare() == "PASS"

def test_write_read_aging_success(mocker):
    # write는 아무 동작도 하지 않음
    mocker.patch('shell.write')
    # read_compare는 항상 "PASS" 반환
    mocker.patch('shell.read_compare', return_value="PASS")
    assert shell.write_read_aging() == "PASS"

def test_write_read_aging_failure(mocker):
    # write는 아무 동작도 하지 않음
    mocker.patch('shell.write')
    # read_compare는 항상 "PASS" 반환
    mocker.patch('shell.read_compare', return_value="FAIL")
    assert shell.write_read_aging() == "FAIL"


def test_partial_lba_write_2_pass(mocker):
    # write는 아무 동작도 하지 않음
    mocker.patch('shell.write')
    # read_compare는 항상 "PASS" 반환
    mocker.patch('shell.read_compare', return_value="PASS")
    assert shell.partial_lba_write_2() == "PASS"

def test_partial_lba_write_2_fail(mocker):
    # write는 아무 동작도 하지 않음
    mocker.patch('shell.write')
    # read_compare는 항상 "PASS" 반환
    mocker.patch('shell.read_compare', return_value="FAIL")
    assert shell.partial_lba_write_2() == "FAIL"


mock_ssd = {}
def mock_write(lba, data):
    mock_ssd[lba] = data
def mock_read(lba):
    return mock_ssd[lba]
def mock_erase_range(start, end):
    for i in range(start, end+1):
        mock_ssd[i] = shell.INITIAL_VALUE

def test_erase_and_writing_aging(mocker):
    global mock_ssd
    mock_ssd = {}

    mocker.patch('shell.call_system', return_value=0)
    mocker.patch('shell.write', side_effect=mock_write)
    mocker.patch('shell.read', side_effect=mock_read)
    mocker.patch('shell.erase_range', side_effect=mock_erase_range)

    assert shell.erase_and_writing_aging() == 'PASS'

def test_erase_and_writing_aging_cycle(mocker):
    global mock_ssd
    mock_ssd = {}

    mocker.patch('shell.call_system', return_value=0)
    mocker.patch('shell.write', side_effect=mock_write)
    mocker.patch('shell.read', side_effect=mock_read)
    mocker.patch('shell.erase_range', side_effect=mock_erase_range)
    assert shell.erase_and_writing_aging_cycle(0,2) == "PASS"
    assert shell.erase_and_writing_aging_cycle(5, 7) == "PASS"


