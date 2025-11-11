"""
Raycasting Mini Game Engine — with hands/weapon sprite + learning AI (Python/Pygame)
Python 3.10+

New features in this version:
  - "Hands + weapon" overlay sprite (center-bottom)
  - NPCs rendered as billboard sprites (depth-sorted & wall-occluded)
  - Simple online-learning AI: NPCs learn which way to step to reduce distance to player over time
    * Lightweight reinforcement: reward moves that reduce distance; persist to ai_brain.json

Controls:
  W/S: forward/back   A/D: strafe    ←/→: rotate    M: minimap   N: spawn NPC   ESC: quit

Run:
  pip install pygame
  python main.py
"""

import json
import math
import os
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

# ----------------------------- Config ---------------------------------
WIDTH, HEIGHT = 960, 600
HALF_W, HALF_H = WIDTH // 2, HEIGHT // 2
FPS = 60
FOV_DEG = 70
FOV = math.radians(FOV_DEG)
NUM_RAYS = WIDTH  # one ray per column (reduce for speed if needed)
MAX_DEPTH = 20
MOVE_SPEED = 3.2  # tiles/sec
ROT_SPEED = math.radians(120)
SPRITE_SIZE_WORLD = 0.8  # approximate width/height in world units

MAP_STR = [
    "111111111111",
    "1P0000000001",
    "100100011000",
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

TILE_SIZE = 1.0
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
COLOR_MINI_NPC = (255, 140, 120)

MINIMAP_SCALE = 8
MINIMAP_PADDING = 10

BRAIN_PATH = "ai_brain.json"
ALPHA = 0.08   # learning rate
DECAY = 0.995  # slight decay toward 1.0

# --------------------------- Utilities --------------------------------

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

# --------------------------- Map parsing -------------------------------

def parse_map():
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
        spawn = (2.5, 2.5)
    return grid, spawn

GRID, SPAWN = parse_map()

PROJ_PLANE_DIST = (WIDTH / 2) / math.tan(FOV / 2)

# ----------------------------- Data -----------------------------------
@dataclass
class Player:
    x: float
    y: float
    angle: float

    def pos(self):
        return (self.x, self.y)

@dataclass
class NPC:
    x: float
    y: float
    angle: float = 0.0
    speed: float = 2.2
    last_dist: float = field(default=1e9)

    def pos(self):
        return (self.x, self.y)

# ----------------------------- AI Brain --------------------------------
class AIBrain:
    """Minimal online-learning brain: chooses among 8 move directions + stay.
    Keeps weights per action. Rewards actions that reduce distance to the player.
    Weights persist to JSON between runs. This is intentionally tiny & transparent.
    """

    ACTIONS = [
        ( 0, 0, "stay"),
        ( 1, 0, "east"), (-1, 0, "west"),
        ( 0, 1, "south"), ( 0,-1, "north"),
        ( 1, 1, "se"),    ( 1,-1, "ne"),
        (-1, 1, "sw"),    (-1,-1, "nw"),
    ]

    def __init__(self, path=BRAIN_PATH):
        self.path = path
        self.weights = {name: 1.0 for _,_,name in self.ACTIONS}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for k,v in data.items():
                        if k in self.weights and isinstance(v, (int,float)):
                            self.weights[k] = float(v)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.weights, f, indent=2)
        except Exception:
            pass

    def choose(self, npc: NPC, player: Player) -> Tuple[float,float,str]:
        # Softmax-like sampling over positive weights (stable & simple)
        names = [name for _,_,name in self.ACTIONS]
        w = [max(1e-3, self.weights[name]) for name in names]
        total = sum(w)
        r = random.random() * total
        acc = 0.0
        idx = 0
        for i,wi in enumerate(w):
            acc += wi
            if r <= acc:
                idx = i
                break
        dx, dy, name = self.ACTIONS[idx]
        return dx, dy, name

    def learn(self, action_name: str, improved: bool):
        # Reward/decay & mild regularization toward 1.0
        cur = self.weights[action_name]
        if improved:
            cur += ALPHA
        else:
            cur *= DECAY
        # Regularize slightly toward 1.0 to avoid runaway
        cur = 0.98*cur + 0.02*1.0
        self.weights[action_name] = clamp(cur, 0.1, 5.0)

# ----------------------------- Engine ----------------------------------
class Engine:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Raycasting Mini Engine — weapons + learning AI")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_minimap = True

        self.player = Player(SPAWN[0], SPAWN[1], angle=0.0)
        self.npcs: List[NPC] = []
        self.brain = AIBrain()

        # simple weapon/hand surfaces (placeholder art)
        self.weapon_surf = self.make_weapon_surface()
        self.hand_surf = self.make_hand_surface()

    # ----------------- Input -----------------
    def handle_input(self, dt: float):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                elif event.key == pygame.K_n:
                    self.spawn_npc()

        keys = pygame.key.get_pressed()
        # Rotation
        if keys[pygame.K_LEFT]:
            self.player.angle -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.player.angle += ROT_SPEED * dt

        # Movement
        dx = dy = 0.0
        dir_x = math.cos(self.player.angle)
        dir_y = math.sin(self.player.angle)
        strafe_x = -dir_y
        strafe_y = dir_x

        if keys[pygame.K_w]:
            dx += dir_x * MOVE_SPEED * dt
            dy += dir_y * MOVE_SPEED * dt
        if keys[pygame.K_s]:
            dx -= dir_x * MOVE_SPEED * dt
            dy -= dir_y * MOVE_SPEED * dt
        if keys[pygame.K_a]:
            dx += strafe_x * MOVE_SPEED * dt
            dy += strafe_y * MOVE_SPEED * dt
        if keys[pygame.K_d]:
            dx -= strafe_x * MOVE_SPEED * dt
            dy -= strafe_y * MOVE_SPEED * dt

        self.try_move_player(dx, dy)

    # ----------------- Collision -----------------
    def is_blocked(self, x: float, y: float) -> bool:
        if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
            return True
        return GRID[int(y)][int(x)] != '0'

    def try_move_player(self, dx: float, dy: float):
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        if not self.is_blocked(new_x, self.player.y):
            self.player.x = new_x
        if not self.is_blocked(self.player.x, new_y):
            self.player.y = new_y

    def try_move_entity(self, ent: NPC, dx: float, dy: float):
        new_x = ent.x + dx
        new_y = ent.y + dy
        if not self.is_blocked(new_x, ent.y):
            ent.x = new_x
        if not self.is_blocked(ent.x, new_y):
            ent.y = new_y

    # ----------------- NPC -----------------
    def spawn_npc(self):
        # place NPC at a free random tile
        free_tiles = [(c + 0.5, r + 0.5) for r in range(MAP_H) for c in range(MAP_W) if GRID[r][c]=='0']
        random.shuffle(free_tiles)
        for x,y in free_tiles:
            # avoid spawning too close
            if (x-self.player.x)**2 + (y-self.player.y)**2 > 9.0:
                self.npcs.append(NPC(x,y))
                break

    def update_npcs(self, dt: float):
        for npc in self.npcs:
            # Simple ticking brain: choose a direction each frame scaled by speed
            px, py = self.player.pos()
            nx, ny = npc.pos()
            prev_dist = math.hypot(px-nx, py-ny)

            # choose action
            ax, ay, name = self.brain.choose(npc, self.player)
            # normalize diagonal
            mag = math.hypot(ax, ay)
            if mag > 0:
                ax /= mag; ay /= mag

            step = npc.speed * dt
            self.try_move_entity(npc, ax*step, ay*step)

            # learning signal: did we get closer?
            nx2, ny2 = npc.pos()
            new_dist = math.hypot(px-nx2, py-ny2)
            improved = new_dist < prev_dist
            self.brain.learn(name, improved)

        # occasionally persist brain
        if random.random() < 0.02:
            self.brain.save()

    # ----------------- Raycasting -----------------
    def cast_rays(self) -> Tuple[List[Tuple[float,int]], List[float]]:
        rays: List[Tuple[float,int]] = []
        zbuffer: List[float] = [MAX_DEPTH]*NUM_RAYS
        start_angle = self.player.angle - FOV / 2
        for col in range(NUM_RAYS):
            ray_angle = start_angle + (col / (NUM_RAYS - 1)) * FOV
            dist, side = self.raycast_single(ray_angle)
            corrected = dist * math.cos(ray_angle - self.player.angle)
            rays.append((corrected, side))
            zbuffer[col] = corrected
        return rays, zbuffer

    def raycast_single(self, ray_angle: float):
        rx = math.cos(ray_angle)
        ry = math.sin(ray_angle)
        map_x = int(self.player.x)
        map_y = int(self.player.y)
        delta_dist_x = abs(1.0 / rx) if rx != 0 else 1e30
        delta_dist_y = abs(1.0 / ry) if ry != 0 else 1e30

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
        side = 0
        for _ in range(1024):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            if map_x < 0 or map_y < 0 or map_x >= MAP_W or map_y >= MAP_H:
                break
            if GRID[map_y][map_x] != '0':
                hit = True
                break
        if not hit:
            return MAX_DEPTH, side
        perp_dist = (side_dist_x - delta_dist_x) if side==0 else (side_dist_y - delta_dist_y)
        return max(0.0001, perp_dist), side

    # ----------------- Rendering -----------------
    def render(self, rays: List[Tuple[float,int]], zbuffer: List[float]):
        surf = self.screen
        surf.fill(COLOR_BG)
        pygame.draw.rect(surf, COLOR_CEIL, (0, 0, WIDTH, HALF_H))
        pygame.draw.rect(surf, COLOR_FLOOR, (0, HALF_H, WIDTH, HALF_H))

        # Walls
        for x, (dist, side) in enumerate(rays):
            if dist <= 0:
                continue
            wall_h = int((TILE_SIZE / dist) * PROJ_PLANE_DIST)
            y1 = HALF_H - wall_h // 2
            y2 = HALF_H + wall_h // 2
            color = COLOR_WALL_DARK if side == 1 else COLOR_WALL
            pygame.draw.line(surf, color, (x, y1), (x, y2))

        # Sprites (NPCs)
        self.render_npc_sprites(zbuffer)

        if self.show_minimap:
            self.draw_minimap(rays)
        self.draw_hud()

        # Hands + Weapon overlay drawn last
        self.draw_weapon_overlay()

        pygame.display.flip()

    def world_to_screen_sprite(self, sx: float, sy: float):
        # camera space transform
        px, py = self.player.pos()
        dx = sx - px
        dy = sy - py

        # rotate into camera space
        sin_a = math.sin(self.player.angle)
        cos_a = math.cos(self.player.angle)
        # camera axes: forward=(cos,sin), right=(-sin,cos)
        cam_x =  cos_a * dx + sin_a * dy   # forward depth
        cam_y = -sin_a * dx + cos_a * dy   # right (+)
        if cam_x <= 0.0001:
            return None  # behind camera

        # projection
        screen_x = int(HALF_W + (cam_y * PROJ_PLANE_DIST / cam_x))
        sprite_h = int((SPRITE_SIZE_WORLD / cam_x) * PROJ_PLANE_DIST)
        sprite_w = sprite_h
        top = HALF_H - sprite_h // 2
        left = screen_x - sprite_w // 2
        depth = cam_x
        return left, top, sprite_w, sprite_h, depth

    def render_npc_sprites(self, zbuffer: List[float]):
        # sort by depth far→near so that nearer can overwrite (after z-check per column)
        to_draw = []
        for npc in self.npcs:
            proj = self.world_to_screen_sprite(npc.x, npc.y)
            if proj is not None:
                left, top, w, h, depth = proj
                to_draw.append((depth, left, top, w, h))
        to_draw.sort(reverse=True, key=lambda t: t[0])

        # simple colored rectangle as placeholder sprite
        for depth, left, top, w, h in to_draw:
            if w <= 0 or h <= 0:
                continue
            # z-occlusion per column
            start = max(0, left)
            end = min(WIDTH-1, left + w)
            for x in range(start, end):
                if 0 <= x < WIDTH and depth < zbuffer[x]:
                    y1 = max(0, top)
                    y2 = min(HEIGHT-1, top + h)
                    pygame.draw.line(self.screen, (235, 120, 110), (x, y1), (x, y2))

    def draw_minimap(self, rays):
        mm_w = MAP_W * MINIMAP_SCALE
        mm_h = MAP_H * MINIMAP_SCALE
        ox = MINIMAP_PADDING
        oy = MINIMAP_PADDING

        pygame.draw.rect(self.screen, (12, 12, 16), (ox - 2, oy - 2, mm_w + 4, mm_h + 4), border_radius=6)
        for r in range(MAP_H):
            for c in range(MAP_W):
                rect = pygame.Rect(ox + c * MINIMAP_SCALE, oy + r * MINIMAP_SCALE, MINIMAP_SCALE, MINIMAP_SCALE)
                if GRID[r][c] != '0':
                    pygame.draw.rect(self.screen, COLOR_MINI_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_MINI_FREE, rect)

        # rays (downsample)
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
        fx = px + int(math.cos(self.player.angle) * 8)
        fy = py + int(math.sin(self.player.angle) * 8)
        pygame.draw.line(self.screen, COLOR_MINI_PLAYER, (px, py), (fx, fy), 2)

        # NPCs
        for npc in self.npcs:
            nx = ox + int(npc.x * MINIMAP_SCALE)
            ny = oy + int(npc.y * MINIMAP_SCALE)
            pygame.draw.circle(self.screen, COLOR_MINI_NPC, (nx, ny), 3)

    def draw_hud(self):
        font = pygame.font.SysFont("consolas", 16)
        text = f"FPS:{int(self.clock.get_fps()):3d}  Pos:({self.player.x:.2f},{self.player.y:.2f})  Angle:{math.degrees(self.player.angle)%360:6.2f}°  NPCs:{len(self.npcs)}"
        surf = font.render(text, True, (200, 200, 210))
        self.screen.blit(surf, (10, HEIGHT - 24))

    def make_weapon_surface(self) -> pygame.Surface:
        # Placeholder: simple gun silhouette
        w, h = int(WIDTH*0.28), int(HEIGHT*0.28)
        surf = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (30,30,35,230), (0,0,w,h), border_radius=12)
        pygame.draw.rect(surf, (80,80,95,255), (w*0.55,h*0.35,w*0.4,h*0.2))  # barrel
        pygame.draw.rect(surf, (110,110,125,255), (w*0.35,h*0.45,w*0.25,h*0.35), border_radius=6)  # grip
        return surf

    def make_hand_surface(self) -> pygame.Surface:
        # Placeholder: two hands holding weapon
        w, h = int(WIDTH*0.35), int(HEIGHT*0.22)
        surf = pygame.Surface((w,h), pygame.SRCALPHA)
        # left hand
        pygame.draw.ellipse(surf, (230, 190, 150, 240), (int(w*0.05), int(h*0.45), int(w*0.35), int(h*0.45)))
        # right hand
        pygame.draw.ellipse(surf, (230, 190, 150, 240), (int(w*0.58), int(h*0.45), int(w*0.35), int(h*0.45)))
        return surf

    def draw_weapon_overlay(self):
        # simple bobbing for life
        t = pygame.time.get_ticks() / 1000.0
        bob = int(math.sin(t*6.0) * 4)
        # weapon centered
        ws = self.weapon_surf
        hs = self.hand_surf
        wx = HALF_W - ws.get_width()//2
        wy = HEIGHT - ws.get_height() - 20 + bob
        self.screen.blit(ws, (wx, wy))
        # hands on top
        hx = HALF_W - hs.get_width()//2
        hy = HEIGHT - hs.get_height() - 8 + bob
        self.screen.blit(hs, (hx, hy))

    # ----------------- Main loop -----------------
    def run(self):
        # spawn one NPC initially
        self.spawn_npc()
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_input(dt)
            self.update_npcs(dt)
            rays, zbuffer = self.cast_rays()
            self.render(rays, zbuffer)
        # persist brain on exit
        self.brain.save()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    Engine().run()
