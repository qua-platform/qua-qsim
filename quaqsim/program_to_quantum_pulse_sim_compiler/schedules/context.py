from dataclasses import dataclass

from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.timeline_single import \
    TimelineSingle


@dataclass
class Context:
    timeline: TimelineSingle
