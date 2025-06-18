from parameter_validator_interface import ParameterValidatorInterface


class LBAValidator(ParameterValidatorInterface):
    MIN_NUM_RUN_PARAMETERS = 2
    def __init__(self, lba_length):
        super().__init__()
        self.lba_length = lba_length

    def is_valid(self, params):
        if len(params) < self.MIN_NUM_RUN_PARAMETERS:
            return False

        command, address = params[0], params[1]

        if command not in ['R', 'W']:
            return False

        if address >= self.lba_length:
            return False

        if command == 'W' and len(params) < 3:
            return False

        return True
