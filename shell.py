import sys

import os
import subprocess
from logger import LOGGER, LATEST_FILE, MAX_BYTES

from shell_command_validator import is_valid_command, is_valid_read_command_params, is_valid_write_command_params, is_valid_erase_command_params, \
    is_valid_fullwrite_command_params,TEST_SCRIPT_1,TEST_SCRIPT_2,TEST_SCRIPT_3, TEST_SCRIPT_4, hex_string_generator
from shell_commands.erase import ShellEraseCommand
from shell_commands.erase_range import ShellEraseRangeCommand
from shell_commands.fullread import ShellFullReadCommand
from shell_commands.fullwrite import ShellFullWriteCommand
from shell_commands.read import ShellReadCommand, read_compare
from shell_commands.script1 import ShellScript1Command
from shell_commands.script2 import ShellScript2Command
from shell_commands.script3 import ShellScript3Command
from shell_commands.script4 import ShellScript4Command
from shell_commands.write import ShellWriteCommand

SUBPROCESS_VALID_STATUS = 0

def is_valid_status(status):
    return status == SUBPROCESS_VALID_STATUS

def flush():
    status = call_system(f'python ssd.py F')
    if is_valid_status(status):
        LOGGER.print_log(f'[FLUSH]')
        return True
    return False

def help():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(current_dir, "help.txt")

    with open(path, encoding="utf-8") as f:
        LOGGER.print_log(f.read().strip())

def shell():
    """무한 루프 쉘 모드"""
    LOGGER.print_log("📥 Shell 모드 진입. 'exit' 입력 시 종료됩니다.")
    while True:
        try:
            user_input_list = input("Shell > ").strip().split()

            if len(user_input_list) < 1:
                LOGGER.print_log("유저가 아무 커맨드도 입력 하지 않았습니다.")
                continue

            command_index, param1_index, param2_index = 0, 1, 2
            command_param = user_input_list[command_index]
            if not is_valid_command(command_param):
                LOGGER.print_log("INVALID COMMAND")
                continue

            if command_param in ('exit'):
                LOGGER.print_log("👋 종료합니다.")
                break
            elif command_param == "write":
                # 인자 check 및 에러 처리 필요
                if not is_valid_write_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("write command parameter가 포맷에 맞지 않습니다.")
                    continue
                lba_str, data_str = user_input_list[param1_index], user_input_list[param2_index]
                ShellWriteCommand([lba_str, data_str]).execute()
            elif command_param == "read":
                if not is_valid_read_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("read command parameter가 포맷에 맞지 않습니다.")
                    continue
                lba_str = user_input_list[param1_index]
                ShellReadCommand( [lba_str]).execute()
            elif command_param == "fullwrite":
                if not is_valid_fullwrite_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("fullwrite command parameter가 포맷에 맞지 않습니다.")
                    continue
                data_str = user_input_list[param1_index]
                ShellFullWriteCommand( [data_str]).execute()
            elif command_param == "fullread":
                ShellFullReadCommand().execute()
            elif command_param == "flush":
                flush()
            elif command_param == "erase":
                if not is_valid_erase_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("erase command parameter가 포맷에 맞지 않습니다.")
                    continue
                lba_str, size_str =  user_input_list[param1_index], user_input_list[param2_index]
                ShellEraseCommand( [int(lba_str), int(size_str)]).execute()
            elif command_param == "erase_range":
                if not is_valid_erase_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("erase range command parameter가 맞지 않습니다.")
                    continue
                lba_start_str, lba_end_str =  user_input_list[param1_index], user_input_list[param2_index]
                ShellEraseRangeCommand( [int(lba_start_str), int(lba_end_str)]).execute()
            elif TEST_SCRIPT_1.startswith(command_param):
                LOGGER.print_log(ShellScript1Command().execute())
            elif TEST_SCRIPT_2.startswith(command_param):
                LOGGER.print_log(ShellScript2Command().execute())
            elif TEST_SCRIPT_3.startswith(command_param):
                LOGGER.print_log(ShellScript3Command().execute())
            elif TEST_SCRIPT_4.startswith(command_param):
                LOGGER.print_log(ShellScript4Command().execute())
            elif command_param == "help":
                help()
            else:
                LOGGER.print_log("❓ 알 수 없는 명령입니다.")
        except (KeyboardInterrupt, EOFError):
            LOGGER.print_log("\n👋 종료합니다.")
            break

def is_runner_script_file(filename):
    return os.path.exists(filename)


class Runner():
    def __init__(self, batch_script):
        self.batch_script = batch_script
        self.script_list : list = []
        self._read_batch_script()

    def _read_batch_script(self):
        lines = None
        try:
            with open(self.batch_script, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            self.script_list = [ item.strip() for item in lines]
        except Exception:
            self.script_list = []

    def run(self):
        for script in self.script_list:
            LOGGER.print_always(f'{script} ___ Run...', end='')
            result = self.run_shell_command(script)
            LOGGER.print_always(f'{result}')
            if result != "PASS": return result
        return "PASS"

    def get_script_list(self):
        return self.script_list

    def run_shell_command(self, script):
        result = "FAIL"
        if TEST_SCRIPT_1.startswith(script):
            result = ShellScript1Command().execute()
        elif TEST_SCRIPT_2.startswith(script):
            result = ShellScript2Command().execute()
        elif TEST_SCRIPT_3.startswith(script):
            result = ShellScript3Command().execute()
        elif TEST_SCRIPT_4.startswith(script):
            result = ShellScript4Command().execute()
        else:
            return "FAIL"
        return result


def run_batch_script(script_name):
    if is_runner_script_file(script_name):
        runner = Runner(script_name)
        return runner.run()
    else:
        LOGGER.print_log(f"INVALID COMMAND : BATCH SCRIPT IS NOT EXIST : {script_name}")
        return "FAIL"

if __name__ == '__main__':
    command = sys.argv[0]
    if len(sys.argv) == 2:
        LOGGER.update_settings(is_stdout=False,file_path=LATEST_FILE, max_bytes=MAX_BYTES)
        if "PASS" != run_batch_script(sys.argv[1]):
            sys.exit(-1)
    else:
        shell()
