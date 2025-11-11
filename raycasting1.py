import math
import os
import sys
import random
import json

import pygame
from pygame.locals import *

# ---------------- Config ----------------
WIDTH, HEIGHT = 1000, 700
HALF_W, HALF_H = WIDTH // 2, HEIGHT // 2
FPS = 60
FOV = math.radians(70)
MAX_DEPTH = 20.0

worldMap = [
    [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 2, 3, 2, 3, 0, 0, 2],
    [2, 0, 3, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 3, 1, 0, 0, 2, 0, 0, 0, 2, 3, 2, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 2, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 1, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 3, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 3, 2, 1, 2, 0, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 2],
    [2, 3, 1, 0, 0, 2, 0, 0, 2, 1, 3, 2, 0, 2, 0, 0, 3, 0, 3, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 2, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 3, 0, 1, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 3, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 1],
    [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1],
]

MAP_H = len(worldMap)
MAP_W = len(worldMap[0])

PROJ_PLANE_DIST = (WIDTH / 2) / math.tan(FOV / 2)

COLOR_BG = (15, 15, 22)
COLOR_CEIL = (25, 25, 35)
COLOR_FLOOR = (18, 18, 24)
COLOR_MINI_WALL = (60, 60, 80)
COLOR_MINI_FREE = (25, 25, 30)
COLOR_MINI_PLAYER = (120, 200, 255)
COLOR_MINI_NPC = (255, 140, 120)
COLOR_RAY = (255, 220, 90)

MINIMAP_SCALE = 8
MINIMAP_PADDING = 10

BRAIN_PATH = "ai_brain.json"
ALPHA = 0.08
DECAY = 0.995

# ---------------- Utils ----------------
def close():
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)

def is_wall(x, y):
    if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
        return True
    return worldMap[int(y)][int(x)] > 0

# ---------------- Weapon sprites ----------------
def _load_or_make(path, size, draw_fn):
    w, h = size
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (w, h))
    except Exception:
        pass
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_fn(surf)
    return surf

def _draw_hand_pair(surf):
    w, h = surf.get_size()
    skin = (225, 200, 170, 255)
    shadow = (200, 180, 150, 255)

    # left hand
    pygame.draw.rect(
        surf, skin,
        (int(w * 0.18), int(h * 0.55), int(w * 0.16), int(h * 0.30)),
        border_radius=6,
    )
    pygame.draw.rect(
        surf, shadow,
        (int(w * 0.18), int(h * 0.78), int(w * 0.16), int(h * 0.07)),
        border_radius=4,
    )

    # right hand
    pygame.draw.rect(
        surf, skin,
        (int(w * 0.66), int(h * 0.55), int(w * 0.16), int(h * 0.30)),
        border_radius=6,
    )
    pygame.draw.rect(
        surf, shadow,
        (int(w * 0.66), int(h * 0.78), int(w * 0.16), int(h * 0.07)),
        border_radius=4,
    )

def _draw_hands_only(surf):
    _draw_hand_pair(surf)

def _draw_gun_fps(surf):
    w, h = surf.get_size()
    _draw_hand_pair(surf)

    body = (28, 28, 34, 255)
    slide = (52, 52, 64, 255)
    grip = (24, 24, 30, 255)
    accent = (110, 180, 255, 255)

    slide_x = int(w * 0.40)
    slide_y = int(h * 0.40)
    slide_w = int(w * 0.30)
    slide_h = int(h * 0.10)
    pygame.draw.rect(surf, slide, (slide_x, slide_y, slide_w, slide_h), border_radius=3)

    body_x = slide_x
    body_y = slide_y + slide_h - 2
    body_w = int(w * 0.22)
    body_h = int(h * 0.09)
    pygame.draw.rect(surf, body, (body_x, body_y, body_w, body_h), border_radius=3)

    grip_x = body_x + int(w * 0.04)
    grip_y = body_y + body_h - 2
    grip_w = int(w * 0.08)
    grip_h = int(h * 0.16)
    pygame.draw.rect(surf, grip, (grip_x, grip_y, grip_w, grip_h), border_radius=4)

    barrel_w = int(w * 0.10)
    barrel_h = int(h * 0.05)
    barrel_x = slide_x + slide_w - barrel_w
    barrel_y = slide_y + int(slide_h * 0.22)
    pygame.draw.rect(surf, slide, (barrel_x, barrel_y, barrel_w, barrel_h), border_radius=2)

    pygame.draw.rect(
        surf, accent,
        (slide_x + int(w * 0.01), slide_y + int(h * 0.03), int(w * 0.05), int(h * 0.01))
    )

def _draw_knife_fps(surf):
    w, h = surf.get_size()
    _draw_hand_pair(surf)

    handle = (30, 30, 32, 255)
    guard = (80, 80, 90, 255)
    blade = (210, 210, 220, 255)

    handle_w = int(w * 0.06)
    handle_h = int(h * 0.16)
    handle_x = int(w * 0.55)
    handle_y = int(h * 0.46)
    pygame.draw.rect(surf, handle, (handle_x, handle_y, handle_w, handle_h), border_radius=4)

    guard_w = int(w * 0.10)
    guard_h = int(h * 0.015)
    guard_x = handle_x - int((guard_w - handle_w) / 2)
    guard_y = handle_y - guard_h
    pygame.draw.rect(surf, guard, (guard_x, guard_y, guard_w, guard_h), border_radius=3)

    blade_len = int(w * 0.22)
    blade_h_half = int(h * 0.05)
    tip_x = guard_x + blade_len
    tip_y = guard_y - int(h * 0.01)

    pygame.draw.polygon(
        surf,
        blade,
        [
            (guard_x, guard_y),
            (tip_x, tip_y),
            (guard_x, guard_y - blade_h_half),
        ],
    )

def build_weapon_assets(view_w, view_h):
    base_w = max(280, view_w // 3)
    base_h = max(190, view_h // 3)
    return {
        "hands": _load_or_make("assets/hands.png", (base_w, base_h), _draw_hands_only),
        "gun":   _load_or_make("assets/gun.png",   (base_w, base_h), _draw_gun_fps),
        "knife": _load_or_make("assets/knife.png", (base_w, base_h), _draw_knife_fps),
    }

def draw_weapon(screen, assets, selected, sway_xy=(0, 0)):
    surf = assets.get(selected)
    if not surf:
        return None
    w, h = screen.get_size()
    ox, oy = sway_xy
    rect = surf.get_rect()
    rect.midbottom = (w // 2 + ox, h - 6 + oy)
    screen.blit(surf, rect)
    return rect

def _attack_spec(weapon):
    if weapon == "gun":
        return (0.10, 0.12)
    if weapon == "knife":
        return (0.18, 0.22)
    return (0.14, 0.20)

def trigger_attack(weapon, state):
    if state.get("mode", "idle") != "idle":
        return
    if state.get("cooldown", 0.0) > 0.0:
        return
    dur, cd = _attack_spec(weapon)
    state["mode"] = "attack"
    state["t"] = 0.0
    state["dur"] = dur
    state["cooldown"] = cd

def update_weapon_state(weapon, state, dt):
    if state.get("cooldown", 0.0) > 0.0:
        state["cooldown"] -= dt
        if state["cooldown"] < 0.0:
            state["cooldown"] = 0.0
    if state.get("mode") == "attack":
        state["t"] += dt
        if state["t"] >= state.get("dur", _attack_spec(weapon)[0]):
            state["mode"] = "idle"
            state["t"] = 0.0

def weapon_anim_offsets(weapon, state):
    mode = state.get("mode", "idle")
    t = state.get("t", 0.0)
    dur = state.get("dur", _attack_spec(weapon)[0])

    if mode != "attack" or dur <= 0:
        return (0, 0), False, 0.0

    p = max(0.0, min(1.0, t / dur))

    if weapon == "gun":
        up = -10 * math.sin(p * math.pi)
        return (0, int(up)), (p < 0.25), 0.0

    if weapon == "knife":
        forward = -18 * math.sin(p * math.pi)
        side = 8 * math.sin(p * math.pi)
        return (int(side), int(forward)), False, p

    up = -8 * math.sin(p * math.pi)
    return (0, int(up)), False, 0.0

def draw_muzzle_flash(screen, weapon_rect):
    x = weapon_rect.right - 26
    y = weapon_rect.top + 18
    pygame.draw.rect(screen, (255, 245, 210), (x, y, 18, 10))
    pygame.draw.rect(screen, (255, 220, 160), (x - 4, y + 3, 10, 6))

def draw_slash_effect(screen, weapon_rect, p):
    alpha = max(0, int(255 * (1.0 - p)))
    color = (255, 255, 255, alpha)
    surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    x1 = weapon_rect.centerx - int(28 * (1 - p))
    y1 = weapon_rect.centery - 20
    x2 = weapon_rect.centerx + int(32 * (1 - p))
    y2 = weapon_rect.centery + 6

    pygame.draw.line(surf, color, (x1, y1), (x2, y2), 2)
    screen.blit(surf, (0, 0))

# ---------------- NPC + AI ----------------
class NPC:
    def __init__(self, x, y, speed=2.0):
        self.x = float(x)
        self.y = float(y)
        self.speed = float(speed)

class AIBrain:
    """작은 온라인 러닝 브레인: 8방향 + 대기 중에서
    '플레이어와 거리 줄어드는 행동'에 보상."""
    ACTIONS = [
        (0, 0, "stay"),
        (1, 0, "east"), (-1, 0, "west"),
        (0, 1, "south"), (0, -1, "north"),
        (1, 1, "se"), (1, -1, "ne"),
        (-1, 1, "sw"), (-1, -1, "nw"),
    ]

    def __init__(self, path=BRAIN_PATH):
        self.path = path
        self.weights = {name: 1.0 for _, _, name in self.ACTIONS}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for k, v in data.items():
                        if k in self.weights and isinstance(v, (int, float)):
                            self.weights[k] = float(v)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.weights, f, indent=2)
        except Exception:
            pass

    def choose(self, npc=None, player=None):
        names = [name for _, _, name in self.ACTIONS]
        ws = [max(1e-3, self.weights[name]) for name in names]
        total = sum(ws)
        r = random.random() * total
        acc = 0.0
        idx = 0
        for i, w in enumerate(ws):
            acc += w
            if r <= acc:
                idx = i
                break
        dx, dy, name = self.ACTIONS[idx]
        return dx, dy, name

    def learn(self, action_name: str, improved: bool):
        cur = self.weights[action_name]
        if improved:
            cur += ALPHA
        else:
            cur *= DECAY
        # 1.0 쪽으로 살짝 당겨서 폭주 방지
        cur = 0.98 * cur + 0.02 * 1.0
        self.weights[action_name] = max(0.1, min(5.0, cur))

def spawn_npc(npcs, player_x, player_y):
    free = []
    for y in range(MAP_H):
        for x in range(MAP_W):
            if worldMap[y][x] == 0:
                free.append((x + 0.5, y + 0.5))
    random.shuffle(free)
    for x, y in free:
        if (x - player_x) ** 2 + (y - player_y) ** 2 > 9.0:  # 플레이어랑 최소 거리
            npcs.append(NPC(x, y))
            break

def try_move_npc(npc, dx, dy):
    new_x = npc.x + dx
    new_y = npc.y + dy
    if not is_wall(new_x, npc.y):
        npc.x = new_x
    if not is_wall(npc.x, new_y):
        npc.y = new_y

def update_npcs(npcs, brain, dt, player_x, player_y):
    for npc in npcs:
        prev_dist = math.hypot(player_x - npc.x, player_y - npc.y)

        ax, ay, name = brain.choose(npc, None)
        mag = math.hypot(ax, ay)
        if mag > 0:
            ax /= mag
            ay /= mag

        step = npc.speed * dt
        try_move_npc(npc, ax * step, ay * step)

        new_dist = math.hypot(player_x - npc.x, player_y - npc.y)
        brain.learn(name, new_dist < prev_dist)

    if random.random() < 0.02:
        brain.save()

def _draw_npc_placeholder(surf):
    w, h = surf.get_size()
    body = (235, 120, 110, 255)
    head = (245, 210, 190, 255)
    pygame.draw.rect(surf, body,
                     (int(w*0.25), int(h*0.35), int(w*0.5), int(h*0.5)),
                     border_radius=6)
    pygame.draw.rect(surf, head,
                     (int(w*0.30), int(h*0.10), int(w*0.4), int(h*0.25)),
                     border_radius=6)

def build_npc_sprite():
    # assets/npc.png 있으면 그걸 쓰고, 없으면 간단한 사람 실루엣 사용
    return _load_or_make("assets/npc.png", (48, 72), _draw_npc_placeholder)

def render_npcs(screen, npcs, player_x, player_y, dir_x, dir_y, plane_x, plane_y, zbuffer, npc_surf):
    if not npcs or npc_surf is None:
        return

    det = plane_x * dir_y - dir_x * plane_y
    if abs(det) < 1e-6:
        return
    inv_det = 1.0 / det

    sprites = []
    for npc in npcs:
        dx = npc.x - player_x
        dy = npc.y - player_y

        # 월프식 카메라 공간 변환
        transform_x = inv_det * (dir_y * dx - dir_x * dy)
        transform_y = inv_det * (-plane_y * dx + plane_x * dy)

        if transform_y <= 0.01:
            continue  # 카메라 뒤

        sprites.append((transform_y, transform_x, npc))

    # depth 기준 far -> near 정렬 (나중에 그릴수록 가까움)
    sprites.sort(key=lambda s: s[0], reverse=True)

    surf_w, surf_h = npc_surf.get_size()

    for depth, trans_x, npc in sprites:
        # 화면 x 위치
        sprite_screen_x = int((WIDTH / 2) * (1 + trans_x / depth))

        # 거리 기반 스케일
        sprite_h = abs(int(HEIGHT / depth * 0.7))
        sprite_w = int(sprite_h * (surf_w / surf_h))

        NPC_VERTICAL_OFFSET = int(HEIGHT * 0.02) # 대략 화면 높이의 2%만큼 아래로
        draw_start_y = HALF_H - sprite_h // 2 + NPC_VERTICAL_OFFSET
        draw_end_y   = HALF_H + sprite_h // 2 + NPC_VERTICAL_OFFSET
        draw_start_x = sprite_screen_x - sprite_w // 2
        draw_end_x = sprite_screen_x + sprite_w // 2

        if draw_end_x < 0 or draw_start_x >= WIDTH:
            continue

        if draw_start_y < 0:
            draw_start_y = 0
        if draw_end_y >= HEIGHT:
            draw_end_y = HEIGHT - 1

        scaled = pygame.transform.smoothscale(npc_surf, (sprite_w, sprite_h))

        # 한 줄(컬럼)씩, zbuffer 보고 벽보다 앞에 있는 부분만 그림
        for stripe in range(max(draw_start_x, 0), min(draw_end_x, WIDTH - 1)):
            if 0 < depth < zbuffer[stripe]:
                tex_x = stripe - draw_start_x
                if 0 <= tex_x < sprite_w:
                    src_rect = pygame.Rect(tex_x, 0, 1, sprite_h)
                    screen.blit(scaled, (stripe, draw_start_y), src_rect)

# ---------------- Minimap ----------------
def draw_minimap(screen, pos_x, pos_y, dir_x, dir_y, rays, npcs=None):
    mm_w = MAP_W * MINIMAP_SCALE
    mm_h = MAP_H * MINIMAP_SCALE
    ox, oy = MINIMAP_PADDING, MINIMAP_PADDING

    pygame.draw.rect(screen, (12, 12, 16),
                     (ox - 2, oy - 2, mm_w + 4, mm_h + 4),
                     border_radius=6)

    for y in range(MAP_H):
        for x in range(MAP_W):
            rect = pygame.Rect(ox + x * MINIMAP_SCALE,
                               oy + y * MINIMAP_SCALE,
                               MINIMAP_SCALE, MINIMAP_SCALE)
            if worldMap[y][x] != 0:
                pygame.draw.rect(screen, COLOR_MINI_WALL, rect)
            else:
                pygame.draw.rect(screen, COLOR_MINI_FREE, rect)

    if rays:
        step = max(1, len(rays) // 120)
        px = ox + int(pos_x * MINIMAP_SCALE)
        py = oy + int(pos_y * MINIMAP_SCALE)
        for i in range(0, len(rays), step):
            dist, ang = rays[i]
            rx = px + int(math.cos(ang) * dist * MINIMAP_SCALE)
            ry = py + int(math.sin(ang) * dist * MINIMAP_SCALE)
            pygame.draw.line(screen, COLOR_RAY, (px, py), (rx, ry), 1)

    # player
    px = ox + int(pos_x * MINIMAP_SCALE)
    py = oy + int(pos_y * MINIMAP_SCALE)
    pygame.draw.circle(screen, COLOR_MINI_PLAYER, (px, py), 3)
    mag = math.hypot(dir_x, dir_y) or 1.0
    fx = px + int(dir_x / mag * 8)
    fy = py + int(dir_y / mag * 8)
    pygame.draw.line(screen, COLOR_MINI_PLAYER, (px, py), (fx, fy), 2)

    # NPCs
    if npcs:
        for npc in npcs:
            nx = ox + int(npc.x * MINIMAP_SCALE)
            ny = oy + int(npc.y * MINIMAP_SCALE)
            pygame.draw.circle(screen, COLOR_MINI_NPC, (nx, ny), 3)

# ---------------- Raycasting ----------------
def cast_rays(pos_x, pos_y, dir_x, dir_y, plane_x, plane_y):
    zbuffer = [MAX_DEPTH] * WIDTH
    rays_for_minimap = []

    for col in range(WIDTH):
        camera_x = 2.0 * col / WIDTH - 1.0
        ray_dir_x = dir_x + plane_x * camera_x
        ray_dir_y = dir_y + plane_y * camera_x

        map_x = int(pos_x)
        map_y = int(pos_y)

        delta_x = abs(1.0 / ray_dir_x) if ray_dir_x != 0 else 1e30
        delta_y = abs(1.0 / ray_dir_y) if ray_dir_y != 0 else 1e30

        if ray_dir_x < 0:
            step_x = -1
            side_x = (pos_x - map_x) * delta_x
        else:
            step_x = 1
            side_x = (map_x + 1.0 - pos_x) * delta_x

        if ray_dir_y < 0:
            step_y = -1
            side_y = (pos_y - map_y) * delta_y
        else:
            step_y = 1
            side_y = (map_y + 1.0 - pos_y) * delta_y

        hit = False
        side = 0

        for _ in range(256):
            if side_x < side_y:
                side_x += delta_x
                map_x += step_x
                side = 0
            else:
                side_y += delta_y
                map_y += step_y
                side = 1

            if map_x < 0 or map_y < 0 or map_x >= MAP_W or map_y >= MAP_H:
                break

            if worldMap[map_y][map_x] > 0:
                hit = True
                break

        if not hit:
            zbuffer[col] = MAX_DEPTH
            rays_for_minimap.append((MAX_DEPTH, math.atan2(ray_dir_y, ray_dir_x)))
            continue

        if side == 0:
            perp = (map_x - pos_x + (1 - step_x) / 2.0) / (ray_dir_x or 1e-6)
        else:
            perp = (map_y - pos_y + (1 - step_y) / 2.0) / (ray_dir_y or 1e-6)

        if perp <= 0:
            perp = 0.0001

        zbuffer[col] = perp
        rays_for_minimap.append((perp, math.atan2(ray_dir_y, ray_dir_x)))

    return zbuffer, rays_for_minimap

def render_walls(screen, zbuffer):
    screen.fill(COLOR_BG)
    pygame.draw.rect(screen, COLOR_CEIL, (0, 0, WIDTH, HALF_H))
    pygame.draw.rect(screen, COLOR_FLOOR, (0, HALF_H, WIDTH, HALF_H))

    for col, dist in enumerate(zbuffer):
        if dist >= MAX_DEPTH:
            continue

        shade = max(0.15, min(1.0, 4.0 / (dist + 0.2)))
        base = 190
        color = (int(base * shade), int(base * shade), int((base + 10) * shade))

        line_h = int((1.0 / dist) * PROJ_PLANE_DIST)
        y1 = HALF_H - line_h // 2
        y2 = HALF_H + line_h // 2

        pygame.draw.line(screen, color, (col, y1), (col, y2))

# ---------------- Main ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PyRay — raycasting + weapon + NPC sprite")

    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    pos_x, pos_y = 3.0, 7.0
    dir_x, dir_y = 1.0, 0.0
    plane_x, plane_y = 0.0, 0.66

    move_speed = 3.0
    rot_speed = math.radians(120)

    show_minimap = True
    show_hud = True

    selected_weapon = "hands"
    weapon_assets = build_weapon_assets(WIDTH, HEIGHT)
    weapon_state = {"mode": "idle", "t": 0.0, "cooldown": 0.0, "dur": 0.0}
    weapon_phase = 0.0

    npcs = []
    brain = AIBrain()
    npc_surf = build_npc_sprite()
    spawn_npc(npcs, pos_x, pos_y)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_F7:
                    show_hud = not show_hud
                elif event.key == K_F9:
                    show_minimap = not show_minimap
                elif event.key == K_1:
                    selected_weapon = "hands"
                elif event.key == K_2:
                    selected_weapon = "gun"
                elif event.key == K_3:
                    selected_weapon = "knife"
                elif event.key == K_SPACE:
                    trigger_attack(selected_weapon, weapon_state)
                elif event.key == K_n:
                    spawn_npc(npcs, pos_x, pos_y)
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                trigger_attack(selected_weapon, weapon_state)

        keys = pygame.key.get_pressed()

        # 이동 (WASD + 방향키)
        fx, fy = dir_x, dir_y
        rx, ry = dir_y, -dir_x

        if keys[K_w] or keys[K_UP]:
            nx = pos_x + fx * move_speed * dt
            ny = pos_y + fy * move_speed * dt
            if not is_wall(nx, pos_y):
                pos_x = nx
            if not is_wall(pos_x, ny):
                pos_y = ny

        if keys[K_s] or keys[K_DOWN]:
            nx = pos_x - fx * move_speed * dt
            ny = pos_y - fy * move_speed * dt
            if not is_wall(nx, pos_y):
                pos_x = nx
            if not is_wall(pos_x, ny):
                pos_y = ny

        if keys[K_a]:
            nx = pos_x - rx * move_speed * dt
            ny = pos_y - ry * move_speed * dt
            if not is_wall(nx, pos_y):
                pos_x = nx
            if not is_wall(pos_x, ny):
                pos_y = ny

        if keys[K_d]:
            nx = pos_x + rx * move_speed * dt
            ny = pos_y + ry * move_speed * dt
            if not is_wall(nx, pos_y):
                pos_x = nx
            if not is_wall(pos_x, ny):
                pos_y = ny

        # 회전 (좌/우)
        if keys[K_LEFT]:
            ang = -rot_speed * dt
            ca, sa = math.cos(ang), math.sin(ang)
            ndx = dir_x * ca - dir_y * sa
            ndy = dir_x * sa + dir_y * ca
            dir_x, dir_y = ndx, ndy
            npx = plane_x * ca - plane_y * sa
            npy = plane_x * sa + plane_y * ca
            plane_x, plane_y = npx, npy

        if keys[K_RIGHT]:
            ang = rot_speed * dt
            ca, sa = math.cos(ang), math.sin(ang)
            ndx = dir_x * ca - dir_y * sa
            ndy = dir_x * sa + dir_y * ca
            dir_x, dir_y = ndx, ndy
            npx = plane_x * ca - plane_y * sa
            npy = plane_x * sa + plane_y * ca
            plane_x, plane_y = npx, npy

        # 무기 / NPC 갱신
        update_weapon_state(selected_weapon, weapon_state, dt)
        update_npcs(npcs, brain, dt, pos_x, pos_y)

        # 월드 렌더
        zbuffer, rays_for_minimap = cast_rays(pos_x, pos_y, dir_x, dir_y, plane_x, plane_y)
        render_walls(screen, zbuffer)
        render_npcs(screen, npcs, pos_x, pos_y, dir_x, dir_y, plane_x, plane_y, zbuffer, npc_surf)

        # 미니맵
        if show_minimap:
            draw_minimap(screen, pos_x, pos_y, dir_x, dir_y, rays_for_minimap, npcs)

        # 무기 흔들림 + 공격 오프셋
        moving = (
            keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d] or
            keys[K_UP] or keys[K_DOWN]
        )
        weapon_phase += (5.0 if moving else 1.5) * dt
        sway_x = int(1.5 * math.sin(weapon_phase * 2.0))
        sway_y = int(2.5 * math.sin(weapon_phase * 1.0))

        (atk_dx, atk_dy), flash_on, slash_p = weapon_anim_offsets(selected_weapon, weapon_state)
        total_dx = sway_x + atk_dx
        total_dy = sway_y + atk_dy

        rect = draw_weapon(screen, weapon_assets, selected_weapon, (total_dx, total_dy))
        if rect:
            if selected_weapon == "gun" and flash_on:
                draw_muzzle_flash(screen, rect)
            if selected_weapon == "knife" and weapon_state.get("mode") == "attack":
                draw_slash_effect(screen, rect, slash_p)

        # HUD
        if show_hud:
            info = f"FPS {int(clock.get_fps()):3d}  Pos({pos_x:.2f},{pos_y:.2f})  NPCs:{len(npcs)}  Weapon:{selected_weapon}"
            hud = font.render(info, True, (200, 200, 210))
            pygame.draw.rect(screen, (20, 20, 30), (0, HEIGHT - 26, WIDTH, 26))
            screen.blit(hud, (10, HEIGHT - 23))

        pygame.display.flip()

    brain.save()
    close()

if __name__ == "__main__":
    main()
