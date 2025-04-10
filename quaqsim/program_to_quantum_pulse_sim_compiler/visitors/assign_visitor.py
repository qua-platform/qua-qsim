from quaqsim.program_ast.assign import Assign
from quaqsim.program_ast.expressions import Reference
from quaqsim.program_ast.expressions.array_cell import ArrayCell
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.expression_visitors.expression_visitor import \
    ExpressionVisitor
from quaqsim.program_to_quantum_pulse_sim_compiler.context import Context
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.visitor import Visitor


class AssignVisitor(Visitor):
    def visit(self, node: Assign, context: Context):
        value = ExpressionVisitor().visit(node.value, context)
        if isinstance(node.target, Reference):
            context.vars[node.target.name] = value
        elif isinstance(node.target, ArrayCell):
            index = ExpressionVisitor().visit(node.target.index, context)
            context.vars[node.target.array.name][index] = value
        else:
            raise NotImplementedError()

