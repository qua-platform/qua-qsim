from typing import Any


class Definition:
    def __init__(self, name: str, type: str, value: Any):
        self.name = name
        self.type = type
        self.value = value


class ArrayDefinition(Definition):
    def __init__(self, name: str, type: str, value: Any, size: int):
        self.size = size
        super().__init__(name, type, value)