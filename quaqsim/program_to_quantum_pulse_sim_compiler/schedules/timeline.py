from typing import Union

from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.timeline_IQ import TimelineIQ
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.timeline_single import \
    TimelineSingle

Timeline = Union[TimelineSingle, TimelineIQ]
