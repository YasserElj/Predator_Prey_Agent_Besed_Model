import numpy as np
import numba
from numba import cuda
import math
from tqdm import tqdm

# Simulation parameters
GRID_SIZE = 20
MAX_STEPS = 1000
NUM_SIMULATIONS = 5  # Number of simulations per initial condition
THREADS_PER_BLOCK = 64  # Number of threads per block

# Define possible cell states
EMPTY = 0
PREY = 1
PREDATOR = 2

# GPU kernel for running the simulation
@cuda.jit
def run_simulation_kernel(prey_counts, predator_counts, grid_size, max_steps, results):
    # Each thread runs one simulation
    idx = cuda.grid(1)
    if idx >= prey_counts.size:
        return

    # Initialize RNG
    rng = numba.cuda.random.XORWOWRandomNumberGenerator(seed=idx)

    # Initialize grid and agents
    grid = cuda.local.array((GRID_SIZE, GRID_SIZE), numba.int8)
    energy_grid = cuda.local.array((GRID_SIZE, GRID_SIZE), numba.int8)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[y][x] = EMPTY
            energy_grid[y][x] = 0

    num_prey = prey_counts[idx]
    num_predators = predator_counts[idx]

    # Place prey
    for _ in range(num_prey):
        while True:
            x = rng.random_raw() % GRID_SIZE
            y = rng.random_raw() % GRID_SIZE
            if grid[y][x] == EMPTY:
                grid[y][x] = PREY
                break

    # Place predators
    for _ in range(num_predators):
        while True:
            x = rng.random_raw() % GRID_SIZE
            y = rng.random_raw() % GRID_SIZE
            if grid[y][x] == EMPTY:
                grid[y][x] = PREDATOR
                energy_grid[y][x] = 5  # Initial energy
                break

    step_count = 0
    while step_count < max_steps:
        step_count += 1
        # Movement arrays
        new_grid = cuda.local.array((GRID_SIZE, GRID_SIZE), numba.int8)
        new_energy_grid = cuda.local.array((GRID_SIZE, GRID_SIZE), numba.int8)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                new_grid[y][x] = grid[y][x]
                new_energy_grid[y][x] = energy_grid[y][x]

        # Move prey
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x] == PREY:
                    # Random move
                    dx = int(rng.uniform(-1, 2))
                    dy = int(rng.uniform(-1, 2))
                    nx = (x + dx) % GRID_SIZE
                    ny = (y + dy) % GRID_SIZE
                    if new_grid[ny][nx] == EMPTY:
                        new_grid[ny][nx] = PREY
                        new_grid[y][x] = EMPTY

        # Move predators
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x] == PREDATOR:
                    energy = energy_grid[y][x]
                    # Random move
                    dx = int(rng.uniform(-1, 2))
                    dy = int(rng.uniform(-1, 2))
                    nx = (x + dx) % GRID_SIZE
                    ny = (y + dy) % GRID_SIZE
                    if new_grid[ny][nx] == PREY:
                        # Eat prey
                        new_grid[ny][nx] = PREDATOR
                        new_energy_grid[ny][nx] = energy + 5
                        new_grid[y][x] = EMPTY
                        new_energy_grid[y][x] = 0
                    elif new_grid[ny][nx] == EMPTY:
                        # Move to empty cell
                        new_grid[ny][nx] = PREDATOR
                        new_energy_grid[ny][nx] = energy - 1
                        new_grid[y][x] = EMPTY
                        new_energy_grid[y][x] = 0
                    else:
                        # Stay in place and lose energy
                        new_energy_grid[y][x] = energy - 1

        # Update grids
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                grid[y][x] = new_grid[y][x]
                energy_grid[y][x] = new_energy_grid[y][x]
                # Remove predator if energy <= 0
                if grid[y][x] == PREDATOR and energy_grid[y][x] <= 0:
                    grid[y][x] = EMPTY
                    energy_grid[y][x] = 0

        # Check if prey or predators are extinct
        prey_remaining = False
        predators_remaining = False
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x] == PREY:
                    prey_remaining = True
                elif grid[y][x] == PREDATOR:
                    predators_remaining = True
        if not prey_remaining or not predators_remaining:
            break

    # Record result
    if not prey_remaining:
        results[idx] = 0  # All prey died
    elif not predators_remaining:
        results[idx] = 1  # All predators died
    else:
        results[idx] = 2  # Coexistence

def run_simulations_on_gpu(prey_counts, predator_counts):
    num_simulations = prey_counts.size
    # Allocate result array
    results = np.zeros(num_simulations, dtype=np.int8)
    # Copy data to device
    d_prey_counts = cuda.to_device(prey_counts)
    d_predator_counts = cuda.to_device(predator_counts)
    d_results = cuda.to_device(results)
    # Calculate grid dimensions
    threads_per_block = THREADS_PER_BLOCK
    blocks_per_grid = (num_simulations + (threads_per_block - 1)) // threads_per_block
    # Launch kernel
    run_simulation_kernel[blocks_per_grid, threads_per_block](d_prey_counts, d_predator_counts, GRID_SIZE, MAX_STEPS, d_results)
    # Copy results back to host
    results = d_results.copy_to_host()
    return results

# Main code
def main():
    # Define the ranges for ratio and density
    ratio_values = np.arange(0.1, 10.05, 0.1)  # Ratios from 0.1 to 10, step of 0.1
    density_values = np.arange(0.1, 1.02, 0.1)  # Densities from 0.1 to 1.0, step of 0.1
    X, Y = np.meshgrid(ratio_values, density_values)
    Z = np.zeros_like(X)

    # Total grid cells
    total_grid_cells = GRID_SIZE * GRID_SIZE

    # Prepare data for simulations
    prey_counts_list = []
    predator_counts_list = []
    positions = []

    for i, ratio in enumerate(ratio_values):
        for j, density in enumerate(density_values):
            N = int(density * total_grid_cells)
            if N < 2:
                N = 2  # Ensure at least one prey and one predator

            num_prey = int((ratio / (ratio + 1)) * N)
            num_predators = N - num_prey

            # Ensure at least one prey and one predator
            if num_prey == 0:
                num_prey = 1
                num_predators = N - 1
            if num_predators == 0:
                num_predators = 1
                num_prey = N - 1

            for _ in range(NUM_SIMULATIONS):
                prey_counts_list.append(num_prey)
                predator_counts_list.append(num_predators)
                positions.append((j, i))

    prey_counts_array = np.array(prey_counts_list, dtype=np.int32)
    predator_counts_array = np.array(predator_counts_list, dtype=np.int32)

    # Run simulations on GPU
    print("Running simulations on GPU...")
    results = run_simulations_on_gpu(prey_counts_array, predator_counts_array)

    # Aggregate results
    outcomes_dict = {}
    for idx, outcome in enumerate(results):
        position = positions[idx]
        if position not in outcomes_dict:
            outcomes_dict[position] = []
        outcomes_dict[position].append(outcome)

    # Determine the most common outcome for each initial condition
    for position, outcomes in outcomes_dict.items():
        most_common_outcome = Counter(outcomes).most_common(1)[0][0]
        j, i = position
        Z[j, i] = most_common_outcome

    # Plotting
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 8))
    extent = [ratio_values.min(), ratio_values.max(), density_values.min(), density_values.max()]
    plt.imshow(Z, extent=extent, origin='lower', aspect='auto', cmap='viridis')
    cbar = plt.colorbar(ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(['All Prey Died', 'All Predators Died', 'Coexistence'])
    plt.xlabel('Ratio (Prey / Predator)')
    plt.ylabel('Density (Agents per Grid Cell)')
    plt.title('Phase Diagram of Predator-Prey Simulation (GPU Accelerated)')
    plt.show()

if __name__ == "__main__":
    main()
