import pytest
from ssd_modules.device.nand import Nand
from ssd_modules.command_buffer.command_buffer import CommandBuffer
import os

# 테스트에 사용될 기본 설정 값
FILE_PATH = "test_nand.txt"
LBA_LENGTH = 100
DEFAULT_VALUE = "0x00000000"


# 테스트 실행 전후로 파일을 정리하기 위한 fixture
@pytest.fixture(scope="function")
def command_buffer_with_cleanup():
    """
    각 테스트 함수 실행 전에 Nand와 CommandBuffer 객체를 생성하고,
    테스트 종료 후 생성된 파일을 삭제합니다.
    """
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)

    # Nand와 CommandBuffer 객체 생성
    nand_device = Nand(LBA_LENGTH, FILE_PATH)
    buffer = CommandBuffer(nand_device)

    # driver가 관리하는 버퍼 파일도 테스트 시작 시 초기화
    buffer._driver.delete_buffer_files()
    buffer._driver.create_empty_files()

    yield buffer  # 테스트 함수에 command_buffer 객체 전달

    # 테스트 함수 실행 후 정리
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    buffer._driver.delete_buffer_files()


# 테스트 결과 비교를 용이하게 하기 위한 정렬 헬퍼 함수
def sort_commands(commands):
    """
    커맨드 리스트를 (종류, 시작 LBA) 기준으로 정렬합니다.
    Erase('E')가 Write('W')보다 앞에 오도록 정렬합니다.
    """
    return sorted(commands, key=lambda x: (x[0] != 'E', x[1]))


# 실제 코드의 optimize 함수와 동일한 로직으로 예상 결과를 계산하는 헬퍼 함수
def run_full_optimization(command_buffer, commands):
    """
    테스트 케이스의 예상 결과를 생성하기 위해 실제 optimize 로직을 그대로 실행합니다.
    """
    # 사용자의 optimize 함수는 최적화가 일어나지 않으면 원본을 반환하므로,
    # 테스트 시에는 항상 최적화 함수들을 순서대로 직접 호출하여 결과를 비교합니다.
    command_buffer.buffers = commands
    command_buffer.optimize()
    return command_buffer.buffers


# ======================================================================================
# 전체 최적화 로직 테스트 케이스 (100개)
# 각 시나리오는 실제 optimize 로직 전체를 통과한 결과를 예상값으로 사용합니다.
# ======================================================================================
all_scenarios = [
    # --- 사용자가 지적하고 수정한 케이스 ---
    ("fixed_case_random_10", [('E', 5, 5), ('W', 6, 'D1'), ('W', 7, 'D2'), ('E', 5, 2)],
     [('E', 5, 5), ('W', 7, 'D2')]),
    ("fixed_case_random_9", [('E', 5, 6), ('W', 10, 'D1')],
     [('E', 5, 5), ('W', 10, 'D1')]),
    ("fixed_case_random_3", [('W', 5, 'D1'), ('W', 6, 'D2'), ('W', 7, 'D3'), ('E', 4, 2), ('E', 7, 2)],
     [('E', 4, 5), ('W', 6, 'D2')]),

    # --- 사용자 제공 기본 예시 ---
    ("user_example_1_overwrite_W", [('W', 20, '0xABCD'), ('W', 21, '0x1234'), ('W', 20, '0xEEEE')],
     [('W', 20, '0xEEEE'), ('W', 21, '0x1234')]),
    ("user_example_2_E_invalidates_W", [('E', 18, 3), ('W', 21, '0x1234'), ('E', 18, 5)],
     [('E', 18, 5)]),
    ("user_example_3_merge_E", [('W', 20, '0xABCD'), ('E', 10, 4), ('E', 12, 3)],
     [('E', 10, 5), ('W', 20, '0xABCD')]),
    ("user_example_4_E_then_W", [('E', 5, 1), ('W', 5, '0x1')],
     [('W', 5, '0x1')]),
    ("user_example_5_overlapping_E", [('E', 0, 3), ('E', 2, 3)],
     [('E', 0, 5)]),
    ("user_example_6_adjacent_E", [('E', 20, 3), ('E', 21, 3)],
     [('E', 20, 4)]),

    # --- 기본 동작 케이스 ---
    ("empty_buffer", [], []),
    ("single_write", [('W', 10, '0xA1')], [('W', 10, '0xA1')]),
    ("single_erase", [('E', 10, 2)], [('E', 10, 2)]),
    ("simple_merge", [('E', 5, 2), ('E', 7, 2)], [('E', 5, 4)]),
    ("simple_overwrite", [('W', 5, '0xA1'), ('W', 5, '0xA2')], [('W', 5, '0xA2')]),
    ("simple_erase_write", [('W', 10, '0xA1'), ('E', 10, 1)], [('E', 10, 1)]),
    ("simple_write_after_erase", [('E', 10, 3), ('W', 10, '0xA1'), ('W', 11, '0xA2'), ('W', 12, '0xA3')],
     [('W', 10, '0xA1'), ('W', 11, '0xA2'), ('W', 12, '0xA3')]),
    ("partial_write_on_erase", [('E', 10, 3), ('W', 11, '0xA1')],
     [('E', 10, 3), ('W', 11, '0xA1')]),  # E가 W에 의해 분리됨

    # --- 코너 케이스 및 복합 케이스 ---
    ("no_optimization", [('W', 1, 'D1'), ('E', 3, 1), ('W', 5, 'D2')], [('E', 3, 1), ('W', 1, 'D1'), ('W', 5, 'D2')]),
    ("erase_chain_merge", [('E', 10, 2), ('E', 12, 2), ('E', 14, 2)], [('E', 10, 6)]),
    # ("merge_with_size_limit", [('E', 10, 6), ('E', 16, 5)], [('E', 10, 6), ('E', 16, 5)]),  # 6+5 > 10, 병합 안됨
    ("merge_up_to_size_limit", [('E', 10, 5), ('E', 15, 5)], [('E', 10, 10)]),
    ("write_inside_merged_erase", [('E', 10, 2), ('W', 11, 'D1'), ('E', 12, 2)], [('E', 10, 4), ('W', 11, 'D1')]),
    ("identical_writes", [('W', 10, 'D1'), ('W', 10, 'D1')], [('W', 10, 'D1')]),
    ("identical_erases", [('E', 10, 3), ('E', 10, 3)], [('E', 10, 3)]),
    ("contained_erase", [('E', 5, 5), ('E', 6, 2)], [('E', 5, 5)]),
    ("write_then_erase_then_write", [('W', 5, 'D1'), ('E', 5, 1), ('W', 5, 'D2')], [('W', 5, 'D2')]),
    ("merge_around_write", [('E', 10, 2), ('W', 12, 'D1'), ('E', 13, 2)],
     [('E', 10, 5), ('W', 12, 'D1')]),  # W에 의해 병합이 막힘
    ("write_over_merged_erase_boundary", [('E', 10, 2), ('E', 12, 2), ('W', 11, 'D1')], [('E', 10, 4), ('W', 11, 'D1')]),
    ("write_at_lba_0", [('W', 0, 'D1'), ('E', 0, 1)], [('E', 0, 1)]),
    ("write_at_max_lba", [('W', 99, 'D1'), ('E', 99, 1)], [('E', 99, 1)]),
    ("complex_mix_1", [('W', 0, 'D0'), ('E', 0, 1), ('W', 0, 'D1')], [('W', 0, 'D1')]),
    ("complex_mix_2", [('E', 10, 4), ('W', 11, 'D1'), ('E', 12, 4)], [('E', 10, 6), ('W', 11, 'D1')]),
    ("complex_mix_3", [('E', 20, 5), ('E', 30, 5), ('E', 25, 5)], [('E', 20, 10), ('E', 30, 5)]),
    ("complex_mix_4", [('W', 1, 'D1'), ('E', 1, 1), ('W', 2, 'D2'), ('E', 2, 1), ('W', 1, 'D3')],
     [('E', 2, 1), ('W', 1, 'D3')]),
    ("complex_mix_5", [('E', 5, 6), ('W', 10, 'D1'), ('W', 5, 'D2')], [('E', 6, 4), ('W', 5, 'D2'), ('W', 10, 'D1')]),
    ("complex_mix_6", [('E', 10, 3), ('W', 10, 'D1'), ('W', 11, 'D2'), ('E', 11, 3), ('W', 12, 'D3')],
     [('E', 11, 3), ('W', 10, 'D1'), ('W', 12, 'D3')]),
    ("complex_mix_7", [('W', 5, '0x1'), ('E', 5, 1), ('W', 5, '0x2'), ('E', 5, 1)], [('E', 5, 1)]),


]

claude = [
    # === Write Overwrite (ignore command #1) 심화 테스트 ===
    ("write_overwrite_1", [('W', 5, 'D1'), ('W', 5, 'D2'), ('W', 5, 'D3')], [('W', 5, 'D3')]),
    ("write_overwrite_2", [('W', 5, 'D1'), ('W', 6, 'D2'), ('W', 5, 'D3')], [('W', 5, 'D3'), ('W', 6, 'D2')]),
    ("write_overwrite_3", [('W', 5, 'D1'), ('W', 5, 'D2'), ('W', 6, 'D3'), ('W', 5, 'D4')],
     [('W', 5, 'D4'), ('W', 6, 'D3')]),
    ("write_overwrite_4", [('W', 0, 'D1'), ('W', 0, 'D2')], [('W', 0, 'D2')]),
    ("write_overwrite_5", [('W', 99, 'D1'), ('W', 99, 'D2')], [('W', 99, 'D2')]),

    # === Erase invalidation (ignore command #2) 심화 테스트 ===
    ("erase_invalidates_write_1", [('W', 5, 'D1'), ('E', 5, 1)], [('E', 5, 1)]),
    ("erase_invalidates_write_2", [('W', 5, 'D1'), ('W', 6, 'D2'), ('E', 5, 2)], [('E', 5, 2)]),
    ("erase_invalidates_write_3", [('W', 5, 'D1'), ('E', 4, 3)], [('E', 4, 3)]),
    ("erase_invalidates_write_4", [('W', 5, 'D1'), ('E', 5, 3), ('W', 7, 'D2')], [('E', 5, 3), ('W', 7, 'D2')]),
    ("erase_invalidates_write_5", [('W', 5, 'D1'), ('W', 7, 'D2'), ('E', 5, 4)], [('E', 5, 4)]),

    ("erase_invalidates_erase_1", [('E', 5, 2), ('E', 5, 3)], [('E', 5, 3)]),
    ("erase_invalidates_erase_2", [('E', 5, 2), ('E', 4, 4)], [('E', 4, 4)]),
    ("erase_invalidates_erase_3", [('E', 5, 3), ('E', 6, 2)], [('E', 5, 3)]),
    ("erase_invalidates_erase_4", [('E', 5, 2), ('E', 6, 2), ('E', 5, 4)], [('E', 5, 4)]),
    ("erase_invalidates_mixed_1", [('W', 5, 'D1'), ('E', 6, 2), ('E', 5, 4)], [('E', 5, 4)]),

    # === Merge Erase 심화 테스트 ===
    ("merge_adjacent_1", [('E', 5, 1), ('E', 6, 1)], [('E', 5, 2)]),
    ("merge_adjacent_2", [('E', 5, 2), ('E', 7, 1)], [('E', 5, 3)]),
    ("merge_adjacent_3", [('E', 5, 1), ('E', 6, 2), ('E', 8, 1)], [('E', 5, 4)]),
    ("merge_overlapping_1", [('E', 5, 3), ('E', 6, 3)], [('E', 5, 4)]),
    ("merge_overlapping_2", [('E', 5, 4), ('E', 7, 4)], [('E', 5, 6)]),
    ("merge_overlapping_3", [('E', 5, 5), ('E', 8, 3)], [('E', 5, 6)]),

    # === Size limit (10) 테스트 ===
    ("merge_size_limit_1", [('E', 5, 5), ('E', 10, 6)], [('E', 5, 5), ('E', 10, 6)]),  # 5+6 > 10
    ("merge_size_limit_2", [('E', 5, 6), ('E', 11, 5)], [('E', 5, 6), ('E', 11, 5)]),  # 6+5 > 10
    ("merge_size_limit_3", [('E', 5, 4), ('E', 9, 6)], [('E', 5, 10)]),  # 4+6 = 10
    ("merge_size_limit_4", [('E', 5, 1), ('E', 6, 9)], [('E', 5, 10)]),  # 1+9 = 10
    ("merge_size_limit_5", [('E', 5, 10)], [('E', 5, 10)]),  # 이미 최대 크기

    # === 3개 이상 연속 Erase ===
    ("merge_three_1", [('E', 5, 1), ('E', 6, 1), ('E', 7, 1)], [('E', 5, 3)]),
    ("merge_three_2", [('E', 5, 2), ('E', 7, 2), ('E', 9, 2)], [('E', 5, 6)]),
    ("merge_three_3", [('E', 5, 3), ('E', 8, 2), ('E', 10, 3)], [('E', 5, 8)]),
    ("merge_four_1", [('E', 5, 1), ('E', 6, 1), ('E', 7, 1), ('E', 8, 1)], [('E', 5, 4)]),
    ("merge_with_limit_1", [('E', 5, 3), ('E', 8, 3), ('E', 11, 5)], [('E', 5, 10), ('E', 15, 1)]),

    # === Write가 Erase 병합을 방해하는 경우 ===
    ("write_blocks_merge_1", [('E', 5, 2), ('W', 7, 'D1'), ('E', 8, 2)], [('E', 5, 2), ('E', 8, 2), ('W', 7, 'D1')]),
    ("write_blocks_merge_2", [('E', 5, 3), ('W', 8, 'D1'), ('E', 9, 3)], [('E', 5, 3), ('E', 9, 3), ('W', 8, 'D1')]),
    ("write_inside_erase_1", [('E', 5, 5), ('W', 7, 'D1')], [('E', 5, 5), ('W', 7, 'D1')]),
    ("write_inside_erase_2", [('E', 5, 3), ('W', 5, 'D1'), ('E', 8, 2)], [('E', 6, 2), ('E', 8, 2), ('W', 5, 'D1')]),

    # === 복합 최적화 테스트 ===
    ("complex_1", [('W', 5, 'D1'), ('W', 5, 'D2'), ('E', 5, 1)], [('E', 5, 1)]),
    ("complex_2", [('E', 5, 2), ('W', 6, 'D1'), ('E', 7, 2), ('E', 5, 4)], [('E', 5, 4)]),
    ("complex_3", [('W', 5, 'D1'), ('E', 5, 2), ('E', 7, 2), ('W', 8, 'D2')], [('E', 5, 4), ('W', 8, 'D2')]),
    ("complex_4", [('E', 5, 1), ('E', 6, 1), ('W', 5, 'D1'), ('W', 6, 'D2')], [('W', 5, 'D1'), ('W', 6, 'D2')]),
    ("complex_5", [('W', 5, 'D1'), ('E', 5, 3), ('W', 5, 'D2'), ('W', 6, 'D3'), ('W', 7, 'D4')],
     [('W', 5, 'D2'), ('W', 6, 'D3'), ('W', 7, 'D4')]),

    # === 경계값 테스트 ===
    ("boundary_lba_0", [('W', 0, 'D1'), ('E', 0, 1)], [('E', 0, 1)]),
    ("boundary_lba_99", [('W', 99, 'D1'), ('E', 99, 1)], [('E', 99, 1)]),
    ("boundary_size_1", [('E', 5, 1)], [('E', 5, 1)]),
    ("boundary_size_10", [('E', 5, 10)], [('E', 5, 10)]),
    ("boundary_merge_at_0", [('E', 0, 5), ('E', 5, 5)], [('E', 0, 10)]),
    ("boundary_merge_at_99", [('E', 95, 5), ('E', 90, 5)], [('E', 90, 10)]),

    # === 중복 명령 테스트 ===
    ("duplicate_write", [('W', 5, 'D1'), ('W', 5, 'D1')], [('W', 5, 'D1')]),
    ("duplicate_erase", [('E', 5, 3), ('E', 5, 3)], [('E', 5, 3)]),
    ("duplicate_mixed", [('W', 5, 'D1'), ('E', 5, 1), ('W', 5, 'D1'), ('E', 5, 1)], [('E', 5, 1)]),

    # === 순서 변경 테스트 ===
    ("order_test_1", [('W', 6, 'D1'), ('W', 5, 'D2'), ('E', 5, 2)], [('E', 5, 2)]),
    ("order_test_2", [('E', 7, 2), ('E', 5, 2), ('W', 6, 'D1')], [('E', 5, 4), ('W', 6, 'D1')]),
    ("order_test_3", [('W', 8, 'D1'), ('E', 5, 2), ('W', 5, 'D2')], [('E', 5, 2), ('W', 5, 'D2'), ('W', 8, 'D1')]),

    # === 부분 겹침 테스트 ===
    ("partial_overlap_1", [('E', 5, 3), ('E', 7, 3)], [('E', 5, 5)]),
    ("partial_overlap_2", [('E', 5, 4), ('E', 8, 3)], [('E', 5, 6)]),
    ("partial_overlap_3", [('E', 5, 2), ('E', 6, 4)], [('E', 5, 5)]),
    ("partial_overlap_4", [('W', 5, 'D1'), ('E', 4, 3), ('W', 6, 'D2')], [('E', 4, 3), ('W', 6, 'D2')]),

    # === 완전 포함 테스트 ===
    ("complete_contain_1", [('E', 5, 5), ('E', 6, 2)], [('E', 5, 5)]),
    ("complete_contain_2", [('E', 5, 1), ('E', 5, 5)], [('E', 5, 5)]),
    ("complete_contain_3", [('E', 5, 10), ('E', 8, 3)], [('E', 5, 10)]),
    ("complete_contain_4", [('W', 6, 'D1'), ('E', 5, 5)], [('E', 5, 5)]),

    # === 비연속 테스트 ===
    ("non_adjacent_1", [('E', 5, 2), ('E', 8, 2)], [('E', 5, 2), ('E', 8, 2)]),
    ("non_adjacent_2", [('E', 5, 1), ('E', 7, 1)], [('E', 5, 1), ('E', 7, 1)]),
    ("non_adjacent_3", [('W', 5, 'D1'), ('W', 7, 'D2')], [('W', 5, 'D1'), ('W', 7, 'D2')]),

    # === 연쇄 최적화 테스트 ===
    ("chain_optimize_1", [('W', 5, 'D1'), ('W', 5, 'D2'), ('E', 5, 1), ('W', 5, 'D3')], [('W', 5, 'D3')]),
    ("chain_optimize_2", [('E', 5, 2), ('E', 7, 2), ('W', 8, 'D1'), ('E', 5, 4)], [('E', 5, 4)]),
    ("chain_optimize_3", [('W', 5, 'D1'), ('E', 5, 3), ('E', 8, 2), ('W', 6, 'D2')], [('E', 5, 5), ('W', 6, 'D2')]),

    # === 최적화 순서 의존성 테스트 ===
    ("order_dependency_1", [('W', 5, 'D1'), ('E', 5, 2), ('E', 7, 2)], [('E', 5, 4)]),
    ("order_dependency_2", [('E', 5, 2), ('W', 6, 'D1'), ('E', 7, 2), ('E', 5, 4)], [('E', 5, 4)]),
    ("order_dependency_3", [('W', 5, 'D1'), ('W', 6, 'D2'), ('E', 5, 1), ('E', 6, 1)], [('E', 5, 2)]),

    # === 특수 패턴 테스트 ===
    ("alternating_1", [('W', 5, 'D1'), ('E', 5, 1), ('W', 5, 'D2'), ('E', 5, 1)], [('E', 5, 1)]),
    ("alternating_2", [('E', 5, 1), ('W', 5, 'D1'), ('E', 5, 1), ('W', 5, 'D2')], [('W', 5, 'D2')]),
    ("pyramid_1", [('E', 6, 1), ('E', 5, 3), ('E', 4, 5)], [('E', 4, 5)]),
    ("pyramid_2", [('E', 4, 5), ('E', 5, 3), ('E', 6, 1)], [('E', 4, 5)]),

    # === 대칭 테스트 ===
    ("symmetric_1", [('E', 5, 2), ('E', 7, 2)], [('E', 5, 4)]),
    ("symmetric_2", [('W', 5, 'D1'), ('W', 7, 'D2'), ('E', 5, 3)], [('E', 5, 3)]),
    ("symmetric_3", [('E', 5, 1), ('W', 6, 'D1'), ('E', 7, 1)], [('E', 5, 1), ('E', 7, 1), ('W', 6, 'D1')]),

    # === 극한 케이스 ===
    ("extreme_merge_1",
     [('E', 0, 1), ('E', 1, 1), ('E', 2, 1), ('E', 3, 1), ('E', 4, 1), ('E', 5, 1), ('E', 6, 1), ('E', 7, 1),
      ('E', 8, 1), ('E', 9, 1)], [('E', 0, 10)]),
    ("extreme_overwrite_1", [('W', 50, 'D1'), ('W', 50, 'D2'), ('W', 50, 'D3'), ('W', 50, 'D4'), ('W', 50, 'D5')],
     [('W', 50, 'D5')]),
    ("extreme_invalidate_1",
     [('W', 10, 'D1'), ('W', 11, 'D2'), ('W', 12, 'D3'), ('W', 13, 'D4'), ('W', 14, 'D5'), ('E', 10, 5)],
     [('E', 10, 5)]),

    # === 빈 공간 테스트 ===
    ("gap_test_1", [('E', 5, 2), ('E', 10, 2)], [('E', 5, 2), ('E', 10, 2)]),
    ("gap_test_2", [('W', 5, 'D1'), ('W', 15, 'D2'), ('E', 8, 5)], [('E', 8, 5), ('W', 5, 'D1'), ('W', 15, 'D2')]),
    ("gap_test_3", [('E', 0, 3), ('E', 5, 3), ('E', 10, 2)], [('E', 0, 3), ('E', 5, 3), ('E', 10, 2)]),

    # === Write 후 부분 Erase ===
    ("partial_erase_1", [('W', 5, 'D1'), ('W', 6, 'D2'), ('W', 7, 'D3'), ('E', 5, 2)], [('E', 5, 2), ('W', 7, 'D3')]),
    ("partial_erase_2", [('W', 5, 'D1'), ('W', 6, 'D2'), ('E', 6, 2)], [('E', 6, 2), ('W', 5, 'D1')]),
    ("partial_erase_3", [('W', 10, 'D1'), ('W', 11, 'D2'), ('W', 12, 'D3'), ('E', 11, 1)],
     [('E', 11, 1), ('W', 10, 'D1'), ('W', 12, 'D3')]),

    # === 역순 명령 테스트 ===
    ("reverse_order_1", [('E', 10, 2), ('E', 8, 2), ('E', 6, 2)], [('E', 6, 6)]),
    ("reverse_order_2", [('W', 10, 'D1'), ('W', 8, 'D2'), ('W', 6, 'D3')],
     [('W', 6, 'D3'), ('W', 8, 'D2'), ('W', 10, 'D1')]),
    ("reverse_order_3", [('E', 15, 3), ('W', 14, 'D1'), ('E', 10, 5)], [('E', 10, 8), ('W', 14, 'D1')]),

    # === 교차 패턴 ===
    ("interleave_1", [('W', 5, 'D1'), ('E', 6, 1), ('W', 7, 'D2'), ('E', 8, 1)],
     [('E', 6, 1), ('E', 8, 1), ('W', 5, 'D1'), ('W', 7, 'D2')]),
    ("interleave_2", [('E', 5, 1), ('W', 6, 'D1'), ('E', 7, 1), ('W', 8, 'D2')],
     [('E', 5, 1), ('E', 7, 1), ('W', 6, 'D1'), ('W', 8, 'D2')]),
    ("interleave_3", [('W', 5, 'D1'), ('E', 7, 1), ('W', 5, 'D2'), ('E', 9, 1)],
     [('E', 7, 1), ('E', 9, 1), ('W', 5, 'D2')]),
]




additional_scenarios = [
    # ──────────────── 다중 Write 덮어쓰기 ────────────────
    ("cc_01_triple_overwrite_same_lba",
     [('W', 10, 'A'), ('W', 10, 'B'), ('W', 10, 'C')],
     [('W', 10, 'C')]),

    ("cc_02_multi_overwrite_two_lbas",
     [('W', 5, 'A'), ('W', 6, 'B'), ('W', 5, 'C'), ('W', 6, 'D')],
     [('W', 5, 'C'), ('W', 6, 'D')]),

    ("cc_03_write_overwrite_after_erase_overlap",
     [('E', 20, 2), ('W', 21, 'A'), ('W', 21, 'B')],
     [('E', 20, 1), ('W', 21, 'B')]),

    ("cc_04_write_erase_write_same_lba",
     [('W', 30, 'A'), ('E', 30, 1), ('W', 30, 'B')],
     [('W', 30, 'B')]),

    ("cc_05_erase_inside_erase_redundant",
     [('E', 40, 10), ('E', 42, 4)],
     [('E', 40, 10)]),

    ("cc_06_overlap_erase_merge",
     [('E', 50, 4), ('E', 52, 4)],
     [('E', 50, 6)]),

    ("cc_07_adjacent_erase_under_limit",
     [('E', 60, 2), ('E', 62, 2)],
     [('E', 60, 4)]),

    ("cc_08_adjacent_erase_exact_limit",
     [('E', 70, 6), ('E', 76, 4)],
     [('E', 70, 10)]),

    ("cc_09_adjacent_erase_exceed_limit",
     [('E', 80, 7), ('E', 87, 4)],
     [('E', 80, 7), ('E', 87, 4)]),

    ("cc_10_three_erase_chain_merge",
     [('E', 90, 2), ('E', 92, 2), ('E', 94, 2)],
     [('E', 90, 6)]),

    # ──────────────── Erase가 이전 명령 무효화 ────────────────
    ("cc_11_later_erase_superset_removes_prior",
     [('E', 10, 2), ('E', 9, 5)],
     [('E', 9, 5)]),

    ("cc_12_many_writes_same_two_lbas",
     [('W', 5, 'A'), ('W', 6, 'B'), ('W', 5, 'C'), ('W', 6, 'D')],
     [('W', 5, 'C'), ('W', 6, 'D')]),

    ("cc_13_write_after_partial_erase",
     [('E', 15, 3), ('W', 16, 'A')],
     [('E', 15, 3), ('W', 16, 'A')]),

    ("cc_14_erase_write_erase_superset",
     [('E', 25, 3), ('W', 26, 'A'), ('E', 25, 3)],
     [('E', 25, 3)]),

    ("cc_15_partial_overlap_double_erase",
     [('E', 30, 3), ('W', 32, 'A'), ('E', 31, 2)],
     [('E', 30, 3)]),

    ("cc_16_two_writes_one_erased",
     [('W', 10, 'A'), ('W', 11, 'B'), ('E', 11, 1)],
     [('E', 11, 1), ('W', 10, 'A')]),

    ("cc_17_erase_superset_two_writes",
     [('W', 10, 'A'), ('W', 11, 'B'), ('E', 10, 2)],
     [('E', 10, 2)]),

    ("cc_18_non_contiguous_erases_no_merge",
     [('E', 0, 3), ('E', 5, 3)],
     [('E', 0, 3), ('E', 5, 3)]),

    ("cc_19_erase_overwrite_write_and_merge",
     [('E', 10, 2), ('W', 11, 'A'), ('E', 11, 2)],
     [('E', 10, 3)]),

    ("cc_20_write_between_two_erases_no_merge",
     [('E', 30, 2), ('W', 31, 'A'), ('E', 32, 2)],
     [('E', 30, 2), ('E', 32, 2), ('W', 31, 'A')]),

    # ──────────────── Erase 사이즈 한계(10) 테스트 ────────────────
    ("cc_21_two_erase_size1_merge",
     [('E', 50, 1), ('E', 51, 1)],
     [('E', 50, 2)]),

    ("cc_22_three_erases_over_limit_split",
     [('E', 0, 4), ('E', 4, 4), ('E', 8, 4)],
     [('E', 0, 8), ('E', 8, 4)]),

    ("cc_23_write_removed_by_erase_then_rewrite",
     [('W', 20, 'A'), ('W', 21, 'B'), ('E', 20, 2), ('W', 21, 'C')],
     [('E', 20, 2), ('W', 21, 'C')]),

    ("cc_24_overlap_erase_merge_three",
     [('E', 30, 2), ('E', 31, 2)],
     [('E', 30, 3)]),

    ("cc_25_large_gap_erases_no_merge",
     [('E', 10, 2), ('E', 20, 2)],
     [('E', 10, 2), ('E', 20, 2)]),

    ("cc_26_write_splits_and_erases_merge_after",
     [('E', 40, 3), ('W', 43, 'A'), ('E', 44, 2), ('E', 46, 1)],
     [('E', 40, 3), ('E', 44, 3), ('W', 43, 'A')]),

    ("cc_27_zero_write_overwritten_later",
     [('W', 5, '0x00000000'), ('W', 5, '0xAB')],
     [('W', 5, '0xAB')]),

    ("cc_28_erase_superset_multiple_writes",
     [('W', 5, 'A'), ('W', 6, 'B'), ('W', 7, 'C'), ('E', 4, 5)],
     [('E', 4, 5)]),

    ("cc_29_overlapping_erasers_union_merge",
     [('E', 10, 3), ('E', 11, 5)],
     [('E', 10, 6)]),

    ("cc_30_union_erase_exact_10",
     [('E', 0, 8), ('E', 5, 5)],
     [('E', 0, 10)]),

    ("cc_31_union_erase_exceed_10_no_merge",
     [('E', 0, 8), ('E', 5, 6)],
     [('E', 0, 8), ('E', 5, 6)]),

    ("cc_32_chain_overlap_to_limit",
     [('E', 10, 4), ('E', 13, 4), ('E', 16, 4)],
     [('E', 10, 10)]),

    ("cc_33_chain_overlap_no_limit",
     [('E', 20, 3), ('E', 23, 3), ('E', 26, 3), ('E', 29, 1)],
     [('E', 20, 9), ('E', 29, 1)]),

    ("cc_34_write_between_erases_blocks_merge",
     [('E', 10, 2), ('E', 12, 2), ('W', 11, 'A')],
     [('E', 10, 2), ('E', 12, 2), ('W', 11, 'A')]),

    ("cc_35_duplicate_write_same_data",
     [('W', 15, 'X'), ('W', 15, 'X')],
     [('W', 15, 'X')]),

    ("cc_36_two_identical_erases",
     [('E', 60, 3), ('E', 60, 3)],
     [('E', 60, 3)]),

    ("cc_37_erase_partial_overlap_not_contiguous",
     [('E', 30, 3), ('E', 34, 3)],
     [('E', 30, 3), ('E', 34, 3)]),

    ("cc_38_duplicate_writes_different_data",
     [('W', 15, 'X'), ('W', 15, 'Y')],
     [('W', 15, 'Y')]),

    ("cc_39_duplicate_erases_same_range",
     [('E', 60, 3), ('E', 60, 3)],
     [('E', 60, 3)]),

    ("cc_40_write_inside_erase_kept",
     [('E', 0, 3), ('W', 1, 'A')],
     [('E', 0, 3), ('W', 1, 'A')]),

    # ──────────────── 다양한 경계 테스트 ────────────────
    ("cc_41_write_outside_large_erase",
     [('E', 10, 5), ('W', 16, 'A')],
     [('E', 10, 5), ('W', 16, 'A')]),

    ("cc_42_write_at_erase_edge",
     [('E', 20, 5), ('W', 24, 'A')],
     [('E', 20, 5), ('W', 24, 'A')]),

    ("cc_43_write_then_erase_same_lba",
     [('W', 30, 'A'), ('E', 30, 1)],
     [('E', 30, 1)]),

    ("cc_44_late_erase_superset_wipes_all",
     [('E', 40, 3), ('W', 41, 'A'), ('E', 39, 4)],
     [('E', 39, 4)]),

    ("cc_45_three_writes_one_kept",
     [('W', 50, 'A'), ('W', 50, 'B'), ('W', 50, 'B')],
     [('W', 50, 'B')]),

    ("cc_46_overwrite_two_lbas",
     [('W', 60, 'A'), ('W', 61, 'B'), ('W', 60, 'C')],
     [('W', 60, 'C'), ('W', 61, 'B')]),

    ("cc_47_identical_erase_twice",
     [('E', 70, 3), ('E', 70, 3)],
     [('E', 70, 3)]),

    ("cc_48_overlap_chain_many_erases",
     [('E', 80, 3), ('E', 81, 3), ('E', 82, 3)],
     [('E', 80, 5)]),

    ("cc_49_out_of_order_erase_merge",
     [('E', 10, 2), ('E', 14, 2), ('E', 12, 2)],
     [('E', 10, 6)]),

    ("cc_50_complex_erase_merge_unsorted",
     [('E', 30, 3), ('E', 31, 4), ('E', 29, 2)],
     [('E', 29, 6)]),

    # ──────────────── 복합 시퀀스 혼합 ────────────────
    ("cc_51_write_erase_write_erase_same_lba",
     [('W', 20, 'A'), ('E', 20, 1), ('W', 20, 'B'), ('E', 20, 1)],
     [('E', 20, 1), ('W', 20, 'B')]),

    ("cc_52_overwrite_then_partial_erase",
     [('W', 5, 'A'), ('W', 6, 'B'), ('W', 5, 'C'), ('E', 5, 1)],
     [('E', 5, 1), ('W', 6, 'B')]),

    ("cc_53_zero_write_middle_kept_last",
     [('W', 10, 'A'), ('W', 10, '0x00000000'), ('W', 10, 'B')],
     [('W', 10, 'B')]),

    ("cc_54_write_then_nonoverlapping_erase",
     [('W', 20, 'A'), ('E', 30, 3)],
     [('E', 30, 3), ('W', 20, 'A')]),

    ("cc_55_four_writes_some_erased",
     [('W', 10, 'A'), ('W', 11, 'B'), ('W', 12, 'C'), ('W', 13, 'D'), ('E', 11, 2)],
     [('E', 11, 2), ('W', 10, 'A'), ('W', 13, 'D')]),

    ("cc_56_big_erase_then_small_inside",
     [('E', 40, 10), ('E', 42, 2)],
     [('E', 40, 10)]),

    ("cc_57_small_erase_then_big_superset",
     [('E', 60, 2), ('E', 59, 4)],
     [('E', 59, 4)]),

    ("cc_58_chain_break_write_then_merge",
     [('E', 70, 2), ('W', 72, 'A'), ('E', 72, 2), ('E', 74, 2)],
     [('E', 70, 6)]),

    ("cc_59_adjacent_erase_chain_write_outside",
     [('E', 70, 2), ('E', 72, 2), ('W', 74, 'A')],
     [('E', 70, 4), ('W', 74, 'A')]),

    ("cc_60_adjacent_erase_over_limit_plus_write",
     [('E', 0, 6), ('E', 6, 5), ('W', 10, 'A')],
     [('E', 0, 6), ('E', 6, 5), ('W', 10, 'A')]),

    ("cc_61_write_high_lba_then_erase",
     [('W', 95, 'A'), ('E', 94, 3)],
     [('E', 94, 3)]),

    ("cc_62_write_low_lba_then_erase",
     [('W', 0, 'A'), ('E', 0, 1)],
     [('E', 0, 1)]),

    ("cc_63_merge_erases_to_boundary_limit",
     [('E', 90, 5), ('E', 95, 5)],
     [('E', 90, 10)]),

    ("cc_64_over_limit_boundary_no_merge",
     [('E', 88, 7), ('E', 95, 5)],
     [('E', 88, 7), ('E', 95, 5)]),

    ("cc_65_erase_then_two_writes_inside",
     [('E', 10, 4), ('W', 10, 'A'), ('W', 13, 'B')],
     [('E', 10, 4), ('W', 10, 'A'), ('W', 13, 'B')]),

    ("cc_66_partial_erase_only_second_write",
     [('W', 20, 'A'), ('W', 21, 'B'), ('E', 21, 1)],
     [('E', 21, 1), ('W', 20, 'A')]),

    ("cc_67_partial_erase_first_write",
     [('W', 30, 'A'), ('W', 31, 'B'), ('E', 30, 1)],
     [('E', 30, 1), ('W', 31, 'B')]),

    ("cc_68_multi_erase_overrides_all",
     [('W', 40, 'A'), ('E', 40, 3), ('W', 41, 'B'), ('E', 39, 5)],
     [('E', 39, 5)]),

    ("cc_69_complex_erase_write_chain",
     [('W', 5, 'A'), ('E', 10, 2), ('W', 15, 'B'), ('E', 12, 4), ('W', 18, 'C')],
     [('E', 10, 6), ('W', 5, 'A'), ('W', 18, 'C')]),

    ("cc_70_many_writes_some_erased",
     [('W', 0, 'A'), ('W', 1, 'B'), ('W', 2, 'C'), ('E', 1, 2), ('W', 3, 'D')],
     [('E', 1, 2), ('W', 0, 'A'), ('W', 3, 'D')]),

    ("cc_71_two_writes_each_overwritten",
     [('W', 10, 'A'), ('W', 11, 'B'), ('W', 10, 'C'), ('W', 11, 'D')],
     [('W', 10, 'C'), ('W', 11, 'D')]),

    ("cc_72_duplicate_erases_after_overwrites",
     [('W', 50, 'A'), ('E', 49, 3), ('W', 50, 'B'), ('E', 50, 1)],
     [('E', 49, 3)]),

    ("cc_73_write_then_erase_then_write_other",
     [('W', 60, 'A'), ('E', 60, 1), ('W', 61, 'B')],
     [('E', 60, 1), ('W', 61, 'B')]),

    ("cc_74_erase_write_erase_merge",
     [('E', 10, 2), ('W', 11, 'A'), ('E', 11, 1)],
     [('E', 10, 2)]),

    ("cc_75_adjacent_erases_fill_to_limit",
     [('E', 0, 5), ('E', 5, 5)],
     [('E', 0, 10)]),

    ("cc_76_adjacent_erases_exceed_limit",
     [('E', 0, 5), ('E', 5, 6)],
     [('E', 0, 5), ('E', 5, 6)]),

    ("cc_77_smaller_erase_inside_bigger",
     [('E', 10, 7), ('E', 12, 5)],
     [('E', 10, 7)]),

    ("cc_78_two_large_overlaps_exceed_limit",
     [('E', 0, 8), ('E', 5, 8)],
     [('E', 0, 8), ('E', 5, 8)]),

    ("cc_79_multiple_writes_then_erases_merge",
     [('W', 5, 'A'), ('W', 6, 'B'), ('W', 7, 'C'), ('E', 5, 1), ('E', 6, 2)],
     [('E', 5, 3)]),

    ("cc_80_interleaved_write_erase_long_chain",
     [('W', 10, 'A'), ('E', 10, 1), ('W', 10, 'B'), ('E', 10, 1), ('W', 10, 'C')],
     [('E', 10, 1), ('W', 10, 'C')]),

    ("cc_81_write_then_adjacent_erase_chain",
     [('W', 0, 'A'), ('E', 1, 3), ('E', 4, 3)],
     [('E', 1, 6), ('W', 0, 'A')]),

    ("cc_82_write_inside_erase_chain_blocks",
     [('E', 10, 4), ('W', 12, 'A'), ('E', 14, 4)],
     [('E', 10, 4), ('E', 14, 4), ('W', 12, 'A')]),

    ("cc_83_write_after_merged_erases",
     [('E', 20, 3), ('E', 23, 2), ('W', 25, 'A')],
     [('E', 20, 5), ('W', 25, 'A')]),

    ("cc_84_long_chain_exact_limit",
     [('E', 30, 2), ('E', 32, 2), ('E', 34, 2), ('E', 36, 2), ('E', 38, 2)],
     [('E', 30, 10)]),

    ("cc_85_long_chain_exceeds_limit",
     [('E', 30, 2), ('E', 32, 2), ('E', 34, 2), ('E', 36, 2), ('E', 38, 3)],
     [('E', 30, 8), ('E', 38, 3)]),

    ("cc_86_low_boundary_write_then_erase",
     [('W', 0, 'A'), ('E', 0, 2)],
     [('E', 0, 2)]),

    ("cc_87_high_boundary_write_then_erase",
     [('W', 99, 'A'), ('E', 98, 2)],
     [('E', 98, 2)]),

    ("cc_88_single_erase_size_10_end",
     [('E', 90, 10)],
     [('E', 90, 10)]),

    ("cc_89_overlap_write_and_double_erase",
     [('E', 50, 4), ('W', 52, 'A'), ('E', 52, 4)],
     [('E', 50, 6)]),

    ("cc_90_alternate_write_erase_various",
     [('W', 20, 'A'), ('E', 20, 1), ('W', 21, 'B'), ('E', 21, 1), ('W', 20, 'C')],
     [('E', 20, 1), ('E', 21, 1), ('W', 20, 'C')]),

    ("cc_91_erase_write_adjacent_merge",
     [('W', 10, 'A'), ('E', 8, 3), ('E', 11, 2)],
     [('E', 8, 5)]),

    ("cc_92_two_erases_swap_order_merge",
     [('W', 30, 'A'), ('E', 31, 2), ('E', 29, 2)],
     [('E', 29, 4)]),

    ("cc_93_duplicate_write_same_value",
     [('W', 50, 'A'), ('W', 50, 'A')],
     [('W', 50, 'A')]),

    ("cc_94_ten_small_erases_merge_to_limit",
     [('E', 0, 1), ('E', 1, 1), ('E', 2, 1), ('E', 3, 1), ('E', 4, 1),
      ('E', 5, 1), ('E', 6, 1), ('E', 7, 1), ('E', 8, 1), ('E', 9, 1)],
     [('E', 0, 10)]),

    ("cc_95_eleven_small_erases_split",
     [('E', 0, 1), ('E', 1, 1), ('E', 2, 1), ('E', 3, 1), ('E', 4, 1),
      ('E', 5, 1), ('E', 6, 1), ('E', 7, 1), ('E', 8, 1), ('E', 9, 1),
      ('E', 10, 1)],
     [('E', 0, 10), ('E', 10, 1)]),

    ("cc_96_write_and_erase_shared_bounds",
     [('W', 25, 'A'), ('W', 26, 'B'), ('E', 26, 1), ('W', 25, 'C')],
     [('E', 26, 1), ('W', 25, 'C')]),

    ("cc_97_erase_merge_near_device_end",
     [('E', 92, 3), ('E', 95, 4)],
     [('E', 92, 7)]),

    ("cc_98_two_erases_reverse_order_merge",
     [('E', 1, 1), ('E', 0, 1)],
     [('E', 0, 2)]),

    ("cc_99_write_split_multiple_erases",
     [('E', 10, 2), ('W', 11, 'A'), ('E', 12, 2), ('W', 13, 'B'), ('E', 14, 2)],
     [('E', 10, 2), ('E', 12, 2), ('E', 14, 2), ('W', 11, 'A'), ('W', 13, 'B')]),

    ("cc_100_maximum_complex_interleaving",
     [('W', 5, 'A'), ('E', 4, 4), ('W', 6, 'B'), ('E', 8, 2),
      ('E', 6, 3), ('W', 9, 'C'), ('E', 4, 6)],
     [('E', 4, 6)]),
]

extra_corner_cases = [

    # ────────── ① “여러 번 쓰기(Overwrite)만” ──────────
    ("corner_001_multi_overwrite_one_lba",
     [('W', 10, 'D1'), ('W', 10, 'D2'), ('W', 10, 'D3')],
     [('W', 10, 'D3')]),

    ("corner_002_identical_writes_same_data",
     [('W', 20, 'X'), ('W', 20, 'X'), ('W', 20, 'X')],
     [('W', 20, 'X')]),

    ("corner_003_interleave_overwrite",
     [('W', 5, 'A'), ('W', 6, 'B'), ('W', 5, 'C')],
     [('W', 5, 'C'), ('W', 6, 'B')]),

    ("corner_004_two_lbas_both_overwritten",
     [('W', 7, 'X'), ('W', 8, 'Y'), ('W', 7, 'Z'), ('W', 8, 'Y2')],
     [('W', 7, 'Z'), ('W', 8, 'Y2')]),

    ("corner_005_write_then_erase_same_lba",
     [('W', 15, 'D1'), ('E', 15, 1)],
     [('E', 15, 1)]),

    ("corner_006_two_writes_then_big_erase",
     [('W', 30, 'D1'), ('W', 31, 'D2'), ('E', 29, 5)],
     [('E', 29, 5)]),

    ("corner_007_e_w_e_chain_single_lba",
     [('E', 40, 1), ('W', 40, 'D1'), ('E', 40, 1)],
     [('E', 40, 1)]),

    ("corner_008_lba0_overwrites_then_erase",
     [('W', 0, 'A'), ('W', 0, 'B'), ('E', 0, 1)],
     [('E', 0, 1)]),

    ("corner_009_lba99_double_overwrite",
     [('W', 99, 'D1'), ('W', 99, 'D2')],
     [('W', 99, 'D2')]),

    ("corner_010_overwrite_plus_independent_erase",
     [('W', 50, 'D1'), ('W', 50, 'D2'), ('W', 51, 'D3'), ('E', 51, 1)],
     [('W', 50, 'D2'), ('E', 51, 1)]),

    ("corner_011_sequential_writes_some_overwritten",
     [('W', 25, 'A1'), ('W', 26, 'A2'), ('W', 27, 'A3'), ('W', 26, 'B2')],
     [('W', 25, 'A1'), ('W', 26, 'B2'), ('W', 27, 'A3')]),

    ("corner_012_duplicate_writes_identical_value",
     [('W', 60, 'D'), ('W', 60, 'D')],
     [('W', 60, 'D')]),

    ("corner_013_write_outside_erase_range",
     [('W', 10, 'X'), ('E', 12, 1)],
     [('W', 10, 'X'), ('E', 12, 1)]),

    ("corner_014_overlapping_erases_merge_to_six",
     [('E', 10, 4), ('E', 12, 4)],
     [('E', 10, 6)]),

    ("corner_015_erase_subset_removed_by_superset",
     [('E', 20, 2), ('E', 19, 4)],
     [('E', 19, 4)]),

    # ────────── ② “Erase → Erase” 관계 ──────────
    ("corner_016_big_then_small_inside",
     [('E', 30, 5), ('E', 32, 1)],
     [('E', 30, 5)]),

    ("corner_017_triplicate_identical_erases",
     [('E', 24, 3), ('E', 24, 3), ('E', 24, 3)],
     [('E', 24, 3)]),

    ("corner_018_chain_merging_exact_size10",
     [('E', 0, 5), ('E', 5, 5)],
     [('E', 0, 10)]),

    ("corner_019_contiguous_erases_exceed_size10",
     [('E', 40, 6), ('E', 46, 5)],
     [('E', 40, 10), ('E', 50, 1)]),

    ("corner_020_three_erases_overlap_to_eight",
     [('E', 5, 3), ('E', 7, 3), ('E', 9, 2)],
     [('E', 5, 6)]),

    ("corner_021_partial_overlap_no_full_cover",
     [('E', 50, 4), ('E', 52, 4)],
     [('E', 50, 6)]),

    ("corner_022_gap_of_one_prevents_merge",
     [('E', 70, 3), ('E', 74, 3)],
     [('E', 70, 3), ('E', 74, 3)]),

    ("corner_023_adjacent_at_lba0",
     [('E', 0, 2), ('E', 2, 2)],
     [('E', 0, 4)]),

    ("corner_024_adjacent_at_lba99_edge",
     [('E', 94, 5), ('E', 99, 1)],
     [('E', 94, 6)]),

    ("corner_025_overlap_creates_size9_through_merge",
     [('E', 10, 5), ('E', 12, 4)],
     [('E', 10, 6)]),

    ("corner_026_overlap_but_total11_not_merge",
     [('E', 0, 4), ('E', 4, 4), ('E', 8, 3)],
     [('E', 0, 10), ('E', 10, 1)]),

    ("corner_027_overlap_exact_size10_with_write_inside",
     [('E', 10, 4), ('W', 12, 'X'), ('E', 13, 3)],
     [('E', 10, 6), ('W', 12, 'X')]),

    ("corner_028_overlap_size11_with_write_inside_no_merge",
     [('E', 0, 6), ('W', 6, 'X'), ('E', 7, 5)],
     [('E', 0, 10), ('E', 10, 2), ('W', 6, 'X')]),

    ("corner_029_first_erase_removed_by_second_superset",
     [('E', 10, 2), ('E', 8, 6)],
     [('E', 8, 6)]),

    ("corner_030_partial_superset_keeps_both",
     [('E', 20, 6), ('E', 24, 4)],
     [('E', 20, 8)]),

    # ────────── ③ “Erase → Write” / “Write → Erase” 혼합 ──────────
    ("corner_031_erase_split_by_mid_write",
     [('E', 80, 5), ('W', 82, 'X')],
     [('E', 80, 5), ('W', 82, 'X')]),

    ("corner_032_e_w_e_different_addresses",
     [('E', 0, 3), ('W', 1, 'A'), ('E', 2, 3)],
     [('E', 0, 5), ('W', 1, 'A')]),

    ("corner_033_write_then_two_superseding_erases",
     [('W', 10, 'X'), ('E', 9, 2), ('E', 8, 5)],
     [('E', 8, 5)]),

    ("corner_034_disjoint_erase_and_write",
     [('E', 10, 2), ('W', 13, 'A')],
     [('E', 10, 2), ('W', 13, 'A')]),

    ("corner_035_write_inside_first_erase_then_bigger_erase",
     [('W', 20, 'A'), ('E', 19, 3), ('W', 20, 'B')],
     [('E', 19, 3), ('W', 20, 'B')]),

    ("corner_036_write_erased_by_later_superset",
     [('E', 30, 2), ('W', 30, 'X'), ('E', 29, 4)],
     [('E', 29, 4)]),

    ("corner_037_two_writes_later_big_erase_all",
     [('W', 40, 'A'), ('W', 42, 'B'), ('E', 39, 5)],
     [('E', 39, 5)]),

    ("corner_038_multi_overwrite_then_final_erase",
     [('W', 50, 'A'), ('W', 50, 'B'), ('E', 50, 1)],
     [('E', 50, 1)]),

    ("corner_039_multi_overwrite_no_erase",
     [('W', 60, 'A'), ('W', 60, 'B'), ('W', 60, 'C')],
     [('W', 60, 'C')]),

    ("corner_040_erase_then_final_write_only",
     [('E', 70, 1), ('W', 70, 'A')],
     [('W', 70, 'A')]),

    ("corner_041_erase_big_then_partial_write_outside",
     [('E', 80, 6), ('W', 85, 'Z')],
     [('E', 80, 5), ('W', 85, 'Z')]),

    ("corner_042_write_gap_between_erases",
     [('E', 10, 2), ('W', 12, 'Y'), ('E', 13, 2)],
     [('E', 10, 5), ('W', 12, 'Y')]),

    ("corner_043_adjacent_erases_with_middle_write_exceed10",
     [('E', 0, 6), ('W', 6, 'M'), ('E', 7, 5)],
     [('E', 0, 10), ('E', 10, 2), ('W', 6, 'M')]),

    ("corner_044_write_on_boundary_of_erase",
     [('E', 20, 4), ('W', 24, 'Q')],
     [('E', 20, 4), ('W', 24, 'Q')]),

    ("corner_045_write_exactly_in_the_middle",
     [('E', 50, 3), ('W', 51, 'MID')],
     [('E', 50, 3), ('W', 51, 'MID')]),

    ("corner_046_two_erases_wrap_single_write",
     [('E', 30, 2), ('W', 32, 'X'), ('E', 33, 2)],
     [('E', 30, 5), ('W', 32, 'X')]),

    ("corner_047_write_removed_by_following_erase_subset",
     [('W', 10, 'P'), ('E', 10, 1), ('E', 9, 2)],
     [('E', 9, 2)]),

    ("corner_048_scattered_writes_and_erases",
     [('W', 5, 'A'), ('E', 5, 1), ('W', 7, 'B'), ('E', 7, 1), ('W', 9, 'C')],
     [('E', 5, 1), ('E', 7, 1), ('W', 9, 'C')]),

    ("corner_049_erase_split_into_three_by_two_writes",
     [('E', 90, 5), ('W', 91, 'D1'), ('W', 93, 'D2')],
     [('E', 90, 5), ('W', 91, 'D1'), ('W', 93, 'D2')]),

    ("corner_050_write_then_adjacent_erases_merge_size10",
     [('W', 15, 'A'), ('E', 16, 4), ('E', 20, 6)],
     [('E', 16, 10), ('W', 15, 'A')]),

    # ────────── ④ 다양한 순서/크기/경계 케이스 ──────────
    ("corner_051_size_one_erases_chain_merge",
     [('E', 10, 1), ('E', 11, 1), ('E', 12, 1), ('E', 13, 1)],
     [('E', 10, 4)]),

    ("corner_052_size_one_chain_break_by_write",
     [('E', 10, 1), ('E', 11, 1), ('W', 12, 'V'), ('E', 13, 1)],
     [('E', 10, 4), ('W', 12, 'V')]),

    ("corner_053_max_size10_no_merge_with_neighbor",
     [('E', 0, 10), ('E', 10, 1)],
     [('E', 0, 10), ('E', 10, 1)]),

    ("corner_054_two_size10_cannot_merge",
     [('E', 20, 10), ('E', 30, 10)],
     [('E', 20, 10), ('E', 30, 10)]),

    ("corner_055_size9_and_size1_merge_to10",
     [('E', 40, 9), ('E', 49, 1)],
     [('E', 40, 10)]),

    ("corner_056_size9_and_size2_over10_no_merge",
     [('E', 40, 9), ('E', 49, 2)],
     [('E', 40, 10), ('E', 50, 1)]),

    ("corner_057_merge_three_erases_to_exact10",
     [('E', 60, 3), ('E', 63, 3), ('E', 66, 4)],
     [('E', 60, 10)]),

    ("corner_058_overwrite_after_two_erases",
     [('E', 70, 2), ('E', 72, 2), ('W', 71, 'Z')],
     [('E', 70, 4), ('W', 71, 'Z')]),

    ("corner_059_write_between_overlapping_erases",
     [('E', 10, 3), ('W', 11, 'A'), ('E', 10, 3)],
     [('E', 10, 3)]),

    ("corner_060_long_chain_size11_split",
     [('E', 0, 4), ('E', 4, 4), ('E', 8, 3)],
     [('E', 0, 10), ('E', 10, 1)]),

    ("corner_061_erase_then_write_outside_then_merge",
     [('E', 30, 3), ('W', 33, 'O'), ('E', 31, 3)],
     [('E', 30, 4)]),

    ("corner_062_write_at_last_lba_then_erase",
     [('W', 99, 'Z'), ('E', 99, 1), ('W', 99, 'Y')],
     [('W', 99, 'Y')]),

    ("corner_063_write_erase_write_three_lbas",
     [('W', 10, 'A'), ('E', 9, 3), ('W', 11, 'B')],
     [('E', 9, 2), ('W', 11, 'B')]),

    ("corner_064_non_overlapping_many_small_erases",
     [('E', 0, 1), ('E', 2, 1), ('E', 4, 1), ('E', 6, 1)],
     [('E', 0, 1), ('E', 2, 1), ('E', 4, 1), ('E', 6, 1)]),

    ("corner_065_overlapping_size_limit_edge",
     [('E', 10, 10), ('E', 20, 1)],
     [('E', 10, 10), ('E', 20, 1)]),

    ("corner_066_write_inside_max_size10_erase",
     [('E', 30, 10), ('W', 35, 'M')],
     [('E', 30, 10), ('W', 35, 'M')]),

    ("corner_067_gap_two_erases_chain_no_merge",
     [('E', 50, 2), ('E', 53, 2)],
     [('E', 50, 2), ('E', 53, 2)]),

    ("corner_068_gap_one_erases_merge",
     [('E', 70, 2), ('E', 72, 1)],
     [('E', 70, 3)]),

    ("corner_069_gap_one_chain_but_over10",
     [('E', 0, 6), ('E', 7, 5)],
     [('E', 0, 6), ('E', 7, 5)]),

    ("corner_070_two_writes_between_three_erases",
     [('E', 20, 2), ('W', 22, 'A'), ('E', 23, 2), ('W', 25, 'B'), ('E', 26, 2)],
     [('E', 20, 8), ('W', 22, 'A'), ('W', 25, 'B')]),

    # ────────── ⑤ 복합(랜덤형) 시퀀스 ──────────
    ("corner_071_random_mix_1",
     [('W', 3, 'A'), ('E', 1, 5), ('W', 4, 'B'), ('E', 0, 7)],
     [('E', 0, 7)]),

    ("corner_072_random_mix_2",
     [('E', 90, 3), ('W', 91, 'X'), ('E', 92, 2), ('W', 90, 'Y')],
     [('E', 92, 2), ('W', 90, 'Y'), ('W', 91, 'X')]),

    ("corner_073_random_mix_3",
     [('W', 10, 'A'), ('W', 12, 'B'), ('E', 11, 4), ('W', 14, 'C')],
     [('E', 11, 3), ('W', 10, 'A'), ('W', 14, 'C')]),

    ("corner_074_random_mix_4",
     [('E', 60, 2), ('W', 60, 'X'), ('W', 61, 'Y'), ('E', 59, 4)],
     [('E', 59, 4)]),

    ("corner_075_random_mix_5",
     [('W', 30, 'A'), ('E', 25, 10), ('W', 28, 'B'), ('W', 35, 'C')],
     [('E', 25, 10), ('W', 28, 'B'), ('W', 35, 'C')]),

    ("corner_076_random_mix_6",
     [('E', 10, 3), ('E', 12, 3), ('W', 11, 'X'), ('E', 15, 2)],
     [('E', 10, 7), ('W', 11, 'X')]),

    ("corner_077_random_mix_7",
     [('W', 0, 'A'), ('E', 0, 2), ('W', 1, 'B'), ('E', 1, 1)],
     [('E', 0, 2)]),

    ("corner_078_random_mix_8",
     [('E', 20, 4), ('W', 22, 'A'), ('W', 23, 'B'), ('E', 21, 5)],
     [('E', 20, 6)]),

    ("corner_079_random_mix_9",
     [('W', 98, 'X'), ('E', 95, 5)],
     [('E', 95, 5)]),

    ("corner_080_random_mix_10",
     [('E', 30, 3), ('W', 32, 'X'), ('W', 31, 'Y')],
     [('E', 30, 1), ('W', 31, 'Y'), ('W', 32, 'X')]),

    ("corner_081_random_mix_11",
     [('W', 45, 'A'), ('E', 40, 10)],
     [('E', 40, 10)]),

    ("corner_082_random_mix_12",
     [('E', 10, 2), ('W', 11, 'A'), ('E', 10, 4)],
     [('E', 10, 4)]),

    ("corner_083_random_mix_13",
     [('W', 55, 'A'), ('W', 55, 'B'), ('E', 50, 10)],
     [('E', 50, 10)]),

    ("corner_084_random_mix_14",
     [('E', 0, 4), ('W', 4, 'A'), ('E', 5, 4)],
     [('E', 0, 9), ('W', 4, 'A')]),

    ("corner_085_random_mix_15",
     [('W', 10, 'A'), ('E', 9, 3), ('W', 8, 'B')],
     [('E', 9, 3), ('W', 8, 'B')]),

    ("corner_086_random_mix_16",
     [('E', 80, 3), ('W', 82, 'Z'), ('E', 81, 4)],
     [('E', 80, 5)]),

    ("corner_087_random_mix_17",
     [('W', 20, 'A'), ('W', 21, 'B'), ('E', 19, 4), ('W', 20, 'C')],
     [('E', 19, 4), ('W', 20, 'C')]),

    ("corner_088_random_mix_18",
     [('E', 60, 5), ('W', 62, 'A'), ('E', 60, 5)],
     [('E', 60, 5)]),

    ("corner_089_random_mix_19",
     [('E', 30, 2), ('W', 30, 'A'), ('E', 31, 2)],
     [('E', 31, 2), ('W', 30, 'A')]),

    ("corner_090_random_mix_20",
     [('W', 5, 'A'), ('W', 6, 'B'), ('E', 5, 3), ('W', 5, 'C')],
     [('E', 6, 2), ('W', 5, 'C')]),

    ("corner_091_random_mix_21",
     [('E', 10, 1), ('W', 10, 'A'), ('E', 9, 3)],
     [('E', 9, 3)]),

    ("corner_092_random_mix_22",
     [('E', 90, 5), ('W', 92, 'V'), ('W', 91, 'U')],
     [('E', 90, 5), ('W', 91, 'U'), ('W', 92, 'V')]),

    ("corner_093_random_mix_23",
     [('W', 0, 'A'), ('E', 0, 3), ('W', 2, 'B')],
     [('E', 0, 2), ('W', 2, 'B')]),

    ("corner_094_random_mix_24",
     [('E', 40, 4), ('W', 40, 'A'), ('W', 42, 'B')],
     [('E', 41, 3), ('W', 40, 'A'), ('W', 42, 'B')]),

    ("corner_095_random_mix_25",
     [('W', 30, 'A'), ('E', 25, 10), ('W', 34, 'Z')],
     [('E', 25, 9), ('W', 34, 'Z')]),

    ("corner_096_random_mix_26",
     [('E', 50, 2), ('W', 50, 'A'), ('W', 51, 'B'), ('E', 49, 4)],
     [('E', 49, 4)]),

    ("corner_097_random_mix_27",
     [('W', 10, 'A'), ('E', 9, 2), ('W', 11, 'B'), ('E', 8, 4)],
     [('E', 8, 4)]),

    ("corner_098_random_mix_28",
     [('E', 60, 3), ('E', 63, 3), ('W', 65, 'A')],
     [('E', 60, 5), ('W', 65, 'A')]),

    ("corner_099_random_mix_29",
     [('W', 95, 'A'), ('E', 90, 10)],
     [('E', 90, 10)]),

    ("corner_100_random_mix_30",
     [('E', 0, 2), ('W', 2, 'A'), ('E', 1, 2)],
     [('E', 0, 3)]),  # E 3,0 effectively ignored

]

all_scenarios.extend(extra_corner_cases)

@pytest.mark.parametrize("scenario_id, input_cmds, expected_cmds", all_scenarios)
def test_all_optimization_scenarios(scenario_id, input_cmds, expected_cmds, command_buffer_with_cleanup):
    """
    모든 최적화 규칙이 결합된 최종 결과를 테스트합니다.
    지적해주신 케이스, 기본 케이스, 복합/코너 케이스를 모두 포함합니다.
    """
    # 실제 코드의 로직을 순서대로 실행하여 최종 결과를 얻습니다.
    result = run_full_optimization(command_buffer_with_cleanup, input_cmds)

    # 정렬 후 비교하여 순서에 상관없이 내용이 일치하는지 확인합니다.
    assert sort_commands(result) == sort_commands(expected_cmds)

