
from shell_command_validator import hex_string_generator
from shell_commands.command import IShellCommand
from logger import LOGGER
from shell_commands.read import read_compare
from shell_commands.write import ShellWriteCommand


class ShellScript2Command(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = "2_PartialLBAWrite"

    def execute(self):
        lba_lst = [4, 0, 3, 1, 2]
        data = hex_string_generator()
        for _ in range(30):
            for lba in lba_lst:
                ShellWriteCommand([lba, data], self.output).execute()

            for lba in [0, 1, 2, 3, 4]:
                if read_compare(lba, data, self.output) == "FAIL":
                    return "FAIL"
        return "PASS"
