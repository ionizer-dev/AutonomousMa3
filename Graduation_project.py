import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 500, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Self-Driving Matatu 🚐")

# Colors
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (255, 255, 255)
CAR_COLOR = (255, 220, 0)
OBSTACLE_COLOR = (200, 50, 50)
BG_COLOR = (100, 200, 255)
PEDESTRIAN_COLOR = (20, 20, 20)

clock = pygame.time.Clock()

# Car sizes
CAR_WIDTH, CAR_HEIGHT = 50, 90

# --- Matatu class ---
class Matatu:
    def __init__(self):
        self.x = WIDTH // 2 - CAR_WIDTH // 2
        self.y = HEIGHT - 150
        self.speed = 5
        self.lane = 1
        self.rect = pygame.Rect(self.x, self.y, CAR_WIDTH, CAR_HEIGHT)
        self.stop_for_pedestrians = False

    def update(self, obstacles, pedestrians, zebra_y):
        if not self.stop_for_pedestrians:
            self.y -= 0.5
            self.rect.y = self.y

        # Check for pedestrians on zebra
        for p in pedestrians:
            if p.on_crosswalk and abs(self.rect.centery - zebra_y) < 100:
                self.stop_for_pedestrians = True
                break
        else:
            self.stop_for_pedestrians = False

        # Avoid collisions
        for obs in obstacles:
            if self.rect.colliderect(obs.rect.inflate(-10, -10)):
                self.avoid()

        # Stay in lanes
        lane_x = [WIDTH//2 - 160, WIDTH//2 - 50, WIDTH//2 + 60]
        self.x += (lane_x[self.lane] - self.x) * 0.2
        self.rect.x = int(self.x)

    def avoid(self):
        self.lane = random.choice([0, 1, 2])

    def draw(self, win):
        color = (255, 120, 0) if self.stop_for_pedestrians else CAR_COLOR
        pygame.draw.rect(win, color, self.rect, border_radius=8)


# --- Obstacle cars ---
class Obstacle:
    def __init__(self):
        lane_x = [WIDTH//2 - 160, WIDTH//2 - 50, WIDTH//2 + 60]
        self.lane = random.choice([0, 1, 2])
        self.x = lane_x[self.lane]
        self.y = random.randint(-600, -100)
        self.speed = random.uniform(3, 6)
        self.rect = pygame.Rect(self.x, self.y, CAR_WIDTH, CAR_HEIGHT)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        if self.y > HEIGHT + 100:
            self.reset()

    def reset(self):
        lane_x = [WIDTH//2 - 160, WIDTH//2 - 50, WIDTH//2 + 60]
        self.lane = random.choice([0, 1, 2])
        self.x = lane_x[self.lane]
        self.y = random.randint(-600, -100)
        self.speed = random.uniform(3, 6)
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, win):
        pygame.draw.rect(win, OBSTACLE_COLOR, self.rect, border_radius=8)


# --- Pedestrian class ---
class Pedestrian:
    def __init__(self, zebra_y):
        self.x = random.choice([WIDTH//2 - 220, WIDTH//2 + 220])
        self.y = zebra_y + random.randint(-10, 10)
        self.speed = random.uniform(1.0, 2.0)
        self.on_crosswalk = True
        self.direction = 1 if self.x < WIDTH//2 else -1
        self.rect = pygame.Rect(self.x, self.y, 10, 20)

    def update(self):
        if self.on_crosswalk:
            self.x += self.speed * self.direction
            self.rect.x = int(self.x)
            if (self.direction == 1 and self.x > WIDTH//2 + 220) or (self.direction == -1 and self.x < WIDTH//2 - 220):
                self.on_crosswalk = False

    def draw(self, win):
        pygame.draw.circle(win, PEDESTRIAN_COLOR, self.rect.center, 8)


# --- Zebra Crossing ---
def draw_zebra_crossing(win, y):
    for i in range(0, WIDTH, 80):
        pygame.draw.rect(win, LINE_COLOR, (i, y, 40, 15))


# --- Draw road ---
def draw_road(win, offset):
    win.fill(BG_COLOR)
    pygame.draw.rect(win, ROAD_COLOR, (WIDTH//2 - 200, 0, 400, HEIGHT))

    # Lane divider lines
    line_y = offset
    while line_y < HEIGHT:
        for lane_x in [WIDTH//2 - 100, WIDTH//2 + 20]:
            pygame.draw.rect(win, LINE_COLOR, (lane_x, line_y, 10, 40))
        line_y += 80


# --- Game setup ---
matatu = Matatu()
obstacles = [Obstacle() for _ in range(6)]
pedestrians = []
scroll_offset = 0
score = 0
font = pygame.font.SysFont(None, 32)
zebra_y = HEIGHT // 2

# --- Main loop ---
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn pedestrians occasionally
    if random.random() < 0.005 and not any(p.on_crosswalk for p in pedestrians):
        pedestrians.append(Pedestrian(zebra_y))

    # Update
    scroll_offset += 5
    if scroll_offset >= 80:
        scroll_offset = 0

    for obs in obstacles:
        obs.update()

    for p in pedestrians:
        p.update()

    # Remove finished pedestrians
    pedestrians = [p for p in pedestrians if p.on_crosswalk]

    matatu.update(obstacles, pedestrians, zebra_y)
    score += 0.05

    # Draw
    draw_road(WIN, -scroll_offset)
    draw_zebra_crossing(WIN, zebra_y)

    for obs in obstacles:
        obs.draw(WIN)
    for p in pedestrians:
        p.draw(WIN)
    matatu.draw(WIN)

    # HUD
    WIN.blit(font.render(f"Score: {int(score)}", True, (0,0,0)), (20, 20))
    if matatu.stop_for_pedestrians:
        WIN.blit(font.render("Stopping for pedestrians...", True, (200,0,0)), (120, 50))
    else:
        WIN.blit(font.render("Auto Driving...", True, (0,120,0)), (160, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
