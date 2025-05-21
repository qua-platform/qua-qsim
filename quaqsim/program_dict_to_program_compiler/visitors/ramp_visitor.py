from typing import List

from .expression_visitors.expression_visitor import ExpressionVisitor
from .visitor import Visitor
from ...program_ast.ramp import Ramp
from ...program_ast.node import Node


class RampVisitor(Visitor):
    def visit(self, d: dict) -> List[Node]:
        value = ExpressionVisitor().visit(d["value"])

        for k in d:
            if k not in ["loc", "value"]:
                raise NotImplementedError(f"Unhandled ramp parameter {k}")

        return [Ramp(value)]
