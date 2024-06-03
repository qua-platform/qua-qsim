import numpy as np
from qm.qua import *
from quaqsim import simulate_program

from qualang_tools.bakery.randomized_benchmark_c1 import c1_table
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def test_rb(transmon_pair_backend,
            transmon_pair_qua_config,
            config_to_transmon_pair_backend_map):

    num_of_sequences = 3  # Number of random sequences
    n_avg = 1  # Number of averaging loops for each random sequence
    max_circuit_depth = 140  # Maximum circuit depth
    delta_clifford = 20  #  Play each sequence with a depth step equals to 'delta_clifford - Must be > 1
    assert (max_circuit_depth / delta_clifford).is_integer(), "max_circuit_depth / delta_clifford must be an integer."
    seed = 345324  # Pseudo-random number generator seed
    # Flag to enable state discrimination if the readout has been calibrated (rotated blobs and threshold)
    state_discrimination = True
    # List of recovery gates from the lookup table
    inv_gates = [int(np.where(c1_table[i, :] == 0)[0][0]) for i in range(24)]

    def readout_macro(I=None, Q=None, threshold=0, state=None):
        if I is None:
            I = declare(fixed)
        if Q is None:
            Q = declare(fixed)
        if threshold is not None and state is None:
            state = declare(bool)

        measure(
            "readout",
            "resonator_1",
            None,
        )
        if threshold is not None:
            assign(state, I > threshold)
        return state, I, Q

    def power_law(power, a, b, p):
        return a * (p**power) + b

    def generate_sequence():
        cayley = declare(int, value=c1_table.flatten().tolist())
        inv_list = declare(int, value=inv_gates)
        current_state = declare(int)
        step = declare(int)
        sequence = declare(int, size=max_circuit_depth + 1)
        inv_gate = declare(int, size=max_circuit_depth + 1)
        i = declare(int)
        rand = Random(seed=seed)

        assign(current_state, 0)
        with for_(i, 0, i < max_circuit_depth, i + 1):
            assign(step, rand.rand_int(24))
            assign(current_state, cayley[current_state * 24 + step])
            assign(sequence[i], step)
            assign(inv_gate[i], inv_list[current_state])

        return sequence, inv_gate

    def play_sequence(sequence_list, depth):
        i = declare(int)
        with for_(i, 0, i <= depth, i + 1):
            with switch_(sequence_list[i], unsafe=True):
                with case_(0):
                    wait(4 // 4, "qubit_1")
                with case_(1):
                    play("x180", "qubit_1")
                with case_(2):
                    play("y180", "qubit_1")
                with case_(3):
                    play("y180", "qubit_1")
                    play("x180", "qubit_1")
                with case_(4):
                    play("x90", "qubit_1")
                    play("y90", "qubit_1")
                with case_(5):
                    play("x90", "qubit_1")
                    play("-y90", "qubit_1")
                with case_(6):
                    play("-x90", "qubit_1")
                    play("y90", "qubit_1")
                with case_(7):
                    play("-x90", "qubit_1")
                    play("-y90", "qubit_1")
                with case_(8):
                    play("y90", "qubit_1")
                    play("x90", "qubit_1")
                with case_(9):
                    play("y90", "qubit_1")
                    play("-x90", "qubit_1")
                with case_(10):
                    play("-y90", "qubit_1")
                    play("x90", "qubit_1")
                with case_(11):
                    play("-y90", "qubit_1")
                    play("-x90", "qubit_1")
                with case_(12):
                    play("x90", "qubit_1")
                with case_(13):
                    play("-x90", "qubit_1")
                with case_(14):
                    play("y90", "qubit_1")
                with case_(15):
                    play("-y90", "qubit_1")
                with case_(16):
                    play("-x90", "qubit_1")
                    play("y90", "qubit_1")
                    play("x90", "qubit_1")
                with case_(17):
                    play("-x90", "qubit_1")
                    play("-y90", "qubit_1")
                    play("x90", "qubit_1")
                with case_(18):
                    play("x180", "qubit_1")
                    play("y90", "qubit_1")
                with case_(19):
                    play("x180", "qubit_1")
                    play("-y90", "qubit_1")
                with case_(20):
                    play("y180", "qubit_1")
                    play("x90", "qubit_1")
                with case_(21):
                    play("y180", "qubit_1")
                    play("-x90", "qubit_1")
                with case_(22):
                    play("x90", "qubit_1")
                    play("y90", "qubit_1")
                    play("x90", "qubit_1")
                with case_(23):
                    play("-x90", "qubit_1")
                    play("y90", "qubit_1")
                    play("-x90", "qubit_1")

    with program() as rb:
        depth = declare(int)  # QUA variable for the varying depth
        depth_target = declare(int)  # QUA variable for the current depth (changes in steps of delta_clifford)
        # QUA variable to store the last Clifford gate of the current sequence which is replaced by the recovery gate
        saved_gate = declare(int)
        m = declare(int)  # QUA variable for the loop over random sequences
        n = declare(int)  # QUA variable for the averaging loop
        I = declare(fixed)  # QUA variable for the 'I' quadrature
        Q = declare(fixed)  # QUA variable for the 'Q' quadrature
        state = declare(bool)  # QUA variable for state discrimination
        # The relevant streams
        m_st = declare_stream()
        if state_discrimination:
            state_st = declare_stream()
        else:
            I_st = declare_stream()
            Q_st = declare_stream()

        with for_(m, 0, m < num_of_sequences, m + 1):  # QUA for_ loop over the random sequences
            sequence_list, inv_gate_list = generate_sequence()  # Generate the random sequence of length max_circuit_depth

            assign(depth_target, 0)  # Initialize the current depth to 0
            with for_(depth, 1, depth <= max_circuit_depth, depth + 1):  # Loop over the depths
                # Replacing the last gate in the sequence with the sequence's inverse gate
                # The original gate is saved in 'saved_gate' and is being restored at the end
                assign(saved_gate, sequence_list[depth])
                assign(sequence_list[depth], inv_gate_list[depth - 1])
                # Only played the depth corresponding to target_depth
                with if_((depth == 1) | (depth == depth_target)):
                    with for_(n, 0, n < n_avg, n + 1):  # Averaging loop
                        # Can be replaced by active reset
                        wait(1, "resonator_1")
                        # Align the two elements to play the sequence after qubit initialization
                        align("resonator_1", "qubit_1")
                        # The strict_timing ensures that the sequence will be played without gaps
                        with strict_timing_():
                            # Play the random sequence of desired depth
                            play_sequence(sequence_list, depth)
                        # Align the two elements to measure after playing the circuit.
                        align("qubit_1", "resonator_1")
                        # Make sure you updated the ge_threshold and angle if you want to use state discrimination
                        state, I, Q = readout_macro(threshold=0, state=state, I=I, Q=Q)
                        # Save the results to their respective streams
                        if state_discrimination:
                            save(state, state_st)
                        else:
                            save(I, I_st)
                            save(Q, Q_st)
                    # Go to the next depth
                    assign(depth_target, depth_target + delta_clifford)
                # Reset the last gate of the sequence back to the original Clifford gate
                # (that was replaced by the recovery gate at the beginning)
                assign(sequence_list[depth], saved_gate)
            # Save the counter for the progress bar
            save(m, m_st)

        with stream_processing():
            m_st.save("iteration")
            if state_discrimination:
                # saves a 2D array of depth and random pulse sequences in order to get error bars along the random sequences
                state_st.boolean_to_int().buffer(n_avg).map(FUNCTIONS.average()).buffer(
                    max_circuit_depth / delta_clifford + 1
                ).buffer(num_of_sequences).save("state")
                # returns a 1D array of averaged random pulse sequences vs depth of circuit for live plotting
                state_st.boolean_to_int().buffer(n_avg).map(FUNCTIONS.average()).buffer(
                    max_circuit_depth / delta_clifford + 1
                ).average().save("state_avg")
            else:
                I_st.buffer(n_avg).map(FUNCTIONS.average()).buffer(max_circuit_depth / delta_clifford + 1).buffer(
                    num_of_sequences
                ).save("I")
                Q_st.buffer(n_avg).map(FUNCTIONS.average()).buffer(max_circuit_depth / delta_clifford + 1).buffer(
                    num_of_sequences
                ).save("Q")
                I_st.buffer(n_avg).map(FUNCTIONS.average()).buffer(max_circuit_depth / delta_clifford + 1).average().save(
                    "I_avg"
                )
                Q_st.buffer(n_avg).map(FUNCTIONS.average()).buffer(max_circuit_depth / delta_clifford + 1).average().save(
                    "Q_avg"
                )

        results = simulate_program(
            qua_program=rb,
            qua_config=transmon_pair_qua_config,
            qua_config_to_backend_map=config_to_transmon_pair_backend_map,
            backend=transmon_pair_backend,
            num_shots=10_000,
            schedules_to_plot=[0]
        )

        plt.show()

        state_probabilities = np.array(results[0])
        plt.plot(results[0], label=f"Simulated Q{0}")
        plt.show()

        plt.show()
        #
        # # At the end of the program, fetch the non-averaged results to get the error-bars
        # if state_discrimination:
        #     results = fetching_tool(job, data_list=["state"])
        #     state = results.fetch_all()[0]
        #     value_avg = np.mean(state, axis=0)
        #     error_avg = np.std(state, axis=0)
        # else:
        #     results = fetching_tool(job, data_list=["I", "Q"])
        #     I, Q = results.fetch_all()
        #     value_avg = np.mean(I, axis=0)
        #     error_avg = np.std(I, axis=0)
        # # data analysis
        # pars, cov = curve_fit(
        #     f=power_law,
        #     xdata=x,
        #     ydata=value_avg,
        #     p0=[0.5, 0.5, 0.9],
        #     bounds=(-np.inf, np.inf),
        #     maxfev=2000,
        # )
        # stdevs = np.sqrt(np.diag(cov))
        #
        # print("#########################")
        # print("### Fitted Parameters ###")
        # print("#########################")
        # print(f"A = {pars[0]:.3} ({stdevs[0]:.1}), B = {pars[1]:.3} ({stdevs[1]:.1}), p = {pars[2]:.3} ({stdevs[2]:.1})")
        # print("Covariance Matrix")
        # print(cov)
        #
        # one_minus_p = 1 - pars[2]
        # r_c = one_minus_p * (1 - 1 / 2**1)
        # r_g = r_c / 1.875  # 1.875 is the average number of gates in clifford operation
        # r_c_std = stdevs[2] * (1 - 1 / 2**1)
        # r_g_std = r_c_std / 1.875
        #
        # print("#########################")
        # print("### Useful Parameters ###")
        # print("#########################")
        # print(
        #     f"Error rate: 1-p = {np.format_float_scientific(one_minus_p, precision=2)} ({stdevs[2]:.1})\n"
        #     f"Clifford set infidelity: r_c = {np.format_float_scientific(r_c, precision=2)} ({r_c_std:.1})\n"
        #     f"Gate infidelity: r_g = {np.format_float_scientific(r_g, precision=2)}  ({r_g_std:.1})"
        # )
        #
        # # Plots
        # plt.figure()
        # plt.errorbar(x, value_avg, yerr=error_avg, marker=".")
        # plt.plot(x, power_law(x, *pars), linestyle="--", linewidth=2)
        # plt.xlabel("Number of Clifford gates")
        # plt.ylabel("Sequence Fidelity")
        # plt.title("Single qubit RB")