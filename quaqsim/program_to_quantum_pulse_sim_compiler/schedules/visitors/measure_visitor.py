from qiskit import pulse
from qiskit.pulse.channels import PulseChannel

from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.measure import (Measure)
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.visitor import Visitor


class MeasureVisitor(Visitor):
    def visit(self, instruction: Measure, instruction_context: PulseChannel):
        pulse.measure(
            qubits=instruction.qubit_index,
            registers=pulse.MemorySlot(instruction.qubit_index)
        )
