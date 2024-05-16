from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.context import Context
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.delay import Delay
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.instruction import Instruction
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.measure import Measure
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.phase_offset import PhaseOffset
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.play import Play
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.reset_phase import ResetPhase
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.reset_phase_visitor import \
    ResetPhaseVisitor
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.visitor import Visitor


class InstructionVisitor(Visitor):
    def visit(self, instruction: Instruction, instruction_context: Context):
        # local imports to avoid circular dependency
        from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.delay_visitor import \
            DelayVisitor
        from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.measure_visitor import \
            MeasureVisitor
        from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.phase_offset_visitor import \
            PhaseOffsetVisitor
        from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.play_visitor import \
            PlayVisitor
        # from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.simultaneous_visitor import \
        #     SimultaneousVisitor

        visitors = {
            Play: PlayVisitor(),
            Measure: MeasureVisitor(),
            Delay: DelayVisitor(),
            ResetPhase: ResetPhaseVisitor(),
            PhaseOffset: PhaseOffsetVisitor(),
            # Simultaneous: SimultaneousVisitor()
        }

        if type(instruction) in visitors:
            instruction.accept(visitors[type(instruction)], instruction_context)
        else:
            raise NotImplementedError(f"Unrecognized instruction type {instruction}")
