from shell_commands.command import IShellCommand
from logger import LOGGER


class ShellEraseRangeCommand(IShellCommand):
    def __init__(self, params=[], output='ssd_output.txt'):
        super().__init__( params, output)
        self.command = 'erase_range'

    def execute(self):
        """
            SSD erase 요청을 Start LBA ~ End LBA 범위에 대해 10 단위로 수행합니다.
            E 명령의 size는 항상 양수입니다.
            유효한 LBA 범위는 0 ~ 99 입니다.
            Start LBA > End LBA인 경우 자동으로 보정합니다.
            """
        # start > end 이면 교환
        lba_start = self.params[0]
        lba_end = self.params[1]
        if lba_start > lba_end:
            lba_start, lba_end = lba_end, lba_start

        # LBA 범위 보정
        if lba_start < self.MIN_LBA:
            lba_start = self.MIN_LBA
        if lba_end >= self.MAX_LBA:
            lba_end = self.MAX_LBA - 1

        current_lba = lba_start
        total_size = lba_end - lba_start + 1
        remaining = total_size
        step = 10

        while remaining > 0:
            chunk_size = min(step, remaining)

            status = self._run_in_subprocess(f'python ssd.py E {current_lba} {chunk_size}')

            if status >= 0:
                # Todo debugging
                LOGGER.print_log(f"[ERASE] E {current_lba:02} {chunk_size}")
                current_lba += chunk_size
                remaining -= chunk_size
            else:
                LOGGER.print_log("Erase 에러 발생")
                return