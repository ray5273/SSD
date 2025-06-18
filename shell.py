import os
import subprocess

from shell_command_validator import is_valid_command, is_valid_read_command_params, is_valid_write_command_params, \
    is_valid_fullwrite_command_params,TEST_SCRIPT_1,TEST_SCRIPT_3, hex_string_generator

# SSD 테스트에 쓰이는 constants
MAX_LBA = 100


def write(lba, data, output='ssd_output.txt'):
    """write"""
    cmd = f'python ssd.py W {lba} {data}'
    status = call_system(cmd)
    if status >= 0:
        # 잘 써졌는지 결과 확인, SSD에서 write 에러 발생 시에 파일에 ERROR 출력.
        result = read(lba, output)
        if result == "ERROR":
            print(f'[WRITE] Fail')
        else:
            print(f'[WRITE] Done')
        return result
    return "INVALID COMMAND : WRITE"


def call_system(cmd: str):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='UTF-8',
                                check=True)  # or 'euc-kr'
        return result.returncode
    except Exception as e:
        print(f"ssd.py를 호출했으나 오류 발생했습니다 : {e}")
        return -1


def read_result_file(filename):
    line = None
    with open(filename, 'r') as f:  # TODO encoding 확인 필요
        line = f.read()
    return line


def read(lba, filename='ssd_output.txt'):
    status = call_system(f'python ssd.py R {lba}')
    if status >= 0:
        read_data = read_result_file(filename)
        lba = int(lba)
        print(f'[READ] LBA {lba:02d} : {read_data}')


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
        print("fullwrite 에러 발생")


def fullread():
    """
    LBA 0 번부터 MAX_LBA - 1 번 까지 Read 를 수행한다
    ssd 전체 값을 모두 화면에 출력한다
    """
    try:
        for lba in range(MAX_LBA):
            read(lba)
    except:
        print("fullread 에러 발생")

def read_compare(lba, data):
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

def full_write_and_read_compare():
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
        print(f.read().strip())

def read_compare(lba, value):
    return True

def partial_lba_write_2():
    # write()
    return True

def shell():
    """무한 루프 쉘 모드"""
    print("📥 Shell 모드 진입. 'exit' 입력 시 종료됩니다.")
    while True:
        try:
            user_input_list = input("Shell > ").strip().split()

            if len(user_input_list) < 1:
                print("유저가 아무 커맨드도 입력 하지 않았습니다.")
                continue

            command_index, param1_index, param2_index = 0, 1, 2
            command_param = user_input_list[command_index]
            if not is_valid_command(command_param):
                print("INVALID COMMAND")
                continue

            if command_param in ('exit'):
                print("👋 종료합니다.")
                break
            elif command_param == "write":
                # 인자 check 및 에러 처리 필요
                if not is_valid_write_command_params(user_input_list=user_input_list):
                    print("write command parameter가 포맷에 맞지 않습니다.")
                    continue
                lba_str, data_str = user_input_list[param1_index], user_input_list[param2_index]
                write(lba=lba_str, data=data_str)
            elif command_param == "read":
                if not is_valid_read_command_params(user_input_list=user_input_list):
                    print("read command parameter가 포맷에 맞지 않습니다.")
                    continue
                lba_str = user_input_list[param1_index]
                read(lba=lba_str)
            elif command_param == "fullwrite":
                if not is_valid_fullwrite_command_params(user_input_list=user_input_list):
                    print("fullwrite command parameter가 포맷에 맞지 않습니다.")
                    continue
                data_str = user_input_list[param1_index]
                fullwrite(data=data_str)
            elif command_param == "fullread":
                fullread()
            elif TEST_SCRIPT_1.startswith(command_param):
                print(full_write_and_read_compare())
            elif TEST_SCRIPT_3.startswith(command_param):
                print(write_read_aging())
            elif command_param == "help":
                help()
            elif user_input.startswith("2_"):
                partial_lba_write()
            else:
                print("❓ 알 수 없는 명령입니다.")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 종료합니다.")
            break


if __name__ == '__main__':
    shell()

