import numpy as np
from quaqsim import simulate_program

from qm.qua import *
import matplotlib.pyplot as plt


def test_allxy(transmon_pair_backend,
               transmon_pair_qua_config,
               config_to_transmon_pair_backend_map):

    n_avg = 1

    # All-XY sequences. The sequence names must match corresponding operation in the config
    sequence = [
        ("I", "I"),
        ("x180", "x180"),
        ("y180", "y180"),
        ("x180", "y180"),
        ("y180", "x180"),
        ("x90", "I"),
        ("y90", "I"),
        ("x90", "y90"),
        ("y90", "x90"),
        ("x90", "y180"),
        ("y90", "x180"),
        ("x180", "y90"),
        ("y180", "x90"),
        ("x90", "x180"),
        ("x180", "x90"),
        ("y90", "y180"),
        ("y180", "y90"),
        ("x180", "I"),
        ("y180", "I"),
        ("x90", "x90"),
        ("y90", "y90"),
    ]

    # All-XY macro generating the pulse sequences from a python list.
    def allXY(pulses):
        """
        Generate a QUA sequence based on the two operations written in pulses. Used to generate the all XY program.
        **Example:** I, Q = allXY(['I', 'y90'])

        :param pulses: tuple containing a particular set of operations to play. The pulse names must match corresponding
            operations in the config except for the identity operation that must be called 'I'.
        :return: two QUA variables for the 'I' and 'Q' quadratures measured after the sequence.
        """
        I_xy = declare(fixed)
        Q_xy = declare(fixed)
        # Play the 1st gate or wait if the gate is identity
        if pulses[0] != "I":
            play(pulses[0], "qubit_1")  # Either play the sequence
        else:
            wait(4 // 4, "qubit_1")  # or wait if sequence is identity
        # Play the 2nd gate or wait if the gate is identity
        if pulses[1] != "I":
            play(pulses[1], "qubit_1")  # Either play the sequence
        else:
            wait(4 // 4, "qubit_1")  # or wait if sequence is identity
        # Align the two elements to measure after playing the qubit gates.
        align("qubit_1", "resonator_1")
        # Measure the state of the resonator and return the two quadratures
        measure(
            "readout",
            "resonator_1",
            None,
            dual_demod.full("rotated_cos", "out1", "rotated_sin", "out2", I_xy),
            dual_demod.full("rotated_minus_sin", "out1", "rotated_cos", "out2", Q_xy),
        )
        return I_xy, Q_xy

    ###################
    # The QUA program #
    ###################
    with program() as ALL_XY:
        n = declare(int)
        r_ = declare(int)  # Index of the sequence to play
        # The result of each set of gates is saved in its own stream
        I_st = [declare_stream() for _ in range(len(sequence))]
        Q_st = [declare_stream() for _ in range(len(sequence))]
        n_st = declare_stream()

        with for_(n, 0, n < n_avg, n + 1):
            # Get a value from the pseudo-random number generator on the OPX FPGA
            # assign(r_, r.rand_int(len(sequence)))
            # Wait for the qubit to decay to the ground state - Can be replaced by active reset
            # Plays a random XY sequence
            # The switch/case method allows to map a python index (here "i") to a QUA number (here "r_") in order to switch
            # between elements in a python list (here "sequence") that cannot be converted into a QUA array (here because it
            # contains strings).
            with for_(r_, 0, r_ < 24, r_ + 1):
                with switch_(r_):
                    for i in range(len(sequence)):
                        with case_(i):
                            # Play the all-XY sequence corresponding to the drawn random number
                            I, Q = allXY(sequence[i])
                            # Save the 'I' & 'Q' quadratures to their respective streams
                            save(I, I_st[i])
                            save(Q, Q_st[i])
            save(n, n_st)

        with stream_processing():
            n_st.save("iteration")
            for i in range(len(sequence)):
                I_st[i].average().save(f"I{i}")
                Q_st[i].average().save(f"Q{i}")

    results = simulate_program(
        qua_program=ALL_XY,
        qua_config=transmon_pair_qua_config,
        qua_config_to_backend_map=config_to_transmon_pair_backend_map,
        backend=transmon_pair_backend,
        num_shots=100_000,
        schedules_to_plot=[5]
    )

    # plt.show()

    state_probabilities = np.array(results[0])
    I = state_probabilities
    # plt.plot(results[0], label=f"Simulated Q{0}")
    # plt.show()

    # Plot results
    plt.suptitle("All XY")
    plt.cla()
    plt.plot(I, "bx", label="Experimental data")
    plt.plot([np.max(I)] * 5 + [(np.mean(I))] * 12 + [np.min(I)] * 4, "r-", label="Expected value")
    plt.ylabel("I quadrature [a.u.]")
    plt.xticks(ticks=range(len(sequence)), labels=[str(el) for el in sequence], rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

    assert np.allclose(I, [np.max(I)] * 5 + [(np.mean(I))] * 12 + [np.min(I)] * 4, atol=0.1)