# try:
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
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    close()
                    return
                # keys[event.key] = True
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
            rays_for_minimap.append( (perpWallDistance, (rayDirectionX, rayDirectionY)) )
            column += 2

        draw_minimap(screen, worldMap, positionX, positionY, directionX, directionY, rays_for_minimap)

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