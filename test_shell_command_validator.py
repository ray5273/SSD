from shell_command_validator import (
    is_valid_command, is_valid_lba, is_valid_data,
    is_valid_read_command_params, is_valid_write_command_params, is_valid_fullwrite_command_params,
    hex_string_generator
)
import pytest
MAX_LBA = 100


def test_is_valid_read_command_params():
    # 정상 케이스
    assert is_valid_read_command_params(["read", "0"])
    assert is_valid_read_command_params(["read", str(MAX_LBA - 1)])
    # 파라미터 개수 부족/과다
    assert not is_valid_read_command_params(["read"])
    assert not is_valid_read_command_params(["read", "1", "extra"])
    # LBA가 유효하지 않은 경우
    assert not is_valid_read_command_params(["read", str(MAX_LBA)])
    assert not is_valid_read_command_params(["read", "-1"])
    assert not is_valid_read_command_params(["read", "abc"])


def test_is_valid_write_command_params():
    # 정상 케이스
    assert is_valid_write_command_params(["write", "0", "0x12345678"])
    assert is_valid_write_command_params(["write", str(MAX_LBA - 1), "0xFFFFFFFF"])
    # 파라미터 개수 부족/과다
    assert not is_valid_write_command_params(["write", "1"])
    assert not is_valid_write_command_params(["write", "1", "0x12345678", "extra"])
    # LBA가 유효하지 않은 경우
    assert not is_valid_write_command_params(["write", str(MAX_LBA), "0x12345678"])
    assert not is_valid_write_command_params(["write", "-1", "0x12345678"])
    assert not is_valid_write_command_params(["write", "abc", "0x12345678"])
    # 데이터가 유효하지 않은 경우
    assert not is_valid_write_command_params(["write", "1", "12345678"])
    assert not is_valid_write_command_params(["write", "1", "0xZZZZZZZZ"])
    assert not is_valid_write_command_params(["write", "1", "0x123"])


def test_is_valid_fullwrite_command_params():
    # 정상 케이스
    assert is_valid_fullwrite_command_params(["fullwrite", "0x12345678"])
    assert is_valid_fullwrite_command_params(["fullwrite", "0xFFFFFFFF"])
    # 파라미터 개수 부족/과다
    assert not is_valid_fullwrite_command_params(["fullwrite"])
    assert not is_valid_fullwrite_command_params(["fullwrite", "0x12345678", "extra"])
    # 데이터가 유효하지 않은 경우
    assert not is_valid_fullwrite_command_params(["fullwrite", "12345678"])
    assert not is_valid_fullwrite_command_params(["fullwrite", "0xZZZZZZZZ"])
    assert not is_valid_fullwrite_command_params(["fullwrite", "0x123"])


def test_is_valid_command():
    # 유효한 command
    assert is_valid_command("write")
    assert is_valid_command("read")

    # 유효한 스크립트
    assert is_valid_command("1")
    assert is_valid_command("1_")
    assert is_valid_command("1_FullWriteAndR")
    assert is_valid_command("1_FullWriteAndReadCompare")

    # 유효하지 않은 커맨드들
    assert not is_valid_command("unknown")
    assert not is_valid_command("")
    assert not is_valid_command("WRITE")  # 대문자 허용하지 않음
    assert not is_valid_command("READ")


def test_is_valid_lba():
    # 성공 해야하는 케이스들
    assert is_valid_lba("0")
    assert is_valid_lba(str(MAX_LBA - 1))

    # 실패 해야하는 케이스들
    assert not is_valid_lba(str(MAX_LBA))  # MAX_LEN이상부터 실패
    assert not is_valid_lba(str(MAX_LBA + 10000))
    assert not is_valid_lba("-1")  # 음수도 실패
    assert not is_valid_lba("abc")


def test_is_valid_data():
    # Valid한 데이터인 경우
    assert is_valid_data("0x000000AF")
    assert is_valid_data("0X00001234")
    assert is_valid_data("0x00abcdef")

    # Valid한 데이터가 아닌 경우
    assert not is_valid_data("1234123412")
    assert not is_valid_data("0xGHIJ1234")
    assert not is_valid_data("0x")


@pytest.mark.repeat(50)
def test_hex_string_generator():
    # 랜덤 hex string generator가 valid_data를 생성하는지를 테스트
    data = hex_string_generator()
    assert is_valid_data(data)
