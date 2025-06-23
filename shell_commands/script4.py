from shell_command_validator import hex_string_generator
from shell_commands.command import IShellCommand
from logger import LOGGER
from shell_commands.erase_range import ShellEraseRangeCommand
from shell_commands.read import read_compare
from shell_commands.write import ShellWriteCommand


class ShellScript4Command(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = "4_EraseAndWriteAgin"

    def execute(self):
        ShellEraseRangeCommand([0, 2]).execute()
        result = self.read_compare_range(0, 2)
        if result == "FAIL":
            return "FAIL"

        cycle_cnt = 0
        for i in range(2, 100, 2):
            cycle_cnt += 1
            if cycle_cnt > 30: break
            result = self.erase_and_writing_aging_cycle(i, i + 2)
            if result == "FAIL":
                return "FAIL"
        return "PASS"

    def erase_and_writing_aging_cycle(self, start, end):
        ShellWriteCommand([start, hex_string_generator()]).execute()
        ShellWriteCommand([start, hex_string_generator()]).execute()
        ShellEraseRangeCommand([start, end]).execute()
        return self.read_compare_range(start, end)

    def read_compare_range(self, start, end):
        for i in range(start, end+1):
            if "FAIL" == read_compare(i, self.INITIAL_VALUE):
                return "FAIL"
        return "PASS"