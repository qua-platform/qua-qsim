from typing import List

from .expression_visitors.expression_visitor import ExpressionVisitor
from ...program_ast.assign import Assign
from ...program_ast.node import Node
from .visitor import Visitor


class AssignVisitor(Visitor):
    def visit(self, d: dict) -> List[Node]:
        expression_visitor = ExpressionVisitor()
        if 'target' not in d:
            raise NotImplementedError()

        target = expression_visitor.visit(d['target'])
        value = expression_visitor.visit(d['expression'])

        return [Assign(target, value)]
