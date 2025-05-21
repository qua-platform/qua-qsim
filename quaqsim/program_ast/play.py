from typing import List, Optional, Union

from .expressions import Expression
from .node import Node
from .ramp import Ramp


class Play(Node):
    def __init__(
        self,
        operation: Union[str, Ramp],
        element: str,
        amp: Optional[Expression] = None,
        duration: Optional[Expression] = None,
    ):
        self.operation = operation
        self.element = element
        self.amp = amp
        self.duration = duration
