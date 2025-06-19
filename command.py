from enum import StrEnum

class Command(StrEnum):
    READ  = "R"
    WRITE = "W"
    ERASE = "E"

class CommandSpec:
    NUM_PARAMS: dict[Command, int] = {Command.READ: 2, Command.WRITE: 3, Command.ERASE: 3}
    VALID_COMMANDS: list[Command] = [Command.READ, Command.WRITE, Command.ERASE]
    def get_num_params(self, command) -> int:
        return self.NUM_PARAMS.get(command, -1)

    def is_valid_command(self, command):
        if command in self.VALID_COMMANDS:
            return True
        return False

    @property
    def minimum_num_params(self):
        return min(self.NUM_PARAMS.values())