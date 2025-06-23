from shell_commands.command import IShellCommand
from logger import LOGGER


class ShellEraseCommand(IShellCommand):
    def __init__(self,  params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = 'erase'

    def execute(self):
        if len(self.params)<2:
            return -1
        lba = self.params[0]
        size = self.params[1]
        direction = 1 if size > 0 else -1
        remaining = abs(size)
        current_lba = lba
        step = 10

        while remaining > 0:
            chunk_size = min(step, remaining)

            if direction > 0:
                actual_lba = current_lba
                upper_bound = actual_lba + chunk_size - 1
                if upper_bound >= self.MAX_LBA:
                    chunk_size = max(0, self.MAX_LBA - actual_lba)
            else:
                actual_lba = current_lba - chunk_size + 1
                if actual_lba < self.MIN_LBA:
                    chunk_size = max(0, current_lba - self.MIN_LBA + 1)
                    actual_lba = self.MIN_LBA

            if chunk_size <= 0:
                break

            status = self._run_in_subprocess(f'python ssd.py E {actual_lba} {chunk_size}')

            if status >= 0:
                # Todo debugging
                LOGGER.print_log(f"[ERASE] E {actual_lba:02} {chunk_size}")
                current_lba += chunk_size * direction
                remaining -= chunk_size
            else:
                LOGGER.print_log("Erase 에러 발생")
                return