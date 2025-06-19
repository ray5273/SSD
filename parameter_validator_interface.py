from abc import ABC, abstractmethod
from command import CommandSpec


class ParameterValidatorInterface(ABC):
    def __init__(self, spec: CommandSpec):
        self._spec = spec

    @abstractmethod
    def is_valid(self, params):
        pass
