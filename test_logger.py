import pytest
import os
from logger import Logger
import sys
import io
import random

TEST_LATEST_FILE = "test_latest_file.log"
TEST_MAX_BYTES = 1000

@pytest.fixture(autouse=True)
def cleanup():
    # 테스트 전 실행
    yield
    # 테스트 후 cleanup
    if os.path.exists(TEST_LATEST_FILE):
        os.remove(TEST_LATEST_FILE)

    # until로 시작하는 로그 파일 정리
    for file in os.listdir():
        if file.startswith("until_") and (file.endswith(".log") or file.endswith(".zip")):
            os.remove(file)

@pytest.fixture()
def stdout_logger():
    logger = Logger(is_stdout=True, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES,test_mode=True)
    logger.update_settings(is_stdout=True, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES, test_mode=True)
    return logger

@pytest.fixture()
def file_only_logger():
    logger = Logger(is_stdout=True, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES, test_mode=True)
    logger.update_settings(is_stdout=False, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES, test_mode=True)
    return logger

def write_generate_1_file(logger:Logger, target_bytes: int):
    """지정된 바이트 수 이상으로 로그 파일을 채웁니다"""
    print("하나의 파일을 채울만큼 printlog를 반복합니다.")
    count = 0

    # 여기서 11번 호출하면 TEST_MAX_BYTES를 딱 넘음
    for i in range(11):
        message = f"Test message {count} to fill up the log file"
        logger.print_log(message)

def test_singleton_without_changing_value():
    logger = Logger(is_stdout=True, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES,test_mode=True)
    another_logger = Logger(is_stdout=False, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES,test_mode=True)
    assert logger is another_logger
    assert logger.is_stdout == True

def test_singleton_update_settings():
    logger = Logger(is_stdout=True, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES, test_mode=True)
    another_logger = Logger(is_stdout=True, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES, test_mode=True)
    assert logger is another_logger
    another_logger.update_settings(is_stdout=False, file_path=TEST_LATEST_FILE, max_bytes=100)

    assert logger.is_stdout == False
    assert logger.max_bytes == 100
    assert logger.file_path == TEST_LATEST_FILE

def test_print_log_success(stdout_logger):
    # stdout 출력 캡처
    captured_output = io.StringIO()
    sys.stdout = captured_output

    test_message = "Test log message"
    stdout_logger.print_log(test_message)

    # 원래 stdout 복원
    sys.stdout = sys.__stdout__

    # 콘솔 출력 확인
    assert test_message in captured_output.getvalue()

    # 파일 출력 확인
    assert os.path.exists(TEST_LATEST_FILE)
    with open(TEST_LATEST_FILE, 'r') as f:
        log_content = f.read()
        assert test_message in log_content

def test_print_log_without_stdout(file_only_logger):
    # stdout이 없을때 print를 안찍어야함.
    # file output은 만들어야함.
    file_logger = Logger(is_stdout=False, file_path=TEST_LATEST_FILE, max_bytes=TEST_MAX_BYTES)

    # stdout 출력 캡처
    captured_output = io.StringIO()
    sys.stdout = captured_output

    test_message = "Test log message without stdout"
    file_logger.print_log(test_message)

    # 원래 stdout 복원
    sys.stdout = sys.__stdout__

    # 콘솔 출력이 없어야 함
    assert test_message not in captured_output.getvalue()
    assert captured_output.getvalue() == ""

    # 파일 출력은 있어야 함
    assert os.path.exists(TEST_LATEST_FILE)
    with open(TEST_LATEST_FILE, 'r') as f:
        log_content = f.read()
        assert test_message in log_content

@pytest.mark.repeat(10)
def test_backup_log_file_generation_success(stdout_logger):
    # TEST_MAX_BYTES 이상
    # until 로그 파일이 제대로 생성되어야함.

    # 먼저 로그 파일을 최대 크기 이상으로 채움
    write_generate_1_file(stdout_logger, TEST_MAX_BYTES + 10)

    # 백업 파일 생성을 트리거
    stdout_logger.print_log("Trigger backup file creation")

    # 백업 파일이 생성되었는지 확인
    backup_files = [f for f in os.listdir() if f.startswith("until_") and f.endswith(".log")]
    assert len(backup_files) == 1

    # 새 로그 파일이 생성되었는지 확인
    assert os.path.exists(TEST_LATEST_FILE)
    assert os.path.getsize(TEST_LATEST_FILE) < TEST_MAX_BYTES


def test_zip_file_generation_after_2_file_generations(file_only_logger):
    """
    - until로 시작하는 파일이 이미 존재할 때 해당 파일의 확장자를 zip으로 바꿈을 테스트
    """
    # 먼저 로그 파일을 최대 크기 이상으로 채움
    write_generate_1_file(file_only_logger, TEST_MAX_BYTES + 100)

    # 두 번째 백업 파일 생성을 트리거하기 위해 다시 파일을 채움
    write_generate_1_file(file_only_logger, TEST_MAX_BYTES + 100)

    # 세 번째 파일 생성을 트리거
    write_generate_1_file(file_only_logger, TEST_MAX_BYTES + 100)

    # 결과 확인
    log_files = [f for f in os.listdir() if f.startswith("until_") and f.endswith(".log")]
    zip_files = [f for f in os.listdir() if f.startswith("until_") and f.endswith(".zip")]

    # until로 시작하는 zip 파일 하나랑, until로 시작하는 log 파일 하나, test_latest.log가 있어야함.
    assert len(log_files) == 1, "하나의 .log 파일이 있어야 함"
    assert len(zip_files) == 1, "하나의 .zip 파일이 있어야 함"
    assert os.path.exists(TEST_LATEST_FILE), "최신 로그 파일이 존재해야 함"

@pytest.mark.repeat(10)
def test_zip_file_generation_after_random_number_file_generations(file_only_logger):
    # 최소 3개의 파일이 생성 될 수 있도록 randint를 생성함.
    num_log_files = random.randint(3,10)
    expected_num_zip_files = num_log_files - 2
    expected_num_log_file = 1

    # N개의 로그 파일을 생성함.
    for _ in range(num_log_files):
        # 로그 파일 생성 1회
        write_generate_1_file(file_only_logger, TEST_MAX_BYTES + 10)

    # 결과 확인
    log_files = [f for f in os.listdir() if f.startswith("until_") and f.endswith(".log")]
    zip_files = [f for f in os.listdir() if f.startswith("until_") and f.endswith(".zip")]

    # 예상되는 숫자의 zip, log, latest log 파일이 존재해야함. (매번 테스트마다 다름)
    assert len(log_files) == expected_num_log_file, "하나의 .log 파일이 있어야 함"
    assert len(zip_files) == expected_num_zip_files, "여러개의 .zip 파일이 있어야 함"
    assert os.path.exists(TEST_LATEST_FILE), "최신 로그 파일이 존재해야 함"