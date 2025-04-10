from .expression_visitor import ExpressionVisitor
from ....program_ast.expressions import Reference
from ....program_ast.expressions.array_cell import ArrayCell


class ArrayCellVisitor:
    def visit(self, array_cell: dict) -> ArrayCell:
        expression_visitor = ExpressionVisitor()

        # todo: expression visitor should support reference visitor
        array_reference = Reference(array_cell['arrayVar']['name'])
        array_index = expression_visitor.visit(array_cell['index'])

        return ArrayCell(array=array_reference, index=array_index)
