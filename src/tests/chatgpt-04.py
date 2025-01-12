import numpy as np

def hardy_cross_method(flows, resistances, tolerance=1e-6, max_iterations=100):
    """
    Perform the Hardy Cross Method for a piping network with loops.
    
    Parameters:
    flows (list): Initial flow guesses for each pipe segment in the loops.
    resistances (list): Resistance values (e.g., head loss coefficient) for each pipe.
    tolerance (float): Convergence tolerance for the method.
    max_iterations (int): Maximum number of iterations to attempt.

    Returns:
    list: Converged flow rates for each pipe segment.
    """
    num_pipes = len(flows)
    iteration = 0

    while iteration < max_iterations:
        sum_fh = 0  # Sum of flow-resistance products
        sum_fq = 0  # Sum of flow-squared-resistance products

        # Calculate sum of fh and fq for the current iteration
        for i in range(num_pipes):
            fh = flows[i] * abs(flows[i]) * resistances[i]  # Flow * |Flow| * resistance (for direction)
            fq = abs(flows[i]) * resistances[i]  # Only magnitude in resistance calculation

            sum_fh += fh
            sum_fq += fq

        # Check if there is any correction needed
        if sum_fq == 0:
            print("Warning: Zero sum of flow-squared terms, may lead to division by zero.")
            break

        # Calculate correction
        correction = -sum_fh / (2 * sum_fq)

        # Apply correction to each flow in the correct direction
        for i in range(num_pipes):
            if flows[i] != 0:
                flows[i] += correction * (flows[i] / abs(flows[i]))  # Direction applied by sign of flow

        # Print debug information
        print(f"Iteration {iteration + 1}: Correction = {correction}")
        print(f"Updated flows: {flows}")

        # Convergence check
        if abs(correction) < tolerance:
            print(f"Converged after {iteration + 1} iterations.")
            break

        iteration += 1

    # Final convergence message if max iterations reached
    if iteration == max_iterations:
        print("Warning: Maximum iterations reached without convergence.")

    return flows

# Example usage with initial flows
initial_flows = [2.0, 1.0, -2.0, -2.0]  # Example initial flows in m³/s
resistances = [0.02, 0.02, 0.02, 0.02]      # Example resistance values (k factor for each pipe)

# Run the Hardy Cross method
converged_flows = hardy_cross_method(initial_flows, resistances)
print("Final converged flow rates:", converged_flows)
