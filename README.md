# Predator-Prey Simulation Project

## Overview

Simulate predator-prey dynamics using a grid-based model:

- **Interactive Simulation**: Adjust initial conditions and observe real-time interactions.
- **Phase Diagram Generation**: Run multiple simulations to create a phase diagram of ecosystem outcomes.

## Features

- **Real-Time Visualization**: Watch predators and prey interact on a grid.
- **Customizable Parameters**: Set initial populations and simulation speed.
- **Outcome Display**: View the simulation state at the end.
- **Progress Tracking**: Monitor simulation progress with global and local progress bars.
- **Phase Diagram**: Visualize different outcomes based on initial populations.

## Requirements

- **Python** 3.6 or higher
- **Libraries**:
  - `pygame`
  - `numpy`
  - `matplotlib`
  - `tqdm`

Install libraries with:

```bash
pip install pygame numpy matplotlib tqdm
```

## Usage

### Interactive Simulation

1. **Run the script**:

   ```bash
   python predator_prey_simulation.py
   ```

2. **Controls**:
   - Use sliders to set initial prey and predator numbers.
   - Click **Setup Simulation** to initialize.
   - Click **Run Simulation** to start.
   - Adjust **Sim Speed** during the simulation.
   - Use **Pause/Resume** and **Reset** as needed.

3. **Visualization**:
   - Prey and predators move on the grid; predators display energy levels.
   - "+Energy Gained" appears briefly when predators eat prey.
   - A live graph shows population changes; the simulation state appears under the graph at the end.

### Phase Diagram Generation

1. **Run the script**:

   ```bash
   python predator_prey_phase_diagram.py
   ```

2. **Progress Monitoring**:
   - **Global Progress Bar**: Tracks overall simulation progress.
   - **Local Progress Bar**: Shows progress for each initial condition set.

3. **Output**:
   - Generates a phase diagram displaying outcome regions:
     - **Red**: All prey died.
     - **Blue**: All predators died.
     - **Green**: Coexistence.

## Customization

- **Simulation Parameters**: Modify variables in the scripts to explore different scenarios.
  - Adjust `NUM_SIMULATIONS`, initial population ranges, and other parameters.
- **Performance**:
  - Increasing `NUM_SIMULATIONS` improves accuracy but may increase computation time.

## License

Open-source project available for educational and research purposes.
