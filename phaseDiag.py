import random
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from tqdm import tqdm  # For progress bars

# Simulation parameters
GRID_SIZE = 15
MAX_STEPS = 1000
NUM_SIMULATIONS = 100  # Number of simulations per initial condition

# Agent classes
class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 5

def run_simulation(initial_prey, initial_predators):
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    prey_list = []
    predator_list = []
    step_count = 0

    # Initialize prey
    for _ in range(initial_prey):
        while True:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if grid[y][x] is None:
                prey = Prey(x, y)
                grid[y][x] = prey
                prey_list.append(prey)
                break

    # Initialize predators
    for _ in range(initial_predators):
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
        for nx, ny in neighbors:
            if grid[ny][nx] is None:
                grid[y][x] = None
                prey.x, prey.y = nx, ny
                grid[ny][nx] = prey
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
            predator.energy += 5
            moved = True
        elif empty_neighbors:
            nx, ny = random.choice(empty_neighbors)
            if grid[ny][nx] is None:
                grid[y][x] = None
                grid[ny][nx] = predator
                predator.x, predator.y = nx, ny
                predator.energy -= 1
                moved = True
        else:
            predator.energy -= 1
        if not moved:
            predator.energy -= 1
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

# Define the range of initial prey and predator populations
prey_range = np.arange(10, 101, 10)
predator_range = np.arange(10, 101, 10)
X, Y = np.meshgrid(prey_range, predator_range)
Z = np.zeros_like(X)

# Total number of initial conditions
total_conditions = len(prey_range) * len(predator_range)

# Global progress bar for the entire simulation
with tqdm(total=total_conditions, desc="Total Progress") as global_pbar:
    for i in range(len(prey_range)):
        for j in range(len(predator_range)):
            initial_prey = int(prey_range[i])
            initial_predators = int(predator_range[j])
            outcomes = []

            # Local progress bar for simulations with the same initial values
            desc = f"Prey: {initial_prey}, Predators: {initial_predators}"
            with tqdm(total=NUM_SIMULATIONS, desc=desc, leave=False) as local_pbar:
                for _ in range(NUM_SIMULATIONS):
                    outcome = run_simulation(initial_prey, initial_predators)
                    outcomes.append(outcome)
                    local_pbar.update(1)

            # Get the most common outcome
            most_common_outcome = Counter(outcomes).most_common(1)[0][0]
            Z[j, i] = most_common_outcome  # Note: Z[j, i] because of how meshgrid works

            global_pbar.update(1)

# Create a contour plot
plt.figure(figsize=(8, 6))
contour = plt.contourf(X, Y, Z, levels=[-0.5, 0.5, 1.5, 2.5], colors=['red', 'blue', 'green'], alpha=0.6)
# plt.colorbar(ticks=[0, 1, 2], label='Simulation Outcome')
plt.clim(-0.5, 2.5)
plt.xlabel('Initial Prey Population')
plt.ylabel('Initial Predator Population')
plt.title('Phase Diagram of Predator-Prey Simulation (Majority Outcome)')
plt.grid(True)

# Customize colorbar labels
cbar = plt.colorbar()
cbar.set_ticks([0, 1, 2])
cbar.set_ticklabels(['All Prey Died', 'All Predators Died', 'Coexistence'])

# Add contour lines
plt.contour(X, Y, Z, levels=[0.5, 1.5], colors='black', linestyles='--')
plt.savefig("Old_phase_diagram.png")
plt.show()
