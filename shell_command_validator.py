import random
import re
from logger import LOGGER

MAX_LBA = 100
TEST_SCRIPT_1 = "1_FullWriteAndReadCompare"
TEST_SCRIPT_2 = "2_PartialLBAWrite"
TEST_SCRIPT_3 = "3_WriteReadAging"
TEST_SCRIPT_4 = "4_EraseAndWriteAging"


def is_valid_read_command_params(user_input_list: list[str]) -> bool:
    # read param은 2개여야함. (커맨드 포함)
    if len(user_input_list) != 2:
        LOGGER.print_log(f"파라미터 갯수가 올바르지 않습니다: {len(user_input_list)}")
        return False
    # 2번째 param은 숫자여야하고, 범위가 MAX_LBA 미만이어야함.
    lba_str = user_input_list[1]
    if not is_valid_lba(lba_str):
        LOGGER.print_log("lba가 valid 하지 않습니다.")
        return False
    return True


def is_valid_write_command_params(user_input_list: list[str]) -> bool:
    # write param은 3개여야함. (커맨드 포함)
    if len(user_input_list) != 3:
        LOGGER.print_log(f"파라미터 갯수가 올바르지 않습니다: {len(user_input_list)}")
        return False

    # 2번째 param은 숫자여야하고, 범위가 MAX_LBA 미만이어야함.
    lba_str = user_input_list[1]
    if not is_valid_lba(lba_str):
        LOGGER.print_log("lba가 valid 하지 않습니다.")
        return False

    # 3번째 param은 0x00000000 ~ 0xFFFFFFFF 형태여야함.
    data_str = user_input_list[2]
    if not is_valid_data(data_str):
        LOGGER.print_log("data가 valid 하지 않습니다.")
        return False
    return True


def is_valid_fullwrite_command_params(user_input_list: list[str]) -> bool:
    # fullwrite param은 2개여야함. (커맨드 포함)
    if len(user_input_list) != 2:
        LOGGER.print_log(f"파라미터 갯수가 올바르지 않습니다: {len(user_input_list)}")
        return False

    # 2번째 param은 0x00000000 ~ 0xFFFFFFFF 사이여야합니다.
    data_str = user_input_list[1]
    if not is_valid_data(data_str):
        LOGGER.print_log("data가 valid 하지 않습니다")
        return False

    return True

def is_integer_or_negative(s: str) -> bool:
    if s.startswith('-') and s[1:].isdigit() :
        return True  # 음수: 앞에 '-' 제외하고 숫자인지 확인
    if s.isdigit() :
        return True
    return False

def is_valid_erase_command_params(user_input_list: list) -> bool:
    if len(user_input_list) != 3:
        LOGGER.print_log(f"파라미터 갯수가 올바르지 않습니다: {len(user_input_list)}")
        return False

    # 2번째 param은 숫자여야하고, 범위가 MAX_LBA 미만이어야함.
    lba_str = user_input_list[1]
    if not is_valid_lba(lba_str):
        LOGGER.print_log("lba가 valid 하지 않습니다.")
        return False

    # 3번째 param은 숫자여야 하고, 범위가 -INF ~ +INF
    size_str = user_input_list[2]

    if not is_integer_or_negative(size_str):
        return False
    return True

def is_valid_erase_range_params(user_input_list: list) -> bool:
    if len(user_input_list) != 3:
        LOGGER.print_log(f"파라미터 갯수가 올바르지 않습니다: {len(user_input_list)}")
        return False

    # 2번째 param은 숫자여야하고, 범위가 MAX_LBA 미만이어야함.
    lba_start_str = user_input_list[1]
    if not is_valid_lba(lba_start_str):
        LOGGER.print_log("start lba가 valid 하지 않습니다.")
        return False

    # 3번째 param은 숫자여야하고, 범위가 MAX_LBA 미만이어야함.
    lba_start_str = user_input_list[2]
    if not is_valid_lba(lba_start_str):
        LOGGER.print_log("end lba가 valid 하지 않습니다.")
        return False

    return True

def is_valid_command(command_param):
    valid_command_list = ["flush", "write", "read", "erase", "erase_range", "fullwrite", "fullread", "help", "exit"]
    if command_param != "" \
        and (TEST_SCRIPT_1.startswith(command_param) \
            or TEST_SCRIPT_2.startswith(command_param) \
            or TEST_SCRIPT_3.startswith(command_param) \
            or TEST_SCRIPT_4.startswith(command_param)):
        return True
    if command_param in valid_command_list:
        return True
    return False


def is_valid_lba(lba):
    """
    LBA가 0~MAX_LEN - 1 범위의 정수인지 확인
    """
    try:
        lba_int = int(lba)
        return 0 <= lba_int < MAX_LBA
    except (ValueError, TypeError):
        return False


def is_valid_data(data):
    """
    0x 또는 0X로 시작하고, 그 뒤에 8자리 A~F, 0~9로만 이루어진 16진수 문자열인지 확인
    예: 0x1234ABCD (총 10글자)
    """
    return bool(re.fullmatch(r'0[xX][A-Fa-f0-9]{8}', str(data)))


def hex_string_generator():
    """
    0x 또는 0X로 시작하고, 그 뒤에 8자리 A~F, 0~9로만 이루어진 16진수 문자열을 생성하는 제너레이터
    예: 0x1234ABCD (총 10글자)
    :return
        candidate: 위 조건을 만족하는 string
    """
    prefix_options = ['0x', '0X']
    hex_digits = '0123456789ABCDEFabcdef'
    while True:
        prefix = random.choice(prefix_options)
        hex_part = ''.join(random.choices(hex_digits, k=8))
        candidate = prefix + hex_part
        return candidate
