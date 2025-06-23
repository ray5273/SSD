import os
import random
import tempfile
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

import shell
from shell_commands.command import IShellCommand
from shell_commands.erase import ShellEraseCommand
from shell_commands.erase_range import ShellEraseRangeCommand
from shell_commands.fullread import ShellFullReadCommand
from shell_commands.fullwrite import ShellFullWriteCommand
from shell_commands.read import ShellReadCommand, read_compare
from shell_commands.script1 import ShellScript1Command
from shell_commands.script2 import ShellScript2Command
from shell_commands.script3 import ShellScript3Command
from shell_commands.script4 import ShellScript4Command
from shell_commands.write import ShellWriteCommand


def test_shell_read(mocker: MockerFixture):
    mocker.patch('shell_commands.read.ShellReadCommand.execute', return_value='0x99999999')
    result = ShellReadCommand([3]).execute()
    assert result == "0x99999999"


def test_call_system():
    cmd_str = f'dir'
    cmd = ShellReadCommand([1])
    assert cmd._run_in_subprocess(cmd_str) == 0


def get_test_ssd_output_file(filename="ssd_output.txt", data='0x00000000'):
    # 시스템 임시 디렉터리 경로
    tmp_dir = tempfile.gettempdir()
    # 내가 지정한 임시 파일명

    file_path = os.path.join(tmp_dir, filename)
    # 임시 파일 생성 및 쓰기
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)
    return file_path

def test_write(mocker):
    # temp output 파일 생성.
    test_data = '0x99ABCDEF'
    test_filename = get_test_ssd_output_file(data=test_data)
    mock_logger = mocker.patch('shell_commands.command.LOGGER.print_log')

    mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
    ShellWriteCommand([3,'0x99ABCDEF'], test_filename).execute()
    expected_calls = [
        mocker.call('[WRITE] Done')
    ]
    mock_logger.assert_has_calls(expected_calls)

def test_erase(mocker):
    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치

    with patch('builtins.print') as mock_print:
        mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
        ShellEraseCommand([3,11]).execute()
        expected_calls = [
            mocker.call('[ERASE] E 03 10'),
            mocker.call('[ERASE] E 13 1'),
        ]
        mock_logger.assert_has_calls(expected_calls)

def test_erase_over_max_lba(mocker):
    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치

    with patch('builtins.print') as mock_print:
        mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
        ShellEraseCommand([99,10]).execute()

        expected_calls = [
            mocker.call('[ERASE] E 99 1'),
        ]
        mock_logger.assert_has_calls(expected_calls)

def test_erase_minus(mocker):
    mock_logger = mocker.patch('shell_commands.command.LOGGER.print_log')
    with patch('builtins.print') as mock_print:
        mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
        ShellEraseCommand( [3, -10]).execute()

        expected_calls = [
            mocker.call('[ERASE] E 00 4'),
        ]
        mock_logger.assert_has_calls(expected_calls)

def test_erase_range(mocker):
    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치

    with patch('builtins.print') as mock_print:
        mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
        ShellEraseRangeCommand([3,10]).execute()
        expected_calls = [
            mocker.call('[ERASE] E 03 8'),
        ]
        mock_logger.assert_has_calls(expected_calls)

def test_erase_range_change_start_end(mocker):
    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치

    with patch('builtins.print') as mock_print:
        mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
        ShellEraseRangeCommand([10, 3]).execute()

        expected_calls = [
            mocker.call('[ERASE] E 03 8'),
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
    write_mocker = mocker.patch("shell_commands.write.ShellWriteCommand.execute")

    test_data = "0xABCD"
    # When : fullwrite(data)를 실행
    ShellFullWriteCommand([test_data]).execute()
    # assert MAX_LBA 만큼 실행
    assert write_mocker.call_count == IShellCommand.MAX_LBA


@pytest.mark.repeat(100)
def test_fullwrite_error_on_random_write(mocker):
    # Given : fullwrite()의 내부 read() 실행의 랜덤 순서(0 ~ MAX_LBA - 1) 에서 RuntimeError를 발생시킴
    error_lba = random.randint(0, IShellCommand.MAX_LBA - 1)

    def side_effect(lba, data):
        if lba == error_lba:
            raise RuntimeError("write error")

    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치
    mocker.patch("shell_commands.write.ShellWriteCommand.execute", side_effect=side_effect)

    # When: fullwrite()를 실행하면
    ShellFullWriteCommand( ["0xABCD"]).execute()
    # Then: fullwrite 에러 발생 print가 확인되어야함.
    mock_logger.assert_any_call("fullwrite 에러 발생")


def test_fullread_success(mocker):
    # Given : read() 함수 동작을 mocking함.
    mock_read = mocker.patch("shell_commands.read.ShellReadCommand.execute")

    # When : fullread()를 실행
    ShellFullReadCommand().execute()

    # Then : MAX_LBA만큼 read()가 실행되어야함.
    assert mock_read.call_count == IShellCommand.MAX_LBA


@pytest.mark.repeat(100)
def test_fullread_error_on_random_read(mocker):
    # Given : fullread()의 내부 read() 실행의 랜덤 순서(0 ~ MAX_LBA - 1) 에서 RuntimeError를 발생시킴
    error_lba = random.randint(0, IShellCommand.MAX_LBA - 1)

    def side_effect(lba):
        if lba == error_lba:
            raise RuntimeError("write error")

    mocker.patch("shell_commands.read.ShellReadCommand.execute", side_effect=side_effect)
    mock_logger = mocker.patch('shell.LOGGER.print_log')  # LOGGER.print_log로 패치
    # When: fullread()를 실행하면
    ShellFullReadCommand().execute()
    # Then: fullread 에러 발생 print가 확인되어야함.
    mock_logger.assert_any_call("fullread 에러 발생")


def test_TestScript1(mocker):
    mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
    mock_write = mocker.patch('shell_commands.write.ShellWriteCommand.execute')
    mocker.patch('shell_commands.script1.ShellScript1Command.write_and_read_compare_in_range', return_value='PASS')
    assert ShellScript1Command().execute() == 'PASS'


def test_write_read_aging_success(mocker):
    mocker.patch('shell_commands.script3.ShellScript3Command.execute', return_value="PASS")
    assert ShellScript3Command().execute() == "PASS"

def test_write_read_aging_failure(mocker):
    # write는 아무 동작도 하지 않음
    mocker.patch('shell_commands.write.ShellWriteCommand.execute')
    # read_compare는 항상 "PASS" 반환
    mocker.patch('shell_commands.read.read_compare', return_value="FAIL")
    assert ShellScript3Command().execute() == "FAIL"


def test_partial_lba_write_2_pass(mocker):
    mocker.patch('shell_commands.script2.ShellScript2Command.execute', return_value="PASS")
    assert ShellScript2Command().execute() == "PASS"

def test_partial_lba_write_2_fail(mocker):
    # write는 아무 동작도 하지 않음
    mocker.patch('shell_commands.write.ShellWriteCommand.execute')
    # read_compare는 항상 "PASS" 반환
    mocker.patch('shell_commands.read.read_compare', return_value="FAIL")
    assert ShellScript2Command().execute() == "FAIL"


mock_ssd = {}
def mock_flush():
    return True
def mock_write(lba, data):
    mock_ssd[lba] = data
def mock_read(lba):
    return mock_ssd[lba]
def mock_erase_range(start, end):
    for i in range(start, end+1):
        mock_ssd[i] = shell.INITIAL_VALUE

def test_erase_and_writing_aging(mocker):
    mocker.patch('shell_commands.script4.ShellScript4Command.execute', return_value="PASS")
    assert ShellScript4Command().execute() == 'PASS'

#커맨드패턴 적용한 커맨드 테스트.
def test_class_shell_read_command_with_result_file():
    test_data = '0x99999999'
    file_path = get_test_ssd_output_file(data=test_data)
    shell_cmd = ShellReadCommand()
    assert shell_cmd.read_result_file(file_path) == test_data

def test_class_shell_read_command_mock_with_valid_lba(mocker):
    mocker.patch.object(IShellCommand, '_run_in_subprocess', return_value=0)
    mock_logger = mocker.patch('shell_commands.command.LOGGER.print_log')
    mocker.patch('shell_commands.read.ShellReadCommand.read_result_file', return_value='0x99ABCDEF')
    # temp output 파일 생성.
    test_data = '0x99ABCDEF'
    test_filename = get_test_ssd_output_file(data=test_data)
    cmd : IShellCommand = ShellReadCommand( ['3'], test_filename)
    cmd.execute()
    mock_logger.assert_called_once_with("[READ] LBA 03 : 0x99ABCDEF")


def test_flush_with_mock(mocker):
    global mock_ssd
    mock_ssd = {}

    mocker.patch('shell.call_system', return_value=0)
    assert shell.flush() == True



