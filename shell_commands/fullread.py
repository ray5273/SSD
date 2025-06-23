from shell_commands.command import IShellCommand
from logger import LOGGER
from shell_commands.read import ShellReadCommand


class ShellFullReadCommand(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = 'fullread'

    def execute(self):
        """
            LBA 0 번부터 MAX_LBA - 1 번 까지 Read 를 수행한다
            ssd 전체 값을 모두 화면에 출력한다
            """
        try:
            for lba in range(self.MAX_LBA):
                ShellReadCommand([lba]).execute()
        except:
            LOGGER.print_log("fullread 에러 발생")
