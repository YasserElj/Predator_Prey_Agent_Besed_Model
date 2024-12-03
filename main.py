import pygame
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Agent classes
class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 5  # Predators lose energy each turn
        self.display_energy_gain = False  # Display "+Energy Gained"
        self.energy_gain_timer = 0  # Timer for displaying energy gain

# UIButton class
class UIButton:
    def __init__(self, x, y, width, height, text, color=(200, 200, 200)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# UISlider class
class UISlider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = initial_val
        self.label = label
        self.font = pygame.font.Font(None, 24)
        self.handle_rect = pygame.Rect(x, y - 5, 20, height + 10)
        self.update_handle_position()
        self.dragging = False
        
    def update_handle_position(self):
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.x = self.rect.x + ratio * (self.rect.width - self.handle_rect.width)
        
    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.handle_rect)
        label_surface = self.font.render(f"{self.label}: {int(self.current_val)}", True, (0, 0, 0))
        surface.blit(label_surface, (self.rect.x, self.rect.y - 30))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.handle_rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = event.pos[0] - self.handle_rect.width // 2
            new_x = max(self.rect.x, min(new_x, self.rect.x + self.rect.width - self.handle_rect.width))
            self.handle_rect.x = new_x
            ratio = (self.handle_rect.x - self.rect.x) / (self.rect.width - self.handle_rect.width)
            self.current_val = self.min_val + ratio * (self.max_val - self.min_val)

# Main Simulation Class
class PredatorPreySimulation:
    def __init__(self):
        pygame.init()
        self.menu_width = 250
        self.grid_size = 20
        self.cell_size = 30
        self.graph_width = 400
        self.screen_width = self.menu_width + self.grid_size * self.cell_size + self.graph_width
        self.screen_height = self.grid_size * self.cell_size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Predator-Prey Simulation")
        self.GREEN_BACKGROUND = (100, 200, 100)
        self.MENU_BACKGROUND = (230, 230, 230)
        self._create_ui_elements()
        self.is_running = False
        self.is_paused = False
        self.grid = None
        self.prey_list = []
        self.predator_list = []
        self.simulation_speed = 5
        self.prey_population_history = []
        self.predator_population_history = []
        self.time_steps = []
        self.step_count = 0
        self.max_steps = 1000  # Max steps for "long time coexistence"
        self.simulation_state = ""
        try:
            self.prey_image = pygame.image.load('rabbit.png')
            self.predator_image = pygame.image.load('fox.png')
        except:
            self.prey_image = None
            self.predator_image = None
        self.font = pygame.font.Font(None, 20)
        self.fig, self.ax = plt.subplots(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig)
            
    def _create_ui_elements(self):
        # Adjusted positions for UI elements
        start_y = 120
        vertical_spacing = 80
        
        self.prey_slider = UISlider(10, start_y, 230, 20, 0, 100, 50, "Initial Prey")
        self.predator_slider = UISlider(10, start_y + vertical_spacing, 230, 20, 0, 50, 20, "Initial Predators")
        self.speed_slider = UISlider(10, start_y + 2 * vertical_spacing, 230, 20, 1, 20, 5, "Sim Speed")
        self.setup_button = UIButton(10, start_y + 3 * vertical_spacing, 230, 50, "Setup Simulation", (150, 255, 150))
        self.run_button = UIButton(10, start_y + 3 * vertical_spacing + 70, 230, 50, "Run Simulation", (100, 200, 100))
        self.pause_button = UIButton(10, start_y + 3 * vertical_spacing + 140, 230, 50, "Pause/Resume", (255, 200, 100))
        self.reset_button = UIButton(10, start_y + 3 * vertical_spacing + 210, 230, 50, "Reset", (200, 150, 150))
        
    def _initialize_population(self, num_prey, num_predators):
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.prey_list = []
        self.predator_list = []
        self.prey_population_history = []
        self.predator_population_history = []
        self.time_steps = []
        self.step_count = 0
        self.simulation_state = ""
        for _ in range(int(num_prey)):
            while True:
                x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
                if self.grid[y][x] is None:
                    prey = Prey(x, y)
                    self.grid[y][x] = prey
                    self.prey_list.append(prey)
                    break
        for _ in range(int(num_predators)):
            while True:
                x, y = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
                if self.grid[y][x] is None or isinstance(self.grid[y][x], Prey):
                    predator = Predator(x, y)
                    self.grid[y][x] = predator
                    self.predator_list.append(predator)
                    break
        
    def draw_menu(self):
        menu_rect = pygame.Rect(0, 0, self.menu_width, self.screen_height)
        pygame.draw.rect(self.screen, self.MENU_BACKGROUND, menu_rect)
        font = pygame.font.Font(None, 36)
        title = font.render("Predator-Prey", True, (0, 0, 0))
        self.screen.blit(title, (10, 20))
        subtitle = pygame.font.Font(None, 24).render("Ecosystem Simulation", True, (50, 50, 50))
        self.screen.blit(subtitle, (10, 60))
        self.prey_slider.draw(self.screen)
        self.predator_slider.draw(self.screen)
        self.speed_slider.draw(self.screen)
        self.setup_button.draw(self.screen)
        self.run_button.draw(self.screen)
        self.pause_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            if self.is_running and not self.is_paused:
                self.simulation_logic()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                    self.prey_slider.handle_event(event)
                    self.predator_slider.handle_event(event)
                    self.speed_slider.handle_event(event)
                    self.simulation_speed = int(self.speed_slider.current_val)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        if self.setup_button.is_clicked(mouse_pos):
                            self._initialize_population(self.prey_slider.current_val, self.predator_slider.current_val)
                            self.is_running = False
                            self.is_paused = False
                        if self.run_button.is_clicked(mouse_pos) and self.grid:
                            self.is_running = True
                            self.is_paused = False
                        if self.pause_button.is_clicked(mouse_pos) and self.is_running:
                            self.is_paused = not self.is_paused
                        if self.reset_button.is_clicked(mouse_pos):
                            self.is_running = False
                            self.is_paused = False
                            self.grid = None
                            self.prey_list = []
                            self.predator_list = []
                            self.prey_population_history = []
                            self.predator_population_history = []
                            self.time_steps = []
                            self.step_count = 0
                            self.simulation_state = ""
            self.screen.fill((255, 255, 255))
            self.draw_menu()
            if self.grid:
                self._draw_grid()
                self._draw_population_graph()
                self._draw_simulation_state()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
        
    def _draw_grid(self):
        grid_start_x = self.menu_width
        grid_rect = pygame.Rect(grid_start_x, 0, self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        pygame.draw.rect(self.screen, self.GREEN_BACKGROUND, grid_rect)
        for x in range(grid_start_x, grid_start_x + self.grid_size * self.cell_size, self.cell_size):
            pygame.draw.line(self.screen, (0, 0, 0), (x, 0), (x, self.grid_size * self.cell_size))
        for y in range(0, self.grid_size * self.cell_size, self.cell_size):
            pygame.draw.line(self.screen, (0, 0, 0), (grid_start_x, y), (grid_start_x + self.grid_size * self.cell_size, y))
        for prey in self.prey_list:
            x = prey.x * self.cell_size + grid_start_x
            y = prey.y * self.cell_size
            agent_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            if self.prey_image:
                scaled_image = pygame.transform.scale(self.prey_image, (self.cell_size, self.cell_size))
                self.screen.blit(scaled_image, agent_rect)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), agent_rect)
        for predator in self.predator_list:
            x = predator.x * self.cell_size + grid_start_x
            y = predator.y * self.cell_size
            agent_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
            if self.predator_image:
                scaled_image = pygame.transform.scale(self.predator_image, (self.cell_size, self.cell_size))
                self.screen.blit(scaled_image, agent_rect)
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), agent_rect)
            energy_text = self.font.render(f"E:{predator.energy}", True, (0, 0, 0))
            self.screen.blit(energy_text, (x, y - 15))
            if predator.display_energy_gain:
                gain_text = self.font.render("+Energy Gained", True, (0, 255, 0))
                self.screen.blit(gain_text, (x, y - 30))
                predator.energy_gain_timer -= 1
                if predator.energy_gain_timer <= 0:
                    predator.display_energy_gain = False
        
    def _draw_population_graph(self):
        graph_start_x = self.menu_width + self.grid_size * self.cell_size
        self.ax.clear()
        self.ax.plot(self.time_steps, self.prey_population_history, label='Prey', color='blue')
        self.ax.plot(self.time_steps, self.predator_population_history, label='Predators', color='red')
        self.ax.set_title('Population over Time')
        self.ax.set_xlabel('Time Steps')
        self.ax.set_ylabel('Population')
        self.ax.legend()
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = self.canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        self.screen.blit(surf, (graph_start_x, 10))
        
    def _draw_simulation_state(self):
        """Display the state of the simulation under the graph."""
        if self.simulation_state:
            graph_start_x = self.menu_width + self.grid_size * self.cell_size
            state_text_surface = self.font.render(f"Simulation State: {self.simulation_state}", True, (0, 0, 0))
            self.screen.blit(state_text_surface, (graph_start_x, 320))
        
    def simulation_logic(self):
        self.step_count += 1
        self.move_prey()
        self.move_predators()
        self.prey_population_history.append(len(self.prey_list))
        self.predator_population_history.append(len(self.predator_list))
        self.time_steps.append(self.step_count)
        pygame.time.delay(int(1000 / self.simulation_speed))
        if len(self.prey_list) == 0:
            self.is_paused = True
            self.is_running = False
            self.simulation_state = "All Prey Died"
        elif len(self.predator_list) == 0:
            self.is_paused = True
            self.is_running = False
            self.simulation_state = "All Predators Died"
        elif self.step_count >= self.max_steps:
            self.is_paused = True
            self.is_running = False
            self.simulation_state = "Long-term Coexistence"
        
    def move_prey(self):
        for prey in self.prey_list[:]:
            x, y = prey.x, prey.y
            neighbors = self.get_neighbors(x, y)
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if self.grid[ny][nx] is None:
                    self.grid[y][x] = None
                    prey.x, prey.y = nx, ny
                    self.grid[ny][nx] = prey
                    break
        
    def move_predators(self):
        random.shuffle(self.predator_list)
        for predator in self.predator_list[:]:
            x, y = predator.x, predator.y
            neighbors = self.get_neighbors(x, y)
            prey_neighbors = []
            empty_neighbors = []
            for nx, ny in neighbors:
                if isinstance(self.grid[ny][nx], Prey):
                    prey_neighbors.append((nx, ny))
                elif self.grid[ny][nx] is None:
                    empty_neighbors.append((nx, ny))
            moved = False
            if prey_neighbors:
                nx, ny = random.choice(prey_neighbors)
                self.grid[y][x] = None
                prey = self.grid[ny][nx]
                self.prey_list.remove(prey)
                self.grid[ny][nx] = predator
                predator.x, predator.y = nx, ny
                predator.energy += 5
                predator.display_energy_gain = True
                predator.energy_gain_timer = 1  # Display for 1 step
                moved = True
            elif empty_neighbors:
                nx, ny = random.choice(empty_neighbors)
                if self.grid[ny][nx] is None:
                    self.grid[y][x] = None
                    self.grid[ny][nx] = predator
                    predator.x, predator.y = nx, ny
                    predator.energy -= 1
                    moved = True
            else:
                predator.energy -= 1
            if not moved:
                predator.energy -= 1
            if predator.energy <= 0:
                self.grid[predator.y][predator.x] = None
                self.predator_list.remove(predator)
        
    def get_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.grid_size
                ny = (y + dy) % self.grid_size
                neighbors.append((nx, ny))
        return neighbors

if __name__ == "__main__":
    sim = PredatorPreySimulation()
    sim.run()
