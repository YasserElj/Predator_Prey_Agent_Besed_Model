import random
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm  # For progress bars
import multiprocessing as mp  # For parallel processing

# Simulation parameters
GRID_SIZE = 20
MAX_STEPS = 100
NUM_SIMULATIONS = 500  # Reduced to manage computational load

# Reproduction probabilities
SHEEP_REPRODUCE = 0.04  # Probability of sheep reproducing each step
WOLF_REPRODUCE = 0.05  # Probability of wolves reproducing each step

# Energy parameters
WOLF_GAIN_FROM_FOOD = 20  # Energy gained by wolves from eating prey
WOLF_INITIAL_ENERGY = 10  # Initial energy for wolves
WOLF_MOVE_COST = 1        # Energy cost per move for wolves

# Agent classes
class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Sheep do not have energy in this model

class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = WOLF_INITIAL_ENERGY  # Initial energy

def run_simulation(args):
    num_prey, num_predators = args
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    prey_list = []
    predator_list = []
    step_count = 0

    # Initialize prey
    for _ in range(num_prey):
        while True:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if grid[y][x] is None:
                prey = Prey(x, y)
                grid[y][x] = prey
                prey_list.append(prey)
                break

    # Initialize predators
    for _ in range(num_predators):
        while True:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if grid[y][x] is None or isinstance(grid[y][x], Prey):
                predator = Predator(x, y)
                grid[y][x] = predator
                predator_list.append(predator)
                break

    while step_count < MAX_STEPS and prey_list and predator_list:
        step_count += 1
        move_prey(grid, prey_list)
        move_predators(grid, prey_list, predator_list)

    # Determine the outcome
    if not prey_list:
        return 0  # All Prey Died
    elif not predator_list:
        return 1  # All Predators Died
    else:
        return 2  # Coexistence

def move_prey(grid, prey_list):
    for prey in prey_list[:]:
        x, y = prey.x, prey.y
        neighbors = get_neighbors(x, y)
        random.shuffle(neighbors)
        moved = False
        for nx, ny in neighbors:
            if grid[ny][nx] is None:
                grid[y][x] = None
                prey.x, prey.y = nx, ny
                grid[ny][nx] = prey
                moved = True
                break
        # Reproduction logic for prey
        if random.random() < SHEEP_REPRODUCE:
            # Reproduce
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if grid[ny][nx] is None:
                    new_prey = Prey(nx, ny)
                    prey_list.append(new_prey)
                    grid[ny][nx] = new_prey
                    break

def move_predators(grid, prey_list, predator_list):
    random.shuffle(predator_list)
    for predator in predator_list[:]:
        x, y = predator.x, predator.y
        neighbors = get_neighbors(x, y)
        prey_neighbors = []
        empty_neighbors = []
        for nx, ny in neighbors:
            if isinstance(grid[ny][nx], Prey):
                prey_neighbors.append((nx, ny))
            elif grid[ny][nx] is None:
                empty_neighbors.append((nx, ny))
        moved = False
        if prey_neighbors:
            nx, ny = random.choice(prey_neighbors)
            grid[y][x] = None
            prey = grid[ny][nx]
            prey_list.remove(prey)
            grid[ny][nx] = predator
            predator.x, predator.y = nx, ny
            predator.energy += WOLF_GAIN_FROM_FOOD
            moved = True
        elif empty_neighbors:
            nx, ny = random.choice(empty_neighbors)
            grid[y][x] = None
            grid[ny][nx] = predator
            predator.x, predator.y = nx, ny
            predator.energy -= WOLF_MOVE_COST
            moved = True
        else:
            predator.energy -= WOLF_MOVE_COST
        if not moved:
            predator.energy -= WOLF_MOVE_COST
        # Reproduction logic for predators
        if random.random() < WOLF_REPRODUCE and predator.energy > 1:
            # Reproduce
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if grid[ny][nx] is None:
                    new_predator = Predator(nx, ny)
                    predator_list.append(new_predator)
                    grid[ny][nx] = new_predator
                    # Split energy between parent and offspring
                    new_predator.energy = predator.energy // 2
                    predator.energy = predator.energy // 2
                    break
        if predator.energy <= 0:
            grid[predator.y][predator.x] = None
            predator_list.remove(predator)

def get_neighbors(x, y):
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % GRID_SIZE
            ny = (y + dy) % GRID_SIZE
            neighbors.append((nx, ny))
    return neighbors

# Define the ranges for ratio and density
ratio_values = np.arange(0.1, 10, 0.5)  # Adjusted for computational efficiency
density_values = np.arange(0.01, 1, 0.05)  # Adjusted for computational efficiency
X, Y = np.meshgrid(ratio_values, density_values)
Z = np.zeros_like(X)

# Total number of initial conditions
total_conditions = len(ratio_values) * len(density_values)

# Calculate total grid cells
total_grid_cells = GRID_SIZE * GRID_SIZE

# Prepare arguments for parallel processing
simulation_args = []
positions = []

for i, ratio in enumerate(ratio_values):
    for j, density in enumerate(density_values):
        # Skip simulations where density is 0 (no agents)
        if density == 0:
            Z[j, i] = np.nan  # Mark as invalid
            continue

        # Calculate total number of agents
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

        # Prepare arguments for simulations
        for _ in range(NUM_SIMULATIONS):
            simulation_args.append((num_prey, num_predators))
            positions.append((j, i))  # To map results back to Z

# Run simulations in parallel
def worker(args):
    num_prey, num_predators = args
    outcome = run_simulation((num_prey, num_predators))
    return outcome

with mp.Pool() as pool:
    # Use tqdm with map for progress bar
    results = list(tqdm(pool.imap(worker, simulation_args), total=len(simulation_args), desc="Running simulations"))

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

# Create a smooth plot using imshow
plt.figure(figsize=(10, 8))
# Mask invalid values
Z_masked = np.ma.masked_invalid(Z)
extent = [ratio_values.min(), ratio_values.max(), density_values.min(), density_values.max()]
plt.imshow(Z_masked, extent=extent, origin='lower', aspect='auto', cmap='viridis')

# Set colorbar with custom ticks and labels
cbar = plt.colorbar(ticks=[0, 1, 2])
cbar.ax.set_yticklabels(['All Prey Died', 'All Predators Died', 'Coexistence'])

plt.xlabel('Ratio (Prey / Predator)')
plt.ylabel('Density (Agents per Grid Cell)')
plt.title('Phase Diagram of Predator-Prey Simulation with Reproduction (Majority Outcome)')
plt.grid(False)
plt.savefig(f"plots/ratio_density_{NUM_SIMULATIONS}_with_reproduction_4.png")
plt.show()
