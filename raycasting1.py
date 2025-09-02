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
    px = ox + int(posX * MINIMAP_SCALE)
    py = oy + int(posY * MINIMAP_SCALE)
    pygame.draw.circle(screen, COLOR_MINI_PLAYER, (px, py), 3)
    
    magd = math.hypot(dirX, dirY) or 1.0
    fx = px + int(dirY / magd * 8)
    fy = py + int(dirX / magd * 8)
    pygame.draw.line(screen, COLOR_MINI_PLAYER, (px, py), (fx, fy), 2)


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