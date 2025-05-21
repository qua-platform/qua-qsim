from .node import Node
from .expressions.expression import Expression
from typing import Optional


class Ramp(Node):
    def __init__(self, value: Expression, loc: Optional[Node] = None):
        self.loc = loc
        self.value = value
