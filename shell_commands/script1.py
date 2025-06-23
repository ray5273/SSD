from shell_commands.command import IShellCommand
from logger import LOGGER
from shell_commands.read import read_compare
from shell_commands.write import ShellWriteCommand


class ShellScript1Command(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = "1_FullWriteAndReadCompare"

    def execute(self):
        data = {}
        for idx, i in enumerate(range(0x00000001, 0x00000101), start=0):
            data[idx] = f"0x{i:08X}"

        step = 5
        for i in range(0, 100, step):
            result = self.write_and_read_compare_in_range(data, i, i + step)
            if result == "FAIL":
                return result

        return "PASS"

    def write_and_read_compare_in_range(self, data, start, end):
        for i in range(start,end):
            ShellWriteCommand([i, data[i]]).execute()
        for i in range(start,end):
            result = read_compare(i, data[i])
            if result == 'FAIL':
                return result
        return 'PASS'
