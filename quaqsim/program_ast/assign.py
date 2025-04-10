from typing import Union

from .expressions import Expression, Reference
from .expressions.array_cell import ArrayCell
from .node import Node


class Assign(Node):
    def __init__(self, target: Union[Reference, ArrayCell], value: Expression):
        self.target = target
        self.value = value
