from output_interface import OutputInterface


class FileOutput(OutputInterface):
    OUTPUT_FILE = "ssd_output.txt"
    def __init__(self, write_mode="w"):
        self._write_mode = write_mode
    def write(self, text):
        with open(self.OUTPUT_FILE, self._write_mode) as f:
            f.write(text)
