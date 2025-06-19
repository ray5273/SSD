import datetime
import inspect
import os


class Logger:
    def __init__(self, is_stdout: bool, file_path: str, max_bytes: int, test_mode=False):
        self.is_stdout = is_stdout
        self.file_path = file_path
        self.max_bytes = max_bytes
        self.test_mode = test_mode

    def update_settings(self, is_stdout: bool, file_path: str, max_bytes: int):
        self.is_stdout = is_stdout
        self.file_path = file_path
        self.max_bytes = max_bytes

    # runner의 출력은 stdout에만 찍히면 되므로 이 메세지를 통해서 출력을함.
    def print_always(self, message: str, end="\n", flush=True):
        print(message, end=end, flush=flush)

    def print_log(self, message: str):
        """
        로그 메시지 출력 함수
        - stdout과 파일 모두 출력 또는 파일만 출력
        - 포맷: [날짜시간] 클래스명.함수명( ) : 로그메세지
        - 클래스명.함수명 부분은 최소 30자리 공간 확보
        """
        # 호출자 정보 가져오기
        frame = inspect.currentframe().f_back
        if frame:
            caller_class = "UnknownClass"
            caller_func = frame.f_code.co_name

            # 클래스 이름 찾기
            if 'self' in frame.f_locals:
                caller_class = frame.f_locals['self'].__class__.__name__
            elif 'cls' in frame.f_locals:
                caller_class = frame.f_locals['cls'].__name__

            caller_info = f"{caller_class}.{caller_func}()"
        else:
            caller_info = "Unknown.Unknown()"

        # 날짜시간 포맷 -> e.g. [26.01.01 17:04]
        now = datetime.datetime.now()
        timestamp = now.strftime("[%y.%m.%d %H:%M]")

        # 클래스명.함수명 부분 30자리로 패딩
        padded_caller = f"{caller_info:<30}"

        # 최종 로그 메시지 생성
        log_line = f"{timestamp} {padded_caller} : {message}"

        # stdout 출력
        if self.is_stdout:
            print(log_line)

        # 파일 MAX 크기 넘어갔을때 처리 및 until_{}.log 파일이 2개이상일때 처리
        if self.file_path:
            file_size = self.get_file_size()

            # 파일 크기가 max_bytes를 초과하면 백업하고 새 파일 생성
            if file_size > self.max_bytes:
                # 파일 이름과 확장자 분리
                file_dir = os.path.dirname(self.file_path)
                file_name = os.path.basename(self.file_path)

                # 백업 파일 이름 생성 (until_YYMMDD_Hh_Mm_Ss.log)
                timestamp_tmp = now.strftime("%y%m%d_%Hh_%Mm_%Ss")
                if self.test_mode:  # 테스트 모드일 때만 나노초 표시
                    # 마이크로초를 1000배 하여 나노초처럼 표시, 테스트시에는 파일이 겹칠 가능성이 높아서 이렇게 처리함.
                    # 실제 케이스에서는 강사님께서 그런 경우는 없다고함.
                    nano_part = now.microsecond * 1000
                    timestamp_tmp = f"{timestamp_tmp}_{nano_part:09d}"

                backup_name = f"until_{timestamp_tmp}.log"
                os.rename(self.file_path, backup_name)

                # 만약 until로 시작하는 파일이 이미 하나 존재하면 해당 파일의 확장자를 zip으로 바꿈
                # until로 시작하는 .log 파일 확인
                until_logs = self.get_until_log_files(file_dir)

                # until로 시작하는 .log 파일이 2개 이상이면 가장 최신 파일 뺴고 전부 zip으로 바꿈
                if len(until_logs) >= 2:
                    self.rename_when_two_log_exists(until_logs)

        # 파일에 로그 쓰기 : 마지막에 해야 latest가 남음
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
            f.flush()
            os.fsync(f.fileno())

    def rename_when_two_log_exists(self, until_logs):
        # 파일 이름에 생성 시간이 있으므로 파일 이름을 기준으로 정렬
        until_logs.sort()
        # 마지막 파일을 제외하고 .zip으로 교체함.
        for current_file in until_logs[:-1]:
            new_name = os.path.splitext(current_file)[0] + '.zip'
            # .log 파일을 .zip으로 변환함
            os.rename(current_file, new_name)

    def get_until_log_files(self, file_dir):
        until_logs = []
        for filename in os.listdir(file_dir if file_dir else '.'):
            if filename.startswith("until_") and filename.endswith(".log"):
                full_path = os.path.join(file_dir if file_dir else '.', filename)
                until_logs.append(full_path)
        return until_logs

    def get_file_size(self):
        # 파일 크기 확인
        file_size = 0
        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)
        return file_size


# 싱글톤 구현
LATEST_FILE = "latest.log"
MAX_BYTES = 10240
# 10KB, latest.log에 파일쓰기, stdout은 True가 Default
LOGGER = Logger(is_stdout=True, file_path=LATEST_FILE, max_bytes=MAX_BYTES, test_mode=False)
