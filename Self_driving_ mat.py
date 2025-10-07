import pygame
import random
import sys
import os


WIDTH, HEIGHT = 700, 800
LANES = [140, 350, 560]  
MATATU_WIDTH, MATATU_HEIGHT = 60, 120
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 60, 120
ZEBRA_HEIGHT = 30
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Autonomous Matatu Simulator')
clock = pygame.time.Clock()

ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

def safe_load(path, size, color=(200, 0, 0)):
    """Try to load an image; if missing, return a colored placeholder."""
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path), size)
    else:
        print(f"⚠️ Missing asset: {path}. Using placeholder.")
        surf = pygame.Surface(size)
        surf.fill(color)
        return surf
MATATU_IMG = safe_load(os.path.join(ASSETS, 'matatuu.png'), (MATATU_WIDTH, MATATU_HEIGHT), (0, 200, 0))
CAR_IMGS = [
    safe_load(os.path.join(ASSETS, f'car{i}.png'), (OBSTACLE_WIDTH, OBSTACLE_HEIGHT), (200, 200, 0))
    for i in range(1, 4)
]
ROAD_IMG = safe_load(os.path.join(ASSETS, 'road.png'), (WIDTH, HEIGHT), (70, 70, 70)) \
    if os.path.exists(os.path.join(ASSETS, 'road.png')) else None

WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)


class Matatu:
    def __init__(self):
        self.lane = 1
        self.x = LANES[self.lane] - MATATU_WIDTH // 2
        self.y = HEIGHT - MATATU_HEIGHT - 20
        self.speed = 8
        self.braking = False
        self.target_x = self.x
        self.lane_change_speed = 15 

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = LANES[self.lane] - MATATU_WIDTH // 2

    def move_right(self):
        if self.lane < len(LANES) - 1:
            self.lane += 1
            self.target_x = LANES[self.lane] - MATATU_WIDTH // 2

    def brake(self):
        self.braking = True

    def release_brake(self):
        self.braking = False

    def update(self):
    
        if abs(self.x - self.target_x) > 2:
            direction = 1 if self.target_x > self.x else -1
            self.x += direction * self.lane_change_speed
        
            if (direction == 1 and self.x > self.target_x) or (direction == -1 and self.x < self.target_x):
                self.x = self.target_x

    def draw(self, surface):
        surface.blit(MATATU_IMG, (self.x, self.y))


class Obstacle:
    def __init__(self, kind):
        self.kind = kind
        self.lane = random.randint(0, len(LANES) - 1)
        self.x = LANES[self.lane] - OBSTACLE_WIDTH // 2
        self.y = -OBSTACLE_HEIGHT if kind == 'vehicle' else -ZEBRA_HEIGHT
        self.speed = 8
        self.img = random.choice(CAR_IMGS) if kind == 'vehicle' else None

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        if self.kind == 'vehicle' and self.img:
            surface.blit(self.img, (self.x, self.y))
        elif self.kind == 'zebra':
            zebra_x = LANES[0] - OBSTACLE_WIDTH // 2 - 60
            zebra_width = (LANES[-1] - LANES[0]) + OBSTACLE_WIDTH + 120
            pygame.draw.rect(surface, YELLOW, (zebra_x, self.y, zebra_width, ZEBRA_HEIGHT))
            num_stripes = 7
            stripe_width = zebra_width // num_stripes
            for i in range(num_stripes):
                if i % 2 == 0:
                    pygame.draw.rect(surface, WHITE, (zebra_x + i * stripe_width, self.y, stripe_width, ZEBRA_HEIGHT))

    def get_rect(self):
        if self.kind == 'vehicle':
            return pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
        else:
            return pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, ZEBRA_HEIGHT)
def main():
    matatu = Matatu()
    obstacles = []
    score = 0
    running = True
    spawn_timer = 0
    zebra_timer = 0
    ZEBRA_INTERVAL = 30 * FPS
    font = pygame.font.SysFont(None, 36)
    road_scroll = 0
    road_speed = 8
    zebra_waiting = False
    zebra_wait_timer = 0
    ZEBRA_STOP_TIME = 7 * FPS

    while running:
        if ROAD_IMG:
            road_scroll = (road_scroll + road_speed) % HEIGHT
            screen.blit(ROAD_IMG, (0, road_scroll - HEIGHT))
            screen.blit(ROAD_IMG, (0, road_scroll))
        else:
            screen.fill(GRAY)
            lane_line_height = 40
            lane_gap = 90
            road_scroll = (road_scroll + road_speed) % (lane_line_height + lane_gap)
            divider_positions = [LANES[0] + (LANES[1] - LANES[0]) // 2,
                                 LANES[1] + (LANES[2] - LANES[1]) // 2]
            for divider_x in divider_positions:
                y = -lane_line_height + road_scroll
                while y < HEIGHT:
                    pygame.draw.rect(screen, WHITE, (divider_x - 5, y, 10, lane_line_height))
                    y += lane_line_height + lane_gap
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        spawn_timer += 1
        zebra_timer += 1
        if spawn_timer > 60:
            obstacles.append(Obstacle('vehicle'))
            spawn_timer = 0
        if zebra_timer > ZEBRA_INTERVAL:
            obstacles.append(Obstacle('zebra'))
            zebra_timer = 0
        for obs in obstacles:
            obs.speed = 8 if not matatu.braking else 2
            obs.update()
        matatu.update()
        obstacles = [obs for obs in obstacles if obs.y < HEIGHT]
        matatu_rect = pygame.Rect(matatu.x, matatu.y, MATATU_WIDTH, MATATU_HEIGHT)
        closest = None
        zebra_ahead = None
        for obs in obstacles:
            if obs.lane == matatu.lane and obs.y < matatu.y:
                if closest is None or obs.y > closest.y:
                    closest = obs
                if obs.kind == 'zebra':
                    zebra_ahead = obs

        if zebra_waiting:
            matatu.brake()
            zebra_wait_timer += 1
            if zebra_wait_timer >= ZEBRA_STOP_TIME:
                zebra_waiting = False
                zebra_wait_timer = 2
        elif zebra_ahead and (matatu.y - zebra_ahead.y) < 30:
            zebra_waiting = True
            matatu.brake()
            zebra_wait_timer = 0
            zebra_ahead.y = HEIGHT + 100
        elif closest and (matatu.y - closest.y) < 300:
            left_lane = matatu.lane - 1
            right_lane = matatu.lane + 1
            safe_left = left_lane >= 0 and not any(o.lane == left_lane and abs(o.y - matatu.y) < 150 for o in obstacles)
            safe_right = right_lane < len(LANES) and not any(o.lane == right_lane and abs(o.y - matatu.y) < 150 for o in obstacles)
            if safe_left:
                matatu.move_left()
            elif safe_right:
                matatu.move_right()
            else:
                matatu.brake()
        else:
            matatu.release_brake()
        for obs in obstacles:
            if matatu_rect.colliderect(obs.get_rect()):
                running = False
        matatu.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
        score += 1
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    
    game_over_text = font.render('GAME OVER!', True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(2050)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
