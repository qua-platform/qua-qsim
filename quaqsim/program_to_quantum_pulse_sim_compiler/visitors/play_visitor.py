from quaqsim.program_ast.play import Play
from quaqsim.program_to_quantum_pulse_sim_compiler.context import Context

from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.timeline_IQ import TimelineIQ
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.expression_visitors.expression_visitor import \
    ExpressionVisitor
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.pulses import \
    waveform_shape
from quaqsim.program_to_quantum_pulse_sim_compiler.visitors.visitor import Visitor


class PlayVisitor(Visitor):
    def visit(self, node: Play, context: Context):
        e = node.element

        length = None
        if node.duration is not None:
            # the argument to the play command is in clock cycles for some reason
            length = 4 * ExpressionVisitor().visit(node.duration, context)

        amp_scaling_factor = None
        if node.amp is not None:
            amp_scaling_factor = ExpressionVisitor().visit(node.amp, context)

        length, [I_shape, Q_shape] = waveform_shape(node, context.qua_config, length, amp_scaling_factor)

        timeline = context.schedules.get_timeline(e)

        if isinstance(timeline, TimelineIQ):
            timeline.play_i(length, I_shape, name=node.operation)
            timeline.play_q(length, Q_shape, name=node.operation)
        else:
            raise NotImplementedError()
