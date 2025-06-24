import os.path
from ssd_modules.file_output.output_interface import OutputInterface


class FileOutput(OutputInterface):
    def __init__(self, output_file_path, write_mode="w"):
        self._write_mode = write_mode
        self._output_file_path = output_file_path
        if not os.path.exists(self._output_file_path):
            self.create_empty_file()

    def create_empty_file(self):
        with open(self._output_file_path, self._write_mode) as f:
            f.write("")

    def write(self, text):
        with open(self._output_file_path, self._write_mode) as f:
            f.write(text)
