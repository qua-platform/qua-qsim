from quaqsim.program_ast.assign import Assign
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.expression_visitors.expression_visitor import \
    ExpressionVisitor
from quaqsim.program_to_quantum_pulse_sim_compiler.context import Context
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.visitor import Visitor


class AssignVisitor(Visitor):
    def visit(self, node: Assign, context: Context):
        context.vars[node.target] = ExpressionVisitor().visit(node.value, context)
