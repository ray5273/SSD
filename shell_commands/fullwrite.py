from shell_commands.command import IShellCommand
from logger import LOGGER
from shell_commands.write import ShellWriteCommand


class ShellFullWriteCommand(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = 'fullwrite'

    def execute(self):
        """
        모든 LBA 영역에 대해 Write 를 수행한다
        모든 LBA 에 값 0xABCDFFF 가 적힌다

        Usage:
            Shell > fullwrite 0xABCDFFFF
        """
        data = self.params[0]
        try:
            for lba in range(self.MAX_LBA):
                ShellWriteCommand([lba, data]).execute()
        except:
            LOGGER.print_log("fullwrite 에러 발생")