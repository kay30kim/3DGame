# packages
import pygame
import sys
import math

# global constants
SCREEN_HEIGHT = 480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 8
TILE_SIZE = int((SCREEN_WIDTH / 2) / MAP_SIZE)
MAX_DEPTH = int(MAP_SIZE * TILE_SIZE)
FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 120
STEP_ANGLE = FOV / CASTED_RAYS

# global variables
player_x = (SCREEN_WIDTH / 2) / 2
player_y = (SCREEN_WIDTH / 2) / 2
player_angle = math.pi

# map
MAP = (
    '########'
    '# #    #'
    '# #  ###'
    '#      #'
    '#      #'
    '#  ##  #'
    '#   #  #'
    '########'
)

# init pygame
pygame.init()

# create game window
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# set window title
pygame.display.set_caption('Raycasting')

# init timer
clock = pygame.time.Clock()

# draw map
def draw_map():
    # loop over map rows
    for row in range(8):
        # loop over map columns
        for col in range(8):
            # calculate square index
            square = row * MAP_SIZE + col
            
            # draw map in the game window
            pygame.draw.rect(
                win,
                (200, 200, 200) if MAP[square] == '#' else (100, 100, 100),
                (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2)
            )

    # draw player on 2D board
    pygame.draw.circle(win, (255, 0, 0), (int(player_x), int(player_y)), 8)
    
    # draw player direction
    pygame.draw.line(win, (0, 255, 0), (player_x, player_y),
                                       (player_x - math.sin(player_angle) * 50,
                                        player_y + math.cos(player_angle) * 50), 3)
    
    # draw player FOV
    pygame.draw.line(win, (0, 255, 0), (player_x, player_y),
                                       (player_x - math.sin(player_angle - HALF_FOV) * 50,
                                        player_y + math.cos(player_angle - HALF_FOV) * 50), 3)
    
    pygame.draw.line(win, (0, 255, 0), (player_x, player_y),
                                       (player_x - math.sin(player_angle + HALF_FOV) * 50,
                                        player_y + math.cos(player_angle + HALF_FOV) * 50), 3)

# raycasting algorithm
def cast_rays():
    # define left most angle of FOV
    start_angle = player_angle - HALF_FOV
    
    # loop over casted rays
    for ray in range(CASTED_RAYS):
        # cast ray step by step
        for depth in range(MAX_DEPTH):
            # get ray target coordinates
            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y + math.cos(start_angle) * depth
            
            # covert target X, Y coordinate to map col, row
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)
            
            # calculate map square index
            square = row * MAP_SIZE + col

            # ray hits the condition
            if MAP[square] == '#':
                # highlight wall that has been hit by a casted ray
                pygame.draw.rect(win, (0, 255, 0), (col * TILE_SIZE,
                                                    row * TILE_SIZE,
                                                    TILE_SIZE - 2,
                                                    TILE_SIZE - 2))

                # draw casted ray
                pygame.draw.line(win, (255, 255, 0), (player_x, player_y), (target_x, target_y))
                break

        # increment angle by a single step
        start_angle += STEP_ANGLE

# game loop
while True:
    # escape condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
    
    # update background
    pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
    
    # draw 2D map
    draw_map()
    
    # apply raycasting
    cast_rays()
    
    # get user input
    keys = pygame.key.get_pressed()
    
    # handle user input
    if keys[pygame.K_LEFT]: player_angle -= 0.1
    if keys[pygame.K_RIGHT]: player_angle += 0.1
    if keys[pygame.K_UP]:
        player_x += -math.sin(player_angle) * 5
        player_y += math.cos(player_angle) * 5
    if keys[pygame.K_DOWN]:
        player_x -= -math.sin(player_angle) * 5
        player_y -= math.cos(player_angle) * 5

    # update display
    pygame.display.flip()
    
    # set FPS
    clock.tick(30)
    
# map change - screen vs window
# number of ray change
# brick color change
# location of player change
# how do we know the ray reached to the wall (index of tile)