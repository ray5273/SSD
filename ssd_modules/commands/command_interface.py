from abc import abstractmethod, ABC


class SSDCommandInterface(ABC):
    ERROR_MSG = "ERROR"
    def __init__(self, device, output_writer, command, num_params, lba_length=100):
        self._device = device
        self._command = command
        self._num_params = num_params
        self._output_writer = output_writer
        self._last_result = None
        self._lba_length = lba_length

    @property
    def result(self):
        return self._last_result

    @result.setter
    def result(self, value):
        self._output_writer.write(value)
        self._last_result = value

    def check_num_params(self, params:list) -> bool:
        return self._num_params == len(params)

    def common_param_validation(self, params:list) -> bool:
        if not isinstance(params, (list, tuple)):
            return False

        if len(params) != self._num_params:
            return False

        command, address = params[0], params[1]
        if command != self._command:
            return False

        if not address.isdigit():
            return False
        address = int(address)
        if address >= self._lba_length or address < 0:
            return False

        return True

    @abstractmethod
    def is_valid_param(self, params: list) -> bool:
        pass

    @abstractmethod
    def execute(self, params: list) -> str:
        pass