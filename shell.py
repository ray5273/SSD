import click
import os
import subprocess

def write(lba, data):
    """write"""
    pass

def read(lba):
    pass
def call_system(cmd:str):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='UTF-8', check=True)  # or 'euc-kr'
    except Exception:
        #TODO : Exception에 대한 처리 없이 오류 발생한 returncode를 리턴하는 것으로 대체.
        ...
    return result.returncode


def read_result_file(filename):
    line = None
    with open(filename, 'r' ) as f: #TODO encoding 확인 필요
        line = f.read()
    return line

def read(lba, filename = 'ssd_output.txt'):
    #TODO lba 범위 확인 & 에러 처리
    status = call_system(f'python ssd.py R {lba}')
    if status >= 0:
        read_data = read_result_file(filename)
        lba=int(lba)
        print(f'[READ] LBA {lba:02d} : {read_data}')

def fullwrite():
    pass

def fullread():
    pass

def help():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(current_dir, "help.txt")

    with open(path, encoding="utf-8") as f:
        click.echo(f.read().strip())

def shell():
    """무한 루프 쉘 모드"""
    click.echo("📥 Shell 모드 진입. 'exit' 입력 시 종료됩니다.")
    while True:
        try:
            user_input = input("Shell > ").strip()
            if user_input in ('exit', 'quit'):
                click.echo("👋 종료합니다.")
                break
            elif user_input.startswith("write"):
                # 인자 check 및 에러 처리 필요
                write.callback(3, 0xAAAABBBB)
            elif user_input.startswith("read"):
                # 인자 check 및 에러 처리 필요
                read.callback(3)
            elif user_input == "fullwrite":
                fullwrite.callback()
            elif user_input == "fullread":
                fullread.callback()
            elif user_input == "help":
                help()
            else:
                click.echo("❓ 알 수 없는 명령입니다.")
        except (KeyboardInterrupt, EOFError):
            click.echo("\n👋 종료합니다.")
            break


if __name__ == '__main__':
        shell()

