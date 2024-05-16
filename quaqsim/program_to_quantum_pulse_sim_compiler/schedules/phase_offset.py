from dataclasses import dataclass

from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.instruction import Instruction


@dataclass
class PhaseOffset(Instruction):
    phase: float
