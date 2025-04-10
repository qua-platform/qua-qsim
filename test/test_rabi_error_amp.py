import numpy as np
from matplotlib import pyplot as plt
from qm.qua import *

from qualang_tools.loops import from_array
from quaqsim import simulate_program


def test_rabi(transmon_pair_backend, transmon_pair_qua_config, config_to_transmon_pair_backend_map):
    n_avg = 1
    # Pulse amplitude sweep (as a pre-factor of the qubit_1 pulse amplitude) - must be within [-2; 2)
    a_min = 0.99
    a_max = 1.01
    n_a = 21
    amplitudes = np.linspace(a_min, a_max, n_a)
    # Number of applied Rabi pulses sweep
    max_nb_of_pulses = 16  # Maximum number of qubit_1 pulses
    nb_of_pulses = np.arange(0, max_nb_of_pulses,
                             2)  # Always play an odd/even number of pulses to end up in the same state
    
    x180_amp = transmon_pair_qua_config['waveforms']['x180_q1_I_wf']['sample']

    with program() as power_rabi_err:
        n = declare(int)  # QUA variable for the averaging loop
        a = declare(fixed)  # QUA variable for the qubit_1 drive amplitude pre-factor
        n_rabi = declare(int)  # QUA variable for the number of qubit_1 pulses
        n2 = declare(int)  # QUA variable for counting the qubit_1 pulses
        I = declare(fixed)  # QUA variable for the measured 'I' quadrature
        Q = declare(fixed)  # QUA variable for the measured 'Q' quadrature
        I_st = declare_stream()  # Stream for the 'I' quadrature
        Q_st = declare_stream()  # Stream for the 'Q' quadrature
        n_st = declare_stream()  # Stream for the averaging iteration 'n'

        with for_(n, 0, n < n_avg, n + 1):  # QUA for_ loop for averaging
            with for_(*from_array(n_rabi, nb_of_pulses)):  # QUA for_ loop for sweeping the number of pulses
                with for_(*from_array(a, amplitudes)):  # QUA for_ loop for sweeping the pulse amplitude
                    # Loop for error amplification (perform many qubit_1 pulses with varying amplitudes)
                    with for_(n2, 0, n2 < n_rabi, n2 + 1):
                        play("x180" * amp(a), "qubit_1")
                    # Align the two elements to measure after playing the qubit_1 pulses.
                    align("qubit_1", "resonator_1")
                    # Measure the state of the resonator
                    # The integration weights have changed to maximize the SNR after having calibrated the IQ blobs.
                    measure(
                        "readout",
                        "resonator_1",
                        None,
                        dual_demod.full("rotated_cos", "out1", "rotated_sin", "out2", I),
                        dual_demod.full("rotated_minus_sin", "out1", "rotated_cos", "out2", Q),
                    )
                    # Save the 'I' & 'Q' quadratures to their respective streams
                    save(I, I_st)
                    save(Q, Q_st)
            # Save the averaging iteration to get the progress bar
            save(n, n_st)

        with stream_processing():
            # Cast the data into a 2D matrix, average the 2D matrices together and store the results on the OPX processor
            I_st.buffer(len(amplitudes)).buffer(len(nb_of_pulses)).average().save("I")
            Q_st.buffer(len(amplitudes)).buffer(len(nb_of_pulses)).average().save("Q")
            n_st.save("iteration")

        
    results = simulate_program(
        qua_program=power_rabi_err,
        qua_config=transmon_pair_qua_config,
        qua_config_to_backend_map=config_to_transmon_pair_backend_map,
        backend=transmon_pair_backend,
        num_shots=10_000,
        schedules_to_plot=[0]
    )
    plt.show()

    I = np.array(results[0]).reshape(
        len(nb_of_pulses),
        len(amplitudes)
    )
    # Plot results
    plt.suptitle("Power Rabi with error amplification")
    plt.subplot(211)
    plt.cla()
    plt.pcolor(amplitudes * x180_amp, nb_of_pulses, I)
    plt.xlabel("Rabi pulse amplitude [V]")
    plt.ylabel("# of Rabi pulses")
    plt.title("I quadrature [V]")
    plt.subplot(212)
    plt.cla()
    plt.plot(amplitudes * x180_amp, np.sum(I, axis=0))
    plt.xlabel("Rabi pulse amplitude [V]")
    plt.ylabel("Sum along the # of Rabi pulses")
    plt.pause(0.1)
    plt.tight_layout()
    plt.show()

    print(f"Optimal x180_amp = {amplitudes[np.argmax(np.sum(I, axis=0))] * x180_amp:.6f} V")

