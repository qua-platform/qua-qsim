from typing import List, Optional

from .node import Node
from .program import Program


class If(Program):
    def __init__(self, body: List[Node], cond, else_ifs=None):
        super().__init__(body)
        self.cond = cond
        if else_ifs is None:
            else_ifs = []
        self.else_ifs = else_ifs
