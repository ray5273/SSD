from shell_command_validator import hex_string_generator
from shell_commands.command import IShellCommand
from logger import LOGGER
from shell_commands.read import read_compare
from shell_commands.write import ShellWriteCommand


class ShellScript3Command(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = "3_WriteReadAging"

    def execute(self):
        """
            Test script 3을 실행하고 결과를 출력합니다.
            :return:
                string: pass 혹은 fail 여부를 출력합니다.
            """
        for i in range(200):
            target_data = hex_string_generator()
            ShellWriteCommand([0, target_data]).execute()
            ShellWriteCommand([99, target_data]).execute()
            if read_compare(0, target_data) == "FAIL":
                return "FAIL"
            if read_compare(99, target_data) == "FAIL":
                return "FAIL"
        return "PASS"
