# SSD 프로젝트 실행 방법 및 동작 설명

## 실행 방법

### 1. 셸 모드 실행
```bash
python shell.py
```
셸 모드를 실행하면 대화형 인터페이스가 시작되며 다양한 명령어를 입력할 수 있습니다.

### 2. 배치 스크립트 실행
```bash
python shell.py [배치_스크립트_파일]
```
배치 스크립트 파일을 인자로 제공하면 파일 내의 명령어들을 순차적으로 실행합니다.

### 3. ssd.py 직접 실행
SSD 모듈을 직접 커맨드라인에서 실행할 수 있습니다:

```bash
# 읽기 명령 (Read)
python ssd.py R <lba>
# 예: python ssd.py R 5 (5번 LBA 읽기)

# 쓰기 명령 (Write)
python ssd.py W <lba> <data>
# 예: python ssd.py W 10 0xABCDEF12 (10번 LBA에 0xABCDEF12 데이터 쓰기)

# 지우기 명령 (Erase)
python ssd.py E <lba> <size>
# 예: python ssd.py E 20 5 (20번 LBA부터 5개 블록 지우기)

# Flush 명령 (Flush)
python ssd.py F
```
- 오류가 발생하면 `ssd_output.txt` 파일에 `ERROR`가 출력 됩니다.
- Write/Erase 커맨드를 통한 결과는 `ssd_nand.txt`에 저장됩니다.

## 주요 동작

### SSD 주요 기능
이 프로젝트는 SSD의 동작을 시뮬레이션하는 프로그램으로, 다음과 같은 주요 기능을 제공합니다:

1. **읽기(Read)**: 특정 LBA에서 데이터를 읽어옵니다.
2. **쓰기(Write)**: 특정 LBA에 데이터를 씁니다.
3. **지우기(Erase)**: 특정 LBA 또는 LBA 범위의 데이터를 지웁니다.
4. **플러시(Flush)**: 버퍼에 임시 저장된 모든 명령어를 처리하여 실제 NAND 저장소에 영구적으로 반영합니다.

### 버퍼 기능 및 최적화 알고리즘

SSD에는 명령어를 저장하는 버퍼 기능이 구현되어 있으며, 버퍼 사이즈는 5입니다. 이 버퍼를 활용한 여러 최적화 알고리즘은 다음과 같습니다:

#### 1. Ignore Command (Write)
- 같은 LBA에 Write하는 명령어가 여러 개 들어온 경우, 마지막 유효한 명령어만 남기고 기존 명령어는 버퍼에서 삭제합니다.
- 예시:
  ```
  W 20 0xABCDABCD
  W 21 0x12341234
  W 20 0xEEEEFFFF  # 이 명령어만 유지되고, 첫 번째 W 20 명령은 무시됨
  W 21 0x12341234  # 두 번째 W 21과 중복되므로, 이 명령어만 유지
  ```

#### 2. Ignore Command (Erase)
- Erase 명령어를 수행하기 이전, 같은 LBA를 Write하거나 Erase하는 명령어가 존재한다면 해당 명령을 버퍼에서 제거합니다.
- 이전 Write/Erase 명령은 어차피 Erase로 덮어쓰이므로 수행할 필요가 없기 때문입니다.

#### 3. Merge Erase
- 두 개의 Erase 명령어가 연속적인 LBA 범위를 가질 수 있다면, 두 명령어를 하나의 명령어로 병합합니다.
- 단, Erase 명령어의 Size는 10보다 클 수 없다는 제약이 있습니다.
- 예시:
  ```
  E 10 5  # LBA 10-14 Erase
  E 15 5  # LBA 15-19 Erase
  ```
  위 두 명령은 `E 10 10` 하나의 명령으로 병합됩니다.

#### 4. Fast Read
- Read를 수행할 때, 먼저 Command Buffer를 확인합니다.
- 버퍼에 읽을 값이 있다면, 실제 NAND를 읽지 않고 버퍼로부터 값을 찾아 반환합니다.
- 이를 통해 읽기 성능을 향상시킬 수 있습니다.

### 셸 명령어

- `read [lba]`: 특정 LBA의 데이터를 읽습니다.
- `write [lba] [data]`: 특정 LBA에 데이터를 씁니다.
- `fullread`: 모든 LBA(0~99)의 데이터를 읽습니다.
- `fullwrite [data]`: 모든 LBA에 동일한 데이터를 씁니다.
- `erase [lba] [size]`: 특정 LBA부터 size만큼 데이터를 지웁니다.
- `erase_range [start_lba] [end_lba]`: 시작 LBA부터 끝 LBA까지 데이터를 지웁니다.
- `flush` : SSD 버퍼에 있는 데이터를 flush합니다.
- `help`: 도움말을 출력합니다.
- `exit`: 셸 모드를 종료합니다.

### 테스트 스크립트

프로젝트에는 SSD 동작을 검증하기 위한 4가지 테스트 스크립트가 포함되어 있습니다:

1. **test_script_1**: 모든 LBA에 순차적으로 데이터를 쓰고 읽어서 검증합니다.
2. **test_script_2**: 특정 LBA 세트(4,0,3,1,2)에 반복적으로 데이터를 쓰고 검증합니다.
3. **test_script_3**: 특정 LBA(0,99)에 200회 반복 쓰기/읽기 테스트를 수행합니다.
4. **test_script_4**: erase 명령 후 쓰기 및 읽기 테스트를 수행합니다.

모든 테스트는 "PASS" 또는 "FAIL" 결과를 반환합니다.

## 파일 구조

- `shell.py`: 사용자 인터페이스 및 명령어 처리
- `ssd.py`: SSD 동작을 시뮬레이션하는 코어 기능
- 로그는 기본적으로 설정된 파일에 저장됩니다

유효한 LBA 범위는 0~99이며, 모든 명령어는 이 범위 내에서 동작합니다.