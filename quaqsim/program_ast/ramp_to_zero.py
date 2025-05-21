from typing import Optional

from .expressions import Expression
from .node import Node


class RampToZero(Node):
    def __init__(self, element: str, duration: Optional[Expression] = None):
        self.element = element
        self.duration = duration
