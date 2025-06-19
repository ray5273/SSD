import os.path

import pytest
from shell import *
import tempfile

def get_test_batch_script():
    commands = [
        'write 3 0xABCDEF12',
        'read 3'
        'erase 3'
        'flush'
        '1_FullWriteAndReadCompare'
        '2_PartialLBAWrite'
        '3_WriteReadAging'
        '4_EraseAndWriteAging'
    ]
    temp_path = tempfile.gettempdir()
    temp_script = 'shell_script.txt'
    fullname = os.path.join(temp_path, temp_script)
    with open(fullname, 'w', encoding='utf-8') as f:
        f.writelines(commands)
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


def test_run_shell_command():
    script_name = get_test_batch_script()
    runner = Runner(script_name)
    assert runner.run_shell_command() == "PASS"
