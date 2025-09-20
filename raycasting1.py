# try:
import math
import time
import pygame
from pygame.locals import *
import os  # NEW

# except ImportError:
#     print("PyRay could not import necessary modules")
#     raise ImportError

# A map over the world
worldMap =  [
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
            [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]]

# Closes the program 
def close(): 
    pygame.display.quit()
    pygame.quit()

def draw_minimap(screen, worldMap, posX, posY, dirX, dirY, rays,
                 scale=8, padding=10):
    """
    screen: pygame Surface
    worldMap: 2D list[int] (0 = free, >0 = wall)
    posX, posY: player position in world units (map cells)
    dirX, dirY: player facing direction vector (normalized-ish)
    rays: list of tuples (perp_dist, (rayDirX, rayDirY))
    scale: pixels per map cell on minimap
    padding: minimap margin from top-left
    """
    MAP_H = len(worldMap)
    MAP_W = len(worldMap[0]) if MAP_H else 0

    mm_w = MAP_W * scale
    mm_h = MAP_H * scale
    ox, oy = padding, padding

    COLOR_BG_BORDER = (12, 12, 16)
    COLOR_MINI_WALL  = (80, 80, 100)
    COLOR_MINI_FREE  = (28, 28, 32)
    COLOR_RAY        = (255, 215, 0)
    COLOR_PLAYER     = (50, 200, 255)

    # background
    pygame.draw.rect(screen, COLOR_BG_BORDER, (ox - 2, oy - 2, mm_w + 4, mm_h + 4), border_radius=6)

    # tiles
    for r in range(MAP_H):
        for c in range(MAP_W):
            rect = pygame.Rect(ox + c * scale, oy + r * scale, scale, scale)
            if worldMap[r][c] != 0:
                pygame.draw.rect(screen, COLOR_MINI_WALL, rect)
            else:
                pygame.draw.rect(screen, COLOR_MINI_FREE, rect)

    # rays (downsample to avoid overdraw)
    if rays:
        step = max(1, len(rays) // 120)
        px = ox + int(posY * scale)  # NOTE: map indexing worldMap[row][col] = [x][y]
        py = oy + int(posX * scale)  # but in your engine posX ~ mapX, posY ~ mapY
        # 위 두 줄은 엔진의 좌표 사용 방식(X/Y ↔ row/col)을 맞추기 위한 보정.
        # 만약 맵 인덱싱/좌표가 일치한다면 px/py 계산을 (posX,posY) 그대로 써도 됨.

        for i in range(0, len(rays), step):
            dist, (rDx, rDy) = rays[i]
            # 방향 정규화 후, 거리(perp)만큼 쏴서 끝점
            mag = math.hypot(rDx, rDy) or 1.0
            ux, uy = rDx / mag, rDy / mag
            rx = px + int(uy * dist * scale)  # 좌표계 축 교차 보정
            ry = py + int(ux * dist * scale)
            pygame.draw.line(screen, COLOR_RAY, (px, py), (rx, ry), 1)

    # player
    px = ox + int(posY * scale)
    py = oy + int(posX * scale)
    pygame.draw.circle(screen, COLOR_PLAYER, (px, py), 3)

    # facing indicator (direction vector)
    magd = math.hypot(dirX, dirY) or 1.0
    fx = px + int(dirY / magd * 8)
    fy = py + int(dirX / magd * 8)
    pygame.draw.line(screen, COLOR_PLAYER, (px, py), (fx, fy), 2)

# --- NEW: 무기 스프라이트 로드/플레이스홀더 및 애니메이션 유틸 ---
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

def _draw_hands_placeholder(surf):
    w, h = surf.get_size()
    skin = (235, 205, 175, 235)
    shade = (210, 180, 150, 235)
    pygame.draw.ellipse(surf, skin,  (int(w*0.05),  int(h*0.50), int(w*0.40), int(h*0.45)))
    pygame.draw.ellipse(surf, skin,  (int(w*0.55),  int(h*0.50), int(w*0.40), int(h*0.45)))
    pygame.draw.ellipse(surf, shade, (int(w*0.08),  int(h*0.68), int(w*0.16), int(h*0.18)))
    pygame.draw.ellipse(surf, shade, (int(w*0.62),  int(h*0.68), int(w*0.16), int(h*0.18)))

def _draw_knife_placeholder(surf):
    _draw_hands_placeholder(surf)
    w, h = surf.get_size()
    handle = (30, 30, 30, 255)
    blade  = (200, 200, 210, 255)
    pygame.draw.rect(surf, handle, (int(w*0.45), int(h*0.60), int(w*0.10), int(h*0.20)), border_radius=4)
    pygame.draw.polygon(
        surf, blade,
        [(int(w*0.50), int(h*0.60)),
         (int(w*0.70), int(h*0.30)),
         (int(w*0.58), int(h*0.60))]
    )

def _draw_gun_placeholder(surf):
    _draw_hands_placeholder(surf)
    w, h = surf.get_size()
    body  = (35, 35, 45, 255)
    grip  = (25, 25, 30, 255)
    barrel= (55, 55, 65, 255)
    pygame.draw.rect(surf, body,   (int(w*0.35), int(h*0.48), int(w*0.30), int(h*0.14)), border_radius=6)
    pygame.draw.rect(surf, grip,   (int(w*0.52), int(h*0.58), int(w*0.10), int(h*0.18)), border_radius=4)
    pygame.draw.rect(surf, barrel, (int(w*0.62), int(h*0.52), int(w*0.18), int(h*0.08)), border_radius=4)

def build_weapon_assets(view_w, view_h):
    base_w = max(240, view_w // 3)
    base_h = max(180, view_h // 3)
    assets = {
        "hands": _load_or_make("assets/hands.png", (base_w, base_h), _draw_hands_placeholder),
        "knife": _load_or_make("assets/knife.png", (base_w, base_h), _draw_knife_placeholder),
        "gun":   _load_or_make("assets/gun.png",   (base_w, base_h), _draw_gun_placeholder),
    }
    return assets

def draw_weapon(screen, assets, selected, sway_xy=(0,0)):
    """현재 선택된 무기를 화면 하단 중앙에 그린다(약간의 흔들림 적용). 반환값: blit된 rect"""
    surf = assets.get(selected)
    if not surf:
        return None
    w, h = screen.get_size()
    ox, oy = sway_xy
    rect = surf.get_rect()
    rect.midbottom = (w // 2 + ox, h - 8 + oy)  # 아래 여백 8px
    screen.blit(surf, rect)
    return rect

def _attack_spec(weapon: str):
    if weapon == "knife": return (0.18, 0.25)  # (duration, cooldown)
    if weapon == "gun":   return (0.12, 0.15)
    return (0.20, 0.25)   # hands

def trigger_attack(weapon: str, state: dict):
    dur, cd = _attack_spec(weapon)
    if state.get("mode", "idle") == "idle" and state.get("cooldown", 0.0) <= 0.0:
        state["mode"] = "attack"
        state["t"] = 0.0
        state["dur"] = dur
        state["cooldown"] = cd

def update_weapon_state(weapon: str, state: dict, dt: float):
    if state.get("cooldown", 0.0) > 0.0:
        state["cooldown"] -= dt
        if state["cooldown"] < 0.0: state["cooldown"] = 0.0
    if state.get("mode", "idle") == "attack":
        state["t"] += dt
        dur = state.get("dur", _attack_spec(weapon)[0])
        if state["t"] >= dur:
            state["mode"] = "idle"
            state["t"] = 0.0

def _ease_out_quad(x: float) -> float:
    return 1.0 - (1.0 - x) * (1.0 - x)

def weapon_anim_offsets(weapon: str, state: dict):
    if state.get("mode") != "attack":
        return (0, 0), False, 0.0
    dur = state.get("dur", _attack_spec(weapon)[0])
    p = max(0.0, min(1.0, state.get("t", 0.0) / dur))
    if weapon == "knife":
        dx = int(18 * math.sin(p * math.pi))
        dy = int(8  * math.sin(p * math.pi))
        flash = False
    elif weapon == "gun":
        dx = 0
        dy = -int(14 * _ease_out_quad(p))
        flash = (state["t"] < min(0.05, dur * 0.45))
    else:  # hands
        dx = 0
        dy = -int(10 * math.sin(p * math.pi))
        flash = False
    return (dx, dy), flash, p

def draw_muzzle_flash(screen, weapon_rect):
    w, h = weapon_rect.size
    x0 = weapon_rect.right - int(w * 0.12)
    y0 = weapon_rect.top   + int(h * 0.52)
    pts = [
        (x0, y0),
        (x0 + int(w * 0.10), y0 - int(h * 0.03)),
        (x0 + int(w * 0.12), y0 + int(h * 0.02)),
    ]
    pygame.draw.polygon(screen, (255, 240, 180), pts)
    pygame.draw.polygon(screen, (255, 255, 220), pts, width=1)

def draw_slash_effect(screen, weapon_rect, p: float):
    w, h = weapon_rect.size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    x = int(w * (0.50 + 0.25 * p))
    y = int(h * (0.50 - 0.10 * math.sin(p * math.pi)))
    tri = [(x, y - 12), (x + 48, y), (x, y + 12)]
    alpha = int(200 * (1.0 - p))
    pygame.draw.polygon(surf, (255, 255, 255, alpha), tri)
    screen.blit(surf, weapon_rect.topleft)

def main():
    pygame.init()

    # Head Up Display information (HUD)
    font = pygame.font.SysFont("Verdana",20)
    HUD = font.render("F1 / F2 - Screenshot JPEG/BMP   F5/F6 - Shadows on/off   F7/F8 - HUD Show/Hide", True, (0,0,0))

    # Creates window 
    WIDTH = 1000
    HEIGHT = 700
    WALL_HEIGHT = HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PyRay - Python Raycasting Engine (v0.03)")

    # --- NEW: 무기/애니메이션 상태 및 에셋/시계 ---
    selected_weapon = "hands"           # 기본 무기
    weapon_phase = 0.0                  # 흔들림 위상
    weapon_state = {"mode": "idle", "t": 0.0, "cooldown": 0.0, "dur": 0.0}
    weapon_assets = build_weapon_assets(WIDTH, HEIGHT)
    clock = pygame.time.Clock()

    showShadow = True
    showHUD = True    
    
    # Defines starting position and direction
    positionX = 3.0
    positionY = 7.0

    directionX = 1.0
    directionY = 0.0

    planeX = 0.0
    planeY = 0.5

    # Movement constants   
    ROTATIONSPEED = 0.02
    MOVESPEED = 0.03

    # Trigeometric tuples + variables for index
    TGM = (math.cos(ROTATIONSPEED), math.sin(ROTATIONSPEED))
    ITGM = (math.cos(-ROTATIONSPEED), math.sin(-ROTATIONSPEED))
    COS, SIN = (0,1)
    
    while True:
        # Catches user input
        # Sets keys[key] to True or False
        # keys = pygame.key.get_pressed()
        dt = clock.tick(60) / 1000.0  # NEW: 프레임 경과시간(초)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    close()
                    return
                # keys[event.key] = True
                # NEW: 무기 전환 & 공격
                if event.key == K_1:
                    selected_weapon = "knife"
                elif event.key == K_3:
                    selected_weapon = "gun"
                elif event.key == K_2:
                    selected_weapon = "hands"
                elif event.key == K_SPACE:
                    trigger_attack(selected_weapon, weapon_state)
            # elif event.type == KEYUP:
            #     keys[event.key] = False
            # NEW: 창 닫기(X) & 마우스 좌클릭 공격
            if event.type == QUIT:
                close()
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                trigger_attack(selected_weapon, weapon_state)

        # Checks with keys are pressed by the user
        # Uses if so that more than one button at a time can be pressed.  
        keys = pygame.key.get_pressed()

        if keys[K_ESCAPE]:
            close()

        if keys[K_LEFT]:
            oldDirectionX = directionX
            directionX = directionX * ITGM[COS] - directionY * ITGM[SIN]
            directionY = oldDirectionX * ITGM[SIN] + directionY * ITGM[COS]
            oldPlaneX = planeX
            planeX = planeX * ITGM[COS] - planeY * ITGM[SIN]
            planeY = oldPlaneX * ITGM[SIN] + planeY * ITGM[COS]

        if keys[K_RIGHT]:
            oldDirectionX = directionX
            directionX = directionX * TGM[COS] - directionY * TGM[SIN]
            directionY = oldDirectionX * TGM[SIN] + directionY * TGM[COS]
            oldPlaneX = planeX
            planeX = planeX * TGM[COS] - planeY * TGM[SIN]
            planeY = oldPlaneX * TGM[SIN] + planeY * TGM[COS]    

        if keys[K_UP]:
            if not worldMap[int(positionX + directionX * MOVESPEED)][int(positionY)]:
                positionX += directionX * MOVESPEED
            if not worldMap[int(positionX)][int(positionY + directionY * MOVESPEED)]:
                positionY += directionY * MOVESPEED
                
        if keys[K_DOWN]:
            if not worldMap[int(positionX - directionX * MOVESPEED)][int(positionY)]:
                positionX -= directionX * MOVESPEED
            if not worldMap[int(positionX)][int(positionY - directionY * MOVESPEED)]:
                positionY -= directionY * MOVESPEED

        if keys[K_F1]:
            try:
                pygame.image.save(screen,('PyRay' + time.strftime('%Y%m%d%H%M%S')+ '.jpeg'))
            except:
                print("Couldn't save jpeg screenshot")
                
        if keys[K_F2]:
            try:
                pygame.image.save(screen,('PyRay' + time.strftime('%Y%m%d%H%M%S')+ '.bmp'))
            except:
                print("Couldn't save bmp screenshot")

        # showShadows - On / Off
        if keys[K_F5]:
            showShadow = True
        if keys[K_F6]:
            showShadow = False

        # showHUD - Show / Hide
        if keys[K_F7]:
            showHUD = True
            print("K_F7:", keys[K_F7])
        if keys[K_F8]:
            showHUD = False
            print("K_F8:", keys[K_F8])

        # --- NEW: 무기 애니메이션 상태 업데이트 ---
        update_weapon_state(selected_weapon, weapon_state, dt)

        # Draws roof and floor
        screen.fill((25,25,25))
        pygame.draw.rect(screen, (50,50,50), (0, HEIGHT/2, WIDTH, HEIGHT/2)) 

        rays_for_minimap = []  # [(perpWallDistance, (rayDirectionX, rayDirectionY)), ...]

        # Starts drawing level from 0 to < WIDTH 
        column = 0        
        while column < WIDTH:
            # Setting FOV
            cameraX = 2.0 * column / WIDTH - 1.0
            rayPositionX = positionX
            rayPositionY = positionY
            rayDirectionX = directionX + planeX * cameraX
            rayDirectionY = directionY + planeY * cameraX + .000000000000001 # avoiding ZDE 

            # In what square is the ray?
            mapX = int(rayPositionX)
            mapY = int(rayPositionY)

            # Delta distance calculation
            # Delta = square ( raydir * raydir) / (raydir * raydir)
            deltaDistanceX = math.sqrt(1.0 + (rayDirectionY * rayDirectionY) / (rayDirectionX * rayDirectionX))
            deltaDistanceY = math.sqrt(1.0 + (rayDirectionX * rayDirectionX) / (rayDirectionY * rayDirectionY))

            # We need sideDistanceX and Y for distance calculation. Checks quadrant
            if (rayDirectionX < 0):
                stepX = -1
                sideDistanceX = (rayPositionX - mapX) * deltaDistanceX

            else:
                stepX = 1
                sideDistanceX = (mapX + 1.0 - rayPositionX) * deltaDistanceX

            if (rayDirectionY < 0):
                stepY = -1
                sideDistanceY = (rayPositionY - mapY) * deltaDistanceY

            else:
                stepY = 1
                sideDistanceY = (rayPositionY - mapY) * deltaDistanceY

            # Finding distance to a wall
            hit = 0
            while  (hit == 0):
                if (sideDistanceX < sideDistanceY):
                    sideDistanceX += deltaDistanceX
                    mapX += stepX
                    side = 0
                    
                else:
                    sideDistanceY += deltaDistanceY
                    mapY += stepY
                    side = 1
                    
                if (worldMap[mapX][mapY] > 0):
                    hit = 1

            # Correction against fish eye effect
            if (side == 0):
                perpWallDistance = abs((mapX - rayPositionX + ( 1.0 - stepX ) / 2.0) / rayDirectionX)
            else:
                perpWallDistance = abs((mapY - rayPositionY + ( 1.0 - stepY ) / 2.0) / rayDirectionY)

            # Calculating HEIGHT of the line to draw
            lineHEIGHT = abs(int(WALL_HEIGHT / (perpWallDistance+.0000001)))
            drawStart = -lineHEIGHT / 2.0 + WALL_HEIGHT / 2.0

            # if drawStat < 0 it would draw outside the screen
            if (drawStart < 0):
                drawStart = 0

            drawEnd = lineHEIGHT / 2.0 + WALL_HEIGHT / 2.0

            if (drawEnd >= WALL_HEIGHT):
                drawEnd = WALL_HEIGHT - 1

            # Wall colors 0 to 3
            wallcolors = [ [], [150,0,0], [0,150,0], [0,0,150] ]
            color = wallcolors[ worldMap[mapX][mapY] ]                                  

            # If side == 1 then ton the color down. Gives a "showShadow" an the wall.
            # Draws showShadow if showShadow is True
            # Depth based shadow
            if showShadow:
                if side == 1:
                    for i,v in enumerate(color):
                        color[i] = int(v / 1.2)                    

            # Drawing the graphics                           
            pygame.draw.line(screen, color, (column,drawStart), (column, drawEnd), 2)
            rays_for_minimap.append( (perpWallDistance, (rayDirectionX, rayDirectionY)) )
            column += 2

        draw_minimap(screen, worldMap, positionX, positionY, directionX, directionY, rays_for_minimap)

        # --- NEW: 무기 흔들림 + 공격 오프셋 & 이펙트 렌더 ---
        moving = keys[K_UP] or keys[K_DOWN] or keys[K_LEFT] or keys[K_RIGHT]
        weapon_phase += 0.12 if moving else 0.05
        sway_x = int(2 * math.sin(weapon_phase * 2.0))
        sway_y = int(3 * math.sin(weapon_phase * 1.0))

        (atk_dx, atk_dy), flash_on, slash_p = weapon_anim_offsets(selected_weapon, weapon_state)
        total_dx = sway_x + atk_dx
        total_dy = sway_y + atk_dy

        weapon_rect = draw_weapon(screen, weapon_assets, selected_weapon, (total_dx, total_dy))
        if weapon_rect:
            if selected_weapon == "gun" and flash_on:
                draw_muzzle_flash(screen, weapon_rect)
            if selected_weapon == "knife" and weapon_state.get("mode") == "attack":
                draw_slash_effect(screen, weapon_rect, slash_p)

        # Drawing HUD if showHUD is True
        if showHUD:
            pygame.draw.rect(screen, (100,100,200), (0, HEIGHT-40, WIDTH, 40))
            screen.blit(HUD, (20,HEIGHT-30))

        # Updating display
        pygame.event.pump()
        pygame.display.flip()           
       
main()

# 1. What is the way of exiting the game? -> esc button -> how can we exit the game with cloes(x) button
# 2. Where the player start? -> Could you trap the player?
# 3. There are two ways of shooting rays.
# 4. Where do we set FOV & DDA(Digital Differential Analyzer)
# 5. Where do we increase height?
