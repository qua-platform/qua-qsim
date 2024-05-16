from quaqsim.program_ast.reset_phase import ResetPhase
from quaqsim.program_to_quantum_pulse_sim_compiler.context import Context
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.visitor import Visitor


class ResetFrameVisitor(Visitor):
    def visit(self, node: ResetPhase, context: Context):
        for element in node.elements:
            timeline = context.schedules.get_timeline(element)
            timeline.phase_offset(-timeline.current_phase)
