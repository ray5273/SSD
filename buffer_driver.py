import os

EMPTY_BUFFER = "empty"
BUFFER_INDEX_START = 1
BUFFER_INDEX_END = 5
NUM_BUFFER_FILE_PARAMETERS = 4


class BufferDriver:
    def __init__(self):
        self.buffer_folder = "buffer_folder"
        self.make_buffer_folder()
        self.create_empty_files()

    def create_empty_files(self):
        for index in range(BUFFER_INDEX_START, BUFFER_INDEX_END + 1):
            is_file_exist = False
            for buffer_file in os.listdir(self.buffer_folder):
                if buffer_file.startswith(f"{index}_"):
                    is_file_exist = True
                    break
            if is_file_exist is False:
                self.make_buffer_file(f"{index}_" + EMPTY_BUFFER)

    def make_buffer_file(self, file_name):
        with open(os.path.join(self.buffer_folder, file_name), "w", encoding="utf-8") as f:
            pass

    def make_buffer_folder(self):
        if not os.path.exists(self.buffer_folder):
            os.makedirs(self.buffer_folder)

    def delete_buffer_files(self):
        for filename in os.listdir(self.buffer_folder):
            file_path = os.path.join(self.buffer_folder, filename)
            if os.path.isfile(file_path):  # 파일만 삭제
                os.remove(file_path)

    def get_parameters(self, buffer_file: str):
        parsed_file_name = buffer_file.split('_')
        commands = parsed_file_name[1:]
        command = commands[0]
        lba = commands[1]
        count_or_data = commands[2]
        if len(parsed_file_name) == NUM_BUFFER_FILE_PARAMETERS:
            lba = int(lba)
            if command == 'E':
                count_or_data = int(count_or_data)
            return tuple([command, lba, count_or_data])
        return None

    def get_list_from_buffer_files(self):
        buffers = []
        for index in range(BUFFER_INDEX_START, BUFFER_INDEX_END + 1):
            for buffer_file in os.listdir(self.buffer_folder):
                if not buffer_file.startswith(f"{index}_"):
                    continue
                try:
                    commands = self.get_parameters(buffer_file)
                    if commands is None:
                        continue
                except BaseException:
                    continue
                buffers.append(commands)
        return buffers

    def make_buffer_files_from_list(self, buffers):
        if len(buffers) > BUFFER_INDEX_END:
            return
        self.delete_buffer_files()
        empty_start_index = 0
        if len(buffers) > 0:
            for index, commands in enumerate(buffers):
                empty_start_index = index
                command = commands[0]
                lba = commands[1]
                count_or_data = commands[2]
                buffer_file_name = f"{index + 1}_{command}_{lba}_{count_or_data}"
                self.make_buffer_file(buffer_file_name)

            empty_start_index += 1

        while empty_start_index < 5:
            buffer_file_name = f"{empty_start_index + 1}_empty"
            self.make_buffer_file(buffer_file_name)
            empty_start_index += 1
