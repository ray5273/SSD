import pytest
from buffer_driver import BufferDriver
import os

@pytest.fixture
def buffer_driver():
    return BufferDriver()


def test_make_empty_list(buffer_driver):
    assert  os.path.isfile(os.path.join('buffer_folder','1_empty'))

def test_get_list_from_buffer_empty_files(buffer_driver):
    list = []
    buffer_driver.make_buffer_files_from_list(list)
    assert buffer_driver.get_list_from_buffer_files() == []

def test_get_list_from_buffer_command_files(buffer_driver):
    command = ('W','0','0x00000000')
    list = [command]
    buffer_driver.make_buffer_files_from_list(list)
    assert buffer_driver.get_list_from_buffer_files() == [('W',0,'0x00000000')]

def test_get_list_from_buffer_command_files2(buffer_driver):
    command1 = ('W','0','0x00000001')
    command2 = ('W','0','0x00000002')
    list = [command1, command2]
    buffer_driver.make_buffer_files_from_list(list)
    assert buffer_driver.get_list_from_buffer_files() == [('W',0,'0x00000001'),('W',0,'0x00000002')]


def test_make_list_to_buffer_file_fail(buffer_driver):
    command1 = ('W','0','0x00000001')
    command2 = ('W','0','0x00000002')
    command3 = ('W','0','0x00000003')
    command4 = ('W','0','0x00000004')
    command5 = ('W','0','0x00000005')
    command6 = ('W','0','0x00000006')
    list = [command1, command2,command3,command4,command5,command6]

    assert buffer_driver.make_buffer_files_from_list(list) == None
def test_delete_buffer_files(buffer_driver):
    buffer_driver.delete_buffer_files()
    assert not os.path.isfile(os.path.join('buffer_folder','1_empty'))
