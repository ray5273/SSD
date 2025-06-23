from shell_commands.command import IShellCommand
from logger import LOGGER


class ShellReadCommand(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = "read"

    def execute(self):
        if len(self.params)==0:
            return -1
        lba = self.params[0]
        cmd = f'python ssd.py R {lba}'
        status = self._run_in_subprocess(cmd)
        read_data = None
        if status >= 0:
            read_data = self.read_result_file(self.output)
            lba = int(lba)
            LOGGER.print_log(f'[READ] LBA {lba:02d} : {read_data}')
        return read_data

    def read_result_file(self, output):
        line = None
        with open(output, 'r') as f:  # TODO encoding 확인 필요
            line = f.read()
        return line


def read_compare(lba, data, filename='ssd_output.txt'):
    if ShellReadCommand([lba]).execute() == data:
        return "PASS"
    return "FAIL"