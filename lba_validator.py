from command import CommandSpec, Command
from parameter_validator_interface import ParameterValidatorInterface


class LBAValidator(ParameterValidatorInterface):
    VALUE_LENGTH = 10

    def __init__(self, spec:CommandSpec, lba_length:int):
        super().__init__(spec)
        self.lba_length = lba_length

    def is_valid(self, params):
        if not isinstance(params, (list, tuple)):
            return False

        if len(params) < self._spec.minimum_num_params:
            return False

        command, address = params[0], params[1]
        if not address.isdigit():
            return False

        address = int(address)
        if not self._spec.is_valid_command(command):
            return False

        if len(params) != self._spec.get_num_params(command):
            return False

        if address >= self.lba_length or address < 0:
            return False

        if command == 'W':
            value = params[2]
            if len(value) != self.VALUE_LENGTH:
                return False
            try:
                _ = int(value, 16)
            except ValueError:
                return False
        return True
