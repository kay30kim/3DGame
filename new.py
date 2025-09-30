"""
Raycasting Mini Game Engine — minimal, single-file template
Python 3.10+ recommended

Controls:
  - W/S: move forward/backward
  - A/D: strafe left/right
  - ←/→: rotate
  - M: toggle minimap
  - ESC or window close: quit

Features:
  - Basic game loop (input → update → render)
  - Grid map + collision
  - Raycasting renderer (vertical strips)
  - FOV & rotation
  - Minimap with ray visualization

Run:
  pip install pygame
  python main.py
"""

import math
import sys
from dataclasses import dataclass

import pygame

# ----------------------------- Config ---------------------------------
WIDTH, HEIGHT = 960, 600
HALF_W, HALF_H = WIDTH // 2, HEIGHT // 2
FPS = 60
FOV_DEG = 70
FOV = math.radians(FOV_DEG)
NUM_RAYS = WIDTH  # one ray per column for simplicity (you can lower for speed)
MAX_DEPTH = 20
MOVE_SPEED = 3.0  # tiles per second
ROT_SPEED = math.radians(120)  # deg/sec

# Map (1 = wall, 0 = empty)
# You can edit this layout freely; P marks the recommended spawn.
MAP_STR = [
    "111111111111",
    "1P0000000001",
    "100100011001",
    "100100000001",
    "100111110001",
    "100000010001",
    "101110010001",
    "100010010001",
    "100010000001",
    "100011111001",
    "100000000001",
    "111111111111",
]

TILE_SIZE = 1.0  # world units per tile (keep as 1 for simplicity)
MAP_H = len(MAP_STR)
MAP_W = len(MAP_STR[0])

# Colors
COLOR_BG = (15, 15, 22)
COLOR_CEIL = (25, 25, 35)
COLOR_FLOOR = (18, 18, 24)
COLOR_WALL = (180, 180, 180)
COLOR_WALL_DARK = (110, 110, 120)
COLOR_RAY = (255, 220, 90)
COLOR_MINI_WALL = (60, 60, 80)
COLOR_MINI_FREE = (25, 25, 30)
COLOR_MINI_PLAYER = (120, 200, 255)

MINIMAP_SCALE = 8  # pixels per tile on the minimap
MINIMAP_PADDING = 10

# --------------------------- Data classes -----------------------------
@dataclass
class Player:
    x: float
    y: float
    angle: float  # radians, 0 = +x axis

    def pos(self):
        return (self.x, self.y)

# ------------------------- Helper functions ---------------------------
def parse_map():
    """Parse MAP_STR to find spawn and grid."""
    grid = []
    spawn = None
    for r, row in enumerate(MAP_STR):
        grow = []
        for c, ch in enumerate(row):
            if ch == 'P':
                spawn = (c + 0.5, r + 0.5)
                grow.append('0')
            else:
                grow.append(ch)
        grid.append(grow)
    if spawn is None:
        # default center if no spawn marker
        spawn = (2.5, 2.5)
    return grid, spawn

GRID, SPAWN = parse_map()

# Precompute some projection constants
PROJ_PLANE_DIST = (WIDTH / 2) / math.tan(FOV / 2)

# ----------------------------- Engine ---------------------------------
class Engine:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Raycasting Mini Engine")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_minimap = True

        self.player = Player(SPAWN[0], SPAWN[1], angle=math.radians(0))

    # -------------- Input --------------
    def handle_input(self, dt: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap

        keys = pygame.key.get_pressed()
        # Rotation
        if keys[pygame.K_LEFT]:
            self.player.angle -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.player.angle += ROT_SPEED * dt

        # Movement (WASD) in world axes relative to facing
        dx = dy = 0.0
        dir_x = math.cos(self.player.angle)
        dir_y = math.sin(self.player.angle)
        # perpendicular vector for strafing
        strafe_x = -dir_y
        strafe_y = dir_x

        if keys[pygame.K_w]:
            dx += dir_x * MOVE_SPEED * dt
            dy += dir_y * MOVE_SPEED * dt
        if keys[pygame.K_s]:
            dx -= dir_x * MOVE_SPEED * dt
            dy -= dir_y * MOVE_SPEED * dt
        if keys[pygame.K_a]:
            dx -= strafe_x * MOVE_SPEED * dt
            dy -= strafe_y * MOVE_SPEED * dt
        if keys[pygame.K_d]:
            dx += strafe_x * MOVE_SPEED * dt
            dy += strafe_y * MOVE_SPEED * dt

        self.try_move(dx, dy)

    # -------------- Physics / Collision --------------
    def is_blocked(self, x: float, y: float) -> bool:
        # Out of bounds = blocked
        if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
            return True
        return GRID[int(y)][int(x)] != '0'

    def try_move(self, dx: float, dy: float):
        # simple AABB-ish collision: resolve per-axis
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if not self.is_blocked(new_x, self.player.y):
            self.player.x = new_x
        if not self.is_blocked(self.player.x, new_y):
            self.player.y = new_y

    # -------------- Raycasting --------------
    def cast_rays(self):
        """Cast one ray per screen column. Return list of (dist, hit_side) per x.
        hit_side: 0 if hit vertical wall, 1 if horizontal (used for shading).
        """
        rays = []
        # starting angle for leftmost ray
        start_angle = self.player.angle - FOV / 2
        for col in range(NUM_RAYS):
            ray_angle = start_angle + (col / (NUM_RAYS - 1)) * FOV
            dist, side = self.raycast_single(ray_angle)
            # correct fish-eye by projecting onto view direction
            corrected = dist * math.cos(ray_angle - self.player.angle)
            rays.append((corrected, side))
        return rays

    def raycast_single(self, ray_angle: float):
        """DDA grid traversal. Returns (distance, side)."""
        # Ray direction
        rx = math.cos(ray_angle)
        ry = math.sin(ray_angle)
        # Which grid cell are we in?
        map_x = int(self.player.x)
        map_y = int(self.player.y)

        # Length of ray to cross one grid step
        delta_dist_x = abs(1.0 / rx) if rx != 0 else 1e30
        delta_dist_y = abs(1.0 / ry) if ry != 0 else 1e30

        # Step direction and initial side distances
        if rx < 0:
            step_x = -1
            side_dist_x = (self.player.x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - self.player.x) * delta_dist_x

        if ry < 0:
            step_y = -1
            side_dist_y = (self.player.y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - self.player.y) * delta_dist_y

        hit = False
        side = 0  # 0: vertical wall hit, 1: horizontal
        for _ in range(1024):  # cap to avoid infinite loops
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            # Out of bounds: treat as hit far away
            if map_x < 0 or map_y < 0 or map_x >= MAP_W or map_y >= MAP_H:
                break
            if GRID[map_y][map_x] != '0':
                hit = True
                break
        if not hit:
            # If no wall found, clamp distance to MAX_DEPTH * tile size
            return MAX_DEPTH, side

        # Compute exact perpendicular distance to the wall
        if side == 0:
            # vertical wall crossed last
            perp_dist = (side_dist_x - delta_dist_x)
        else:
            perp_dist = (side_dist_y - delta_dist_y)
        return max(0.0001, perp_dist), side

    # -------------- Rendering --------------
    def render(self, rays):
        surf = self.screen
        surf.fill(COLOR_BG)

        # split background into ceiling and floor
        pygame.draw.rect(surf, COLOR_CEIL, (0, 0, WIDTH, HALF_H))
        pygame.draw.rect(surf, COLOR_FLOOR, (0, HALF_H, WIDTH, HALF_H))

        # draw walls as vertical strips
        for x, (dist, side) in enumerate(rays):
            if dist <= 0:
                continue
            wall_h = int((TILE_SIZE / dist) * PROJ_PLANE_DIST)
            y1 = HALF_H - wall_h // 2
            y2 = HALF_H + wall_h // 2

            color = COLOR_WALL_DARK if side == 1 else COLOR_WALL
            pygame.draw.line(surf, color, (x, y1), (x, y2))

        if self.show_minimap:
            self.draw_minimap(rays)

        # HUD text
        self.draw_hud()

        pygame.display.flip()

    def draw_minimap(self, rays):
        mm_w = MAP_W * MINIMAP_SCALE
        mm_h = MAP_H * MINIMAP_SCALE
        ox = MINIMAP_PADDING
        oy = MINIMAP_PADDING

        # background
        pygame.draw.rect(self.screen, (12, 12, 16), (ox - 2, oy - 2, mm_w + 4, mm_h + 4), border_radius=6)
        # tiles
        for r in range(MAP_H):
            for c in range(MAP_W):
                rect = pygame.Rect(ox + c * MINIMAP_SCALE, oy + r * MINIMAP_SCALE, MINIMAP_SCALE, MINIMAP_SCALE)
                if GRID[r][c] != '0':
                    pygame.draw.rect(self.screen, COLOR_MINI_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_MINI_FREE, rect)

        # rays (downsample to avoid overdraw)
        step = max(1, NUM_RAYS // 120)
        start_angle = self.player.angle - FOV / 2
        for col in range(0, NUM_RAYS, step):
            ray_angle = start_angle + (col / (NUM_RAYS - 1)) * FOV
            dist, _ = rays[col]
            px = ox + int(self.player.x * MINIMAP_SCALE)
            py = oy + int(self.player.y * MINIMAP_SCALE)
            rx = px + int(math.cos(ray_angle) * dist * MINIMAP_SCALE)
            ry = py + int(math.sin(ray_angle) * dist * MINIMAP_SCALE)
            pygame.draw.line(self.screen, COLOR_RAY, (px, py), (rx, ry), 1)

        # player
        px = ox + int(self.player.x * MINIMAP_SCALE)
        py = oy + int(self.player.y * MINIMAP_SCALE)
        pygame.draw.circle(self.screen, COLOR_MINI_PLAYER, (px, py), 3)
        # facing indicator
        fx = px + int(math.cos(self.player.angle) * 8)
        fy = py + int(math.sin(self.player.angle) * 8)
        pygame.draw.line(self.screen, COLOR_MINI_PLAYER, (px, py), (fx, fy), 2)

    def draw_hud(self):
        font = pygame.font.SysFont("consolas", 16)
        text = f"FPS: {int(self.clock.get_fps()):3d}  Pos: ({self.player.x:.2f},{self.player.y:.2f})  Angle: {math.degrees(self.player.angle)%360:6.2f}°  FOV:{FOV_DEG}"
        surf = font.render(text, True, (200, 200, 210))
        self.screen.blit(surf, (10, HEIGHT - 24))

    # -------------- Main loop --------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input(dt)
            rays = self.cast_rays()
            self.render(rays)
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Engine().run()
