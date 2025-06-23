from shell_commands.command import IShellCommand
from shell_commands.read import ShellReadCommand
from logger import LOGGER


class ShellWriteCommand(IShellCommand):
    def __init__(self, params=[], output='ssd_output.txt'):
        super().__init__(params, output)
        self.command = "write"

    def execute(self):
        if len(self.params)<2:
            return -1
        lba = self.params[0]
        data = self.params[1]
        cmd = f'python ssd.py W {lba} {data}'
        status = self._run_in_subprocess(cmd)
        if status == 0:
            LOGGER.print_log(f'[WRITE] Done')
            return
        return "INVALID COMMAND : WRITE"
