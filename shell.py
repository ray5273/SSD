import click
import os
import subprocess
from logger import LOGGER

from shell_command_validator import is_valid_command, is_valid_read_command_params, is_valid_write_command_params, is_valid_erase_command_params, \
    is_valid_fullwrite_command_params,TEST_SCRIPT_1,TEST_SCRIPT_2,TEST_SCRIPT_3, TEST_SCRIPT_4, hex_string_generator

# SSD 테스트에 쓰이는 constants
MAX_LBA = 100
MIN_LBA = 0
INITIAL_VALUE = '0x00000000'

def write(lba, data, output='ssd_output.txt'):
    """write"""
    cmd = f'python ssd.py W {lba} {data}'
    status = call_system(cmd)
    if status >= 0:
        # 잘 써졌는지 결과 확인, SSD에서 write 에러 발생 시에 파일에 ERROR 출력.
        result = read(lba, output)
        if result == "ERROR":
            LOGGER.print_log(f'[WRITE] Fail')
        else:
            LOGGER.print_log(f'[WRITE] Done')
        return result
    return "INVALID COMMAND : WRITE"


def call_system(cmd: str):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='UTF-8',
                                check=True)  # or 'euc-kr'
        return result.returncode
    except Exception as e:
        LOGGER.print_log(f"ssd.py를 호출했으나 오류 발생했습니다 : {e}")
        return -1


def read_result_file(filename):
    line = None
    with open(filename, 'r') as f:  # TODO encoding 확인 필요
        line = f.read()
    return line


def read(lba, filename='ssd_output.txt'):
    status = call_system(f'python ssd.py R {lba}')
    read_data = None
    if status >= 0:
        read_data = read_result_file(filename)
        lba=int(lba)
        LOGGER.print_log(f'[READ] LBA {lba:02d} : {read_data}')
    return read_data


def fullwrite(data):
    """
    모든 LBA 영역에 대해 Write 를 수행한다
    모든 LBA 에 값 0xABCDFFF 가 적힌다

    Usage:
        Shell > fullwrite 0xABCDFFFF
    """
    try:
        for lba in range(MAX_LBA):
            write(lba, data)
    except:
        LOGGER.print_log("fullwrite 에러 발생")


def fullread():
    """
    LBA 0 번부터 MAX_LBA - 1 번 까지 Read 를 수행한다
    ssd 전체 값을 모두 화면에 출력한다
    """
    try:
        for lba in range(MAX_LBA):
            read(lba)
    except:
        LOGGER.print_log("fullread 에러 발생")

def erase(lba:int, size:int):
    """
    SSD erase 요청을 내부적으로 10단위로 나누어 처리합니다.
    size가 음수이면 역방향으로 처리하되, 실제 E 명령에 들어가는 size는 항상 양수입니다.
    유효한 LBA 범위는 0~99로 제한됩니다.
    """


    direction = 1 if size > 0 else -1
    remaining = abs(size)
    current_lba = lba
    step = 10

    while remaining > 0:
        chunk_size = min(step, remaining)

        if direction > 0:
            actual_lba = current_lba
            upper_bound = actual_lba + chunk_size - 1
            if upper_bound >= MAX_LBA:
                chunk_size = max(0, MAX_LBA - actual_lba)
        else:
            actual_lba = current_lba - chunk_size + 1
            if actual_lba < MIN_LBA:
                chunk_size = max(0, current_lba - MIN_LBA + 1)
                actual_lba = MIN_LBA

        if chunk_size <= 0:
            break

        status = call_system(f'python ssd.py E {actual_lba} {chunk_size}')

        if status >= 0:
            # Todo debugging
            LOGGER.print_log(f"[ERASE] E {actual_lba:02} {chunk_size}")
            current_lba += chunk_size * direction
            remaining -= chunk_size
        else:
            LOGGER.print_log("Erase 에러 발생")
            return



def erase_range(lba_start: int, lba_end: int):
    """
    SSD erase 요청을 Start LBA ~ End LBA 범위에 대해 10 단위로 수행합니다.
    E 명령의 size는 항상 양수입니다.
    유효한 LBA 범위는 0 ~ 99 입니다.
    Start LBA > End LBA인 경우 자동으로 보정합니다.
    """
    # start > end 이면 교환
    if lba_start > lba_end:
        lba_start, lba_end = lba_end, lba_start

    # LBA 범위 보정
    if lba_start < MIN_LBA:
        lba_start = MIN_LBA
    if lba_end >= MAX_LBA:
        lba_end = MAX_LBA - 1

    current_lba = lba_start
    total_size = lba_end - lba_start + 1
    remaining = total_size
    step = 10

    while remaining > 0:
        chunk_size = min(step, remaining)

        status = call_system(f'python ssd.py E {current_lba} {chunk_size}')

        if status >= 0:
            # Todo debugging
            LOGGER.print_log(f"[ERASE] E {current_lba:02} {chunk_size}")
            current_lba += chunk_size
            remaining -= chunk_size
        else:
            LOGGER.print_log("Erase 에러 발생")
            return



def read_compare(lba, data, filename='ssd_output.txt'):
    if read(lba) == data:
        return "PASS"
    return "FAIL"

def write_and_read_compare_in_range(data, start, end):
    for i in range(start,end):
        write(i, data[i])
    for i in range(start,end):
        result = read_compare(i, data[i])
        if result == 'FAIL':
            return result
    return 'PASS'

def full_write_and_read_compare(output='ssd_output.txt'):
    data = {}
    for idx, i in enumerate(range(0x00000001, 0x00000101), start=0):
        data[idx] = f"0x{i:08X}"

    step = 5
    for i in range(0, 100, step):
        result = write_and_read_compare_in_range(data, i, i+step)
        if result =="FAIL":
            return result

    return "PASS"

def write_read_aging():
    """
    Test script 3을 실행하고 결과를 출력합니다.
    :return:
        string: pass 혹은 fail 여부를 출력합니다.
    """
    for i in range(200):
        target_data = hex_string_generator()
        write(0,target_data)
        write(99,target_data)
        if read_compare(0,target_data) == "FAIL":
            return "FAIL"
        if read_compare(99,target_data) == "FAIL":
            return "FAIL"
    return "PASS"

def help():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(current_dir, "help.txt")

    with open(path, encoding="utf-8") as f:
        LOGGER.print_log(f.read().strip())


def partial_lba_write_2(filename='ssd_output.txt', data='0xAAAABBBB'):

    lba_lst = [4,0,3,1,2]

    for _ in range(30):
        for lba in lba_lst:
            write(lba, data, filename)

        for lba in [0,1,2,3,4]:
            if read_compare(lba, data, filename) == "FAIL":
                return "FAIL"
    return "PASS"


def read_compare_range(start, end):
    for i in range(start, end+1):
        if "FAIL" == read_compare(i, INITIAL_VALUE):
            return "FAIL"
    return "PASS"


def erase_and_writing_aging_cycle(start, end):
    write(start, hex_string_generator())
    write(start, hex_string_generator())
    erase_range(start ,end)
    return read_compare_range(start, end)

def erase_and_writing_aging():

    erase_range(0,2)
    result = read_compare_range(0,2)
    if result == "FAIL":
        return "FAIL"

    cycle_cnt = 0
    for i in range(2, 100, 2):
        cycle_cnt+=1
        if cycle_cnt > 30: break
        result = erase_and_writing_aging_cycle(i, i+2)
        if result == "FAIL":
            return "FAIL"
    return "PASS"

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
                write(lba=lba_str, data=data_str)
            elif command_param == "read":
                if not is_valid_read_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("read command parameter가 포맷에 맞지 않습니다.")
                    continue
                lba_str = user_input_list[param1_index]
                read(lba=lba_str)
            elif command_param == "fullwrite":
                if not is_valid_fullwrite_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("fullwrite command parameter가 포맷에 맞지 않습니다.")
                    continue
                data_str = user_input_list[param1_index]
                fullwrite(data=data_str)
            elif command_param == "fullread":
                fullread()
            elif command_param == "erase":
                if not is_valid_erase_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("erase command parameter가 포맷에 맞지 않습니다.")
                    continue
                lba_str, size_str =  user_input_list[param1_index], user_input_list[param2_index]
                erase(lba=int(lba_str), size=int(size_str))
            elif command_param == "erase_range":
                if not is_valid_erase_command_params(user_input_list=user_input_list):
                    LOGGER.print_log("erase range command parameter가 맞지 않습니다.")
                    continue
                lba_start_str, lba_end_str =  user_input_list[param1_index], user_input_list[param2_index]
                erase_range(lba_start=int(lba_start_str), lba_end=int(lba_end_str))
            elif TEST_SCRIPT_1.startswith(command_param):
                LOGGER.print_log(full_write_and_read_compare())
            elif TEST_SCRIPT_2.startswith(command_param):
                LOGGER.print_log(partial_lba_write_2())
            elif TEST_SCRIPT_3.startswith(command_param):
                LOGGER.print_log(write_read_aging())
            elif TEST_SCRIPT_4.startswith(command_param):
                LOGGER.print_log(erase_and_writing_aging())
            elif command_param == "help":
                help()
            else:
                LOGGER.print_log("❓ 알 수 없는 명령입니다.")
        except (KeyboardInterrupt, EOFError):
            LOGGER.print_log("\n👋 종료합니다.")
            break


if __name__ == '__main__':
    shell()
