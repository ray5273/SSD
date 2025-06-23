from shell_commands.command import IShellCommand
from logger import LOGGER


class ShellFlushCommand(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = "flush"

    def execute(self):
        status = self._run_in_subprocess(f'python ssd.py F')
        if self.is_valid_status(status):
            LOGGER.print_log(f'[FLUSH]')
            return True
        return False