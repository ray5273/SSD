from abc import ABC, abstractmethod


class ParameterValidatorInterface(ABC):
    @abstractmethod
    def is_valid(self, params):
        pass
