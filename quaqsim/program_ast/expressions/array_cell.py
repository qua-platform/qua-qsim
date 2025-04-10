from . import Reference
from .expression import Expression


class ArrayCell(Expression):
    def __init__(self, array: Reference, index: Expression):
        self.array = array
        self.index = index

    def __str__(self):
        return f"{self.array}[{self.index}]"
