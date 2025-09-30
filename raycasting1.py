# try:
import random
import os
import math
import time
import pygame
from pygame.locals import *

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

MINIMAP_SCALE = 8  # pixels per tile on the minimap
MINIMAP_PADDING = 10
COLOR_MINI_WALL = (60, 60, 80)
COLOR_MINI_FREE = (25, 25, 30)
COLOR_MINI_PLAYER = (120, 200, 255)
COLOR_RAY = (255, 215, 0)

def draw_minimap(screen, worldMap, posX, posY, dirX, dirY, rays, scale=8, padding=10):
    MAP_W = len(worldMap)
    MAP_H = len(worldMap[0])
    mm_w = MAP_W * MINIMAP_SCALE
    mm_h = MAP_H * MINIMAP_SCALE
    ox = MINIMAP_PADDING
    oy = MINIMAP_PADDING
    pygame.draw.rect(screen, (12, 12, 16), (ox - 2, oy - 2, mm_w + 4, mm_h + 4), border_radius=6)
    for r in range(MAP_H):
        for c in range(MAP_W):
            rect = pygame.Rect(ox + c * MINIMAP_SCALE, oy + r * MINIMAP_SCALE, MINIMAP_SCALE, MINIMAP_SCALE)
            if worldMap[r][c] != 0:
                pygame.draw.rect(screen, COLOR_MINI_WALL, rect)
            else:
                pygame.draw.rect(screen, COLOR_MINI_FREE, rect)
    
    if rays:
        step = max(1, len(rays) // 120)
        px = ox + int(posY * scale)
        py = oy + int(posX * scale)

        for i in range(0, len(rays), step):
            dist, (rDx, rDy) = rays[i]
            mag = math.hypot(rDx, rDy) or 1.0
            ux, uy = rDx / mag, rDy / mag
            rx = px + int(uy * dist * scale)
            ry = py + int(ux * dist * scale)
            pygame.draw.line(screen, COLOR_RAY, (px, py), (rx, ry), 1)
    px = ox + int(posY * MINIMAP_SCALE)
    py = oy + int(posX * MINIMAP_SCALE)
    pygame.draw.circle(screen, COLOR_MINI_PLAYER, (px, py), 3)
    
    magd = math.hypot(dirX, dirY) or 1.0
    fx = px + int(dirY / magd * 8)
    fy = py + int(dirX / magd * 8)
    pygame.draw.line(screen, COLOR_MINI_PLAYER, (px, py), (fx, fy), 2)



def draw_hands(surf):
    w, h = surf.get_size()
    skin = (235, 205, 175, 235)
    shade = (210, 180, 150, 235)
    pygame.draw.ellipse(surf, skin,  (int(w*0.05),  int(h*0.50), int(w*0.40), int(h*0.45)))
    pygame.draw.ellipse(surf, skin,  (int(w*0.55),  int(h*0.50), int(w*0.40), int(h*0.45)))
    pygame.draw.ellipse(surf, shade, (int(w*0.08),  int(h*0.68), int(w*0.16), int(h*0.18)))
    pygame.draw.ellipse(surf, shade, (int(w*0.62),  int(h*0.68), int(w*0.16), int(h*0.18)))


def draw_knife(surf):
    draw_hands(surf)
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
    
def draw_gun(surf):
    draw_hands(surf)
    w, h = surf.get_size()
    body = (100, 100, 100, 255)
    grip = (200, 200, 200, 255)
    barrel= (55, 55, 65, 255)
    pygame.draw.rect(surf, body,   (int(w*0.35), int(h*0.48), int(w*0.30), int(h*0.14)), border_radius=6)
    pygame.draw.rect(surf, grip,   (int(w*0.52), int(h*0.58), int(w*0.10), int(h*0.18)), border_radius=4)
    pygame.draw.rect(surf, barrel, (int(w*0.62), int(h*0.52), int(w*0.18), int(h*0.08)), border_radius=4)
  
def load_or_make(path, size, draw_fn):
    w, h = size
    try:
        if os.path.exists(path):
            print(".")
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (w, h))
    except Exception:
        pass
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_fn(surf)
    return surf
    
def build_weapon_assets(view_w, view_h):
    base_w = max(240, view_w // 3)
    base_h = max(180, view_h // 3)
    assets = {
        "hands": load_or_make("assets/hands.png", (base_w, base_h), draw_hands),
      	"gun" : load_or_make("assets/gun.png", (base_w, base_h), draw_gun),
        "knife": load_or_make("assets/knife.png", (base_w, base_h), draw_knife)
    }
    return assets


# def update_weapon(weapon):
#     if weapon = "hands":
    
#     elif weapon = "gun":
    
#     elif weapon = "knife"
  
def draw_weapon(screen, assets, weapon, xy=(0,0)):
    w, h = screen.get_size()
    surf = assets.get(weapon)
    rect = surf.get_rect()
    ox, oy = xy
    rect.midbottom = (w // 2 + ox, h - 8 + oy)
    screen.blit(surf, rect)
    return rect

def trigger_attack(weapon, state):
    if state.get("mode", "idle") == "idle" and state.get("cooldown", 0.0) <= 0.0:
        if weapon == "gun":
            state["mode"] = "attack"
            state["t"] = 0.0
            state["dur"] = 0.10      # 공격 애니 길이
            state["cooldown"] = 0.20 # 쿨다운
        elif weapon == "knife":
            state["mode"] = "attack"
            state["t"] = 0.0
            state["dur"] = 0.20
            state["cooldown"] = 0.30
      
  
def animation_offset(weapon, state):
    dur = state.get("dur", 0.1)
    p = max(0.0, min(1.0, state.get("t", 0.0) / (dur if dur > 0 else 0.1)))
    flash = False
    if weapon == "knife":
        dx = int(14 *  math.sin(p * math.pi))
        dy = int(8  *  math.sin(p * math.pi))
    elif weapon == "gun":
        dx = 0
        dy = -int(10 * math.sin(p * math.pi))
        flash = (state.get("t", 0.0) < min(0.05, dur * 0.45))  # <- 키 에러 방지
    else:  # hands
        dx = 0
        dy = -int(10 * math.sin(p * math.pi))
    return dx, dy, flash, p

# def _ease_out_quad(x: float) -> float:
#     return 1.0 - (1.0 - x) * (1.0 - x)
  
def update_weapon_state(weapon, state, dt):
    if state.get("cooldown", 0.0) > 0.0:
        state["cooldown"] -= dt
    if state.get("mode", "idle") == "attack":
        state["t"] += dt
        dur = state.get("dur")
        if state["t"] >= dur:
            state["mode"] = "idle"
            state["t"] = 0.0

def draw_muzzle_flash(screen, weapon_rect):
    mx = weapon_rect.right - int(weapon_rect.width * 0.12)
    my = weapon_rect.top   + int(weapon_rect.height * 0.20)

    poly = [
        (mx, my - 8),
        (mx + 26, my),
        (mx, my + 8)
    ]
    pygame.draw.polygon(screen, (255, 245, 200), poly)
    pygame.draw.circle(screen, (255, 240, 180), (mx + 10, my), 6)

def main():
    pygame.init()

    # Head Up Display information (HUD)
    font = pygame.font.SysFont("Verdana",20)
    HUD = font.render("F1 / F2 - Screenshot JPEG/BMP   F5/F6 - Shadows on/off   F7/F8 - HUD Show/Hide", True, (0,0,0))

    # Creates window 
    WIDTH = 800
    HEIGHT = 600
    WALL_HEIGHT = HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PyRay - Python Raycasting Engine (v0.03)")

    # Animation
    # weapon_phase = 0.0 
    weapon_state = {"mode":"idle", "t":0.0, "cooldown":0.0, "dur":0.0}
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

    dx = 0
    dy = 0

    weapon = "hands"
    weapon_assets = build_weapon_assets(WIDTH, HEIGHT)
    
    while True:
        # Catches user input
        # Sets keys[key] to True or False
        # keys = pygame.key.get_pressed()
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    close()
                    return
                if event.key == K_1: #손
                    weapon = "hands" 
                elif event.key == K_2: #권총
                    weapon = "gun"
                elif event.key == K_3: #칼
                    weapon = "knife"
                # elif event.key == K_SPACE:
                # keys[event.key] = True
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                trigger_attack(weapon, weapon_state)
            # elif event.type == KEYUP:
            #     keys[event.key] = False
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
            # dx, dy = animation_offset(weapon)



        if keys[K_RIGHT]:
            oldDirectionX = directionX
            directionX = directionX * TGM[COS] - directionY * TGM[SIN]
            directionY = oldDirectionX * TGM[SIN] + directionY * TGM[COS]
            oldPlaneX = planeX
            planeX = planeX * TGM[COS] - planeY * TGM[SIN]
            planeY = oldPlaneX * TGM[SIN] + planeY * TGM[COS]    
            # dx, dy = animation_offset(weapon)
     

        if keys[K_UP]:
            if not worldMap[int(positionX + directionX * MOVESPEED)][int(positionY)]:
                positionX += directionX * MOVESPEED
            if not worldMap[int(positionX)][int(positionY + directionY * MOVESPEED)]:
                positionY += directionY * MOVESPEED
            # dx, dy = animation_offset(weapon)
           
                
        if keys[K_DOWN]:
            if not worldMap[int(positionX - directionX * MOVESPEED)][int(positionY)]:
                positionX -= directionX * MOVESPEED
            if not worldMap[int(positionX)][int(positionY - directionY * MOVESPEED)]:
                positionY -= directionY * MOVESPEED
            # dx, dy = animation_offset(weapon)
            

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

        # Animation State update
        update_weapon_state(weapon, weapon_state, dt)
            
        # Draws roof and floor
        screen.fill((25,25,25))
        pygame.draw.rect(screen, (50,50,50), (0, HEIGHT/2, WIDTH, HEIGHT/2)) 
                
        # Starts drawing level from 0 to < WIDTH 
        rays_for_minimap = [] 
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
                sideDistanceY = (mapY + 1.0 - rayPositionY) * deltaDistanceY

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
            column += 2
            rays_for_minimap.append( (perpWallDistance, (rayDirectionX, rayDirectionY)) )
        draw_minimap(screen, worldMap, positionX, positionY, directionX, directionY, rays_for_minimap)
        dx, dy, flash_on, p = animation_offset(weapon, weapon_state)  # <- state 전달
        rect = draw_weapon(screen, weapon_assets, weapon, (dx, dy))

        # 플래시 그리기
        if weapon == "gun" and flash_on:
            draw_muzzle_flash(screen, rect)

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