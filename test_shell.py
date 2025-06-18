
import pytest
from pytest_mock import MockerFixture

import shell


def test_shell_read(mocker: MockerFixture):
    mocker.patch('shell.read', return_value='0x99999999')
    result = shell.read("3")
    assert result == "0x99999999"

def test_call_system():
    cmd = f'dir'
    assert shell.call_system(cmd) == 0

@pytest.mark.skip
def test_read_result_file():
    ...

@pytest.mark.skip
def test_read_with_valid_lba():
    ...