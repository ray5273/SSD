import os.path

import pytest
import shell
from shell import Runner
import tempfile

def get_test_batch_script():
    commands = [
        '1_FullWriteAndReadCompare',
        '2_PartialLBAWrite',
        '3_WriteReadAging',
        '4_EraseAndWriteAging',
    ]
    temp_path = tempfile.gettempdir()
    temp_script = 'shell_script.txt'
    fullname = os.path.join(temp_path, temp_script)
    with open(fullname, 'w', encoding='utf-8') as f:
        f.write("\n".join(commands ) )
    return fullname

def get_test_batch_script_with_1_3():
    commands = [
        '1_FullWriteAndReadCompare',
        '2_PartialLBAWrite',
        '3_WriteReadAging',
        # '4_EraseAndWriteAging',
    ]
    temp_path = tempfile.gettempdir()
    temp_script = 'shell_script.txt'
    fullname = os.path.join(temp_path, temp_script)
    with open(fullname, 'w', encoding='utf-8') as f:
        f.write("\n".join(commands ) )
    return fullname

def get_test_batch_script_with_1():
    commands = [
        '1_FullWriteAndReadCompare',
        # '2_PartialLBAWrite',
        # '3_WriteReadAging',
        # '4_EraseAndWriteAging',
    ]
    temp_path = tempfile.gettempdir()
    temp_script = 'shell_script.txt'
    fullname = os.path.join(temp_path, temp_script)
    with open(fullname, 'w', encoding='utf-8') as f:
        f.write("\n".join(commands ) )
    return fullname

def remove_test_batch_script(filename):
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception:
            return False
    return True

def test_create_runner():
    script_name = get_test_batch_script()
    runner = Runner(script_name)
    remove_test_batch_script(script_name)
    assert runner is not None


def test_read_batch_script():
    script_name = get_test_batch_script()
    runner = Runner(script_name)
    runner._read_batch_script()
    remove_test_batch_script(script_name)
    assert len(runner.get_script_list()) != 0

mock_ssd = {}
def mock_write(lba, data, filename=''):
    mock_ssd[lba] = data
def mock_read(lba):
    return mock_ssd[lba]
def mock_erase(lba):
    mock_ssd[lba] = '0x00000000'
def mock_erase_range(start, end):
    for i in range(start, end+1):
        mock_ssd[i] = shell.INITIAL_VALUE

def test_run_shell_command_with_mock_script1(mocker):
    runner = Runner('')
    mocker.patch('shell.Runner.run_shell_command', return_value ="PASS")
    assert runner.run_shell_command("1_FullWriteAndReadCompare") == "PASS"

def test_run_shell_command_with_mock_script4(mocker):
    runner = Runner('')
    mocker.patch('shell.Runner.run_shell_command', return_value="PASS")
    assert runner.run_shell_command("4_EraseAndWriteAging") == "PASS"

def test_run_shell_1_command():
    runner = Runner('')
    assert runner.run_shell_command("1_FullWriteAndReadCompare") == "PASS"

def test_run_shell_4_command():
    runner = Runner('')
    assert runner.run_shell_command("4_EraseAndWriteAging") == "PASS"

def test_run_batch_script():
    runner = Runner(get_test_batch_script())
    assert runner.run() == "PASS"

def test_call_in_cli():
    assert os.system('python shell.py test.txt') < 0
    assert os.system(f'python shell.py {get_test_batch_script_with_1()}') == 0

