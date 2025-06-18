import os
import subprocess

# SSD 테스트에 쓰이는 constants
MAX_LBA = 100

def validate_lba(lba):
    try:
        nlba = int(lba)
        if not (0 <= nlba < 100):
            return False
    except Exception:
        return False
    return True

def validate_data(data):
    if len(data) > 10:
        return False
    try:
        value = str(data)[2:].lower()
        for ch in value:
            if not ( (ord('a') <= ord(ch) <= ord('f')) or (ord('0') <= ord(ch) <= ord('9')) ):
                return False
    except Exception:
        return False
    return True


def write(lba, data, output='ssd_output.txt'):
    """write"""
    if not validate_lba(lba):
        print("INVALID COMMAND : INVALID LBA")
        return

    if not validate_data(data):
        print("INVALID COMMAND : DATA")
        return

    cmd = f'python ssd.py W {lba} {data}'
    status = call_system(cmd)
    if status >= 0:
        #잘 써졌는지 결과 확인, SSD에서 write 에러 발생 시에 파일에 ERROR 출력.
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
    except Exception:
        # TODO : Exception에 대한 처리 없이 오류 발생한 returncode를 리턴하는 것으로 대체.
        ...
    return result.returncode


def read_result_file(filename):
    line = None
    with open(filename, 'r') as f:  # TODO encoding 확인 필요
        line = f.read()
    return line


def read(lba, filename='ssd_output.txt'):
    # TODO lba 범위 확인 & 에러 처리
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


def help():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(current_dir, "help.txt")

    with open(path, encoding="utf-8") as f:
        print(f.read().strip())


def shell():
    """무한 루프 쉘 모드"""
    print("📥 Shell 모드 진입. 'exit' 입력 시 종료됩니다.")
    while True:
        try:
            user_input = input("Shell > ").strip()
            if user_input in ('exit', 'quit'):
                print("👋 종료합니다.")
                break
            elif user_input.startswith("write"):
                # 인자 check 및 에러 처리 필요
                write(3, 0xAAAABBBB)
            elif user_input.startswith("read"):
                # 인자 check 및 에러 처리 필요
                read(3)
            elif user_input.startswith("fullwrite"):
                data = user_input.split()[1]
                fullwrite(data)
            elif user_input.startswith("fullread"):
                fullread()
            elif user_input == "help":
                help()
            else:
                print("❓ 알 수 없는 명령입니다.")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 종료합니다.")
            break


if __name__ == '__main__':
    shell()
