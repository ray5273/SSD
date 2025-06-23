

from abc import ABC, abstractmethod
import subprocess
from logger import LOGGER

class IShellCommand(ABC):
    MAX_LBA = 100
    MIN_LBA = 0
    # SSD 테스트에 쓰이는 constants
    INITIAL_VALUE = '0x00000000'
    SUBPROCESS_VALID_STATUS = 0

    def is_valid_status(self, status):
        return status == self.SUBPROCESS_VALID_STATUS

    def __init__(self, params=[], output=None):
        self.command = 'CMD'
        self.params = params
        self.output = output

    def _run_in_subprocess(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8',
                                    check=True)  # or 'euc-kr'
            return result.returncode
        except Exception as e:
            LOGGER.print_log(f"ssd.py를 호출했으나 오류 발생했습니다 : {e}")
            return -1

    @abstractmethod
    def execute(self):
        pass








