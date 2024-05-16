# QuaQsim
A quantum simulator for QUA programs.

## Installation
pip install git+http://github.com/qua-plaftorm/quaqsim.git

## Example
### 1. Load your quantum parameters
```python
from quaqsim.architectures.transmon_pair import TransmonPair
from quaqsim.architectures import TransmonSettings
from quaqsim.architectures.transmon_pair_settings import TransmonPairSettings

settings = TransmonPairSettings(
    TransmonSettings(
        resonant_frequency=4860000000.0,
        anharmonicity=-320000000.0,
        rabi_frequency=0.22e9
    ),
    TransmonSettings(
        resonant_frequency=4970000000.0,
        anharmonicity=-320000000.0,
        rabi_frequency=0.26e9
    ),
    coupling_strength=0.002e9
)

transmon_pair = TransmonPair(settings)
```

### 2. Map your QUA elements to simulation channels
```python
from quaqsim.architectures.from_qua_channels import (
    TransmonPairBackendChannelReadout,
    TransmonPairBackendChannelIQ, 
    ChannelType
)

qubit_1_freq = 4860000000
qubit_2_freq = 4970000000.0

channel_map = {
    "qubit_1": TransmonPairBackendChannelIQ(
        qubit_index=0,
        carrier_frequency=qubit_1_freq,
        operator_i=transmon_pair.transmon_1_drive_operator(quadrature='I'),
        operator_q=transmon_pair.transmon_1_drive_operator(quadrature='Q'),
        type=ChannelType.DRIVE
    ),
    "qubit_1t2": TransmonPairBackendChannelIQ(
        qubit_index=0,
        carrier_frequency=qubit_2_freq,
        operator_i=transmon_pair.transmon_1_drive_operator(quadrature='I'),
        operator_q=transmon_pair.transmon_1_drive_operator(quadrature='Q'),
        type=ChannelType.CONTROL
    ),
    "qubit_2": TransmonPairBackendChannelIQ(
        qubit_index=1,
        carrier_frequency=qubit_2_freq,
        operator_i=transmon_pair.transmon_2_drive_operator(quadrature='I'),
        operator_q=transmon_pair.transmon_2_drive_operator(quadrature='Q'),
        type=ChannelType.DRIVE
    ),
    "resonator_1": TransmonPairBackendChannelReadout(0),
    "resonator_2": TransmonPairBackendChannelReadout(1),
}
```

### 3. Define a QUA Program
```python
from qm.qua import *

start, stop, step = -2, 2, 0.1
with program() as prog:
    a = declare(fixed)

    with for_(a, start, a < stop - 0.0001, a + step):
        play("x90"*amp(a), "qubit_1")
        play("x90"*amp(a), "qubit_2")

        align("qubit_1", "qubit_2", "resonator_1", "resonator_2")
        measure("readout", "resonator_1", None)
        measure("readout", "resonator_2", None)

```
### 4. Simulate!
```python
import numpy as np
import matplotlib.pyplot as plt

from quaqsim import simulate_program

results = simulate_program(
    qua_program=prog,
    qua_config=transmon_pair_qua_config,
    qua_config_to_backend_map=config_to_transmon_pair_backend_map,
    backend=transmon_pair_backend,
    num_shots=10_000,
)

for i, result in enumerate(results):
    plt.plot(np.arange(start, stop, step), results[i], '.-', label=f"Simulated Q{i}")
    plt.ylim(-0.05, 1.05)
plt.legend()
plt.show()
```
![](img/rabi_example.png)
