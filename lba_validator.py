from parameter_validator_interface import ParameterValidatorInterface


class LBAValidator(ParameterValidatorInterface):
    MIN_NUM_RUN_PARAMETERS = 2
    NUM_WRITE_PARAMETERS = 3
    AVAILABLE_COMMANDS = ['R', 'W']
    VALUE_LENGTH = 10

    def __init__(self, lba_length):
        super().__init__()
        self.lba_length = lba_length

    def is_valid(self, params):
        if not isinstance(params, (list, tuple)):
            return False

        if len(params) < self.MIN_NUM_RUN_PARAMETERS:
            return False

        command, address = params[0], params[1]
        if not address.isdigit():
            return False

        address = int(address)
        if command not in self.AVAILABLE_COMMANDS:
            return False

        if address >= self.lba_length:
            return False

        if command == 'W':
            if len(params) < self.NUM_WRITE_PARAMETERS:
                return False
            value = params[2]
            if len(value) != self.VALUE_LENGTH:
                return False
            try:
                _ = int(value, 16)
            except ValueError:
                return False
        return True
