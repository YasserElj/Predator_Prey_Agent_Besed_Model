# Predator-Prey Agent-Based Model

This project simulates predator-prey dynamics using an agent-based modeling approach. The model explores how different initial conditions influence outcomes such as predator extinction, prey extinction, or coexistence. It includes various iterations that progressively refined the model to better understand the complex dynamics of ecosystems.

## Project Overview

- **Authors**: Mohamed Kelai, Oussama Zaidi, Yasser El-jarida
- **Supervisor**: Pr. Julien Randon Furling
- **Course**: Mathematical Models of Complexity and Simulation at UM6P

## Models Implemented

### 1. Initial Visual Simulation
The first version was built using Python with Pygame to observe population dynamics visually. This version allowed for manual configuration of prey and predator populations and displayed their interactions in real-time. However, it lacked scalability and computational efficiency for in-depth analysis.

### 2. Phase Diagram Using Initial Populations
We expanded the model to analyze population outcomes based on different initial prey and predator population sizes. The model recorded outcomes such as predator extinction, prey extinction, or coexistence, and displayed them in a phase diagram.

### 3. Ratio and Density-Based Phase Diagram
The model was refined to use the ratio of prey to predators and the density of agents per grid cell as parameters. This approach provided a smoother representation of critical transitions between extinction and coexistence.

### 4. Prey Reproduction Mechanism
We introduced prey reproduction to the model, giving each prey a probability of reproducing each simulation step. This addition was aimed at exploring whether prey reproduction could enhance the stability of the ecosystem and lead to more frequent coexistence scenarios.

## Key Features
- **Agent-Based Modeling**: Each prey and predator is represented as an individual agent interacting on a 20x20 grid.
- **Dynamic Metrics**: Population ratios, densities, and prey reproduction are used to explore the stability of predator-prey interactions.
- **Visualization**: Phase diagrams show critical transitions between predator extinction, prey extinction, and coexistence.
- **Scalability**: Simulations were conducted using the Toubkal supercomputer, enabling detailed and high-resolution results.

## Running the Simulation
1. Clone the repository:
   ```
   git clone https://github.com/YasserElj/Predator_Prey_Agent_Besed_Model.git
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the simulation:
   ```
   python main.py
   ```

## Dependencies
- Python 3.x
- `matplotlib` for visualizations
- `numpy` for numerical operations
- `tqdm` for progress bars
- `multiprocessing` for parallel simulations

## Results
The final phase diagrams reveal critical insights into the dynamics of the predator-prey system. Introducing prey reproduction expanded the coexistence zones and provided a stabilizing effect, particularly in moderate density regions.

## Visuals
### 1. Initial Predator-Prey Visual Simulation
![Initial Visual Simulation](images/visual_interface.png)
*Figure 1: Initial predator-prey visual simulation using Pygame.*

### 2. Phase Diagram Using Initial Populations
![Phase Diagram Initial Populations](images/Old_phase_diagram.png)
*Figure 2: Phase diagram of the simulation outcomes using initial populations as axes.*

### 3. Ratio and Density-Based Phase Diagram (Smaller Scale)
![Smaller-Scale Phase Diagram](images/ratio_density_10.png)
*Figure 3: Phase diagram from the smaller-scale simulation using prey/predator ratio and agent density.*

### 4. Ratio and Density-Based Phase Diagram (Full Scale)
![Full-Scale Phase Diagram](images/ratio_density_500_2.png)
*Figure 4: Full-scale phase diagram of predator-prey simulation using prey/predator ratio and agent density as axes.*

### 5. Phase Diagram with Prey Reproduction
![Phase Diagram with Reproduction](images/ratio_density_reproduction.png)
*Figure 5: Phase diagram of predator-prey simulation with prey reproduction.*

