import pygame
pygame.init()
screen = pygame.display.set_mode((640, 480))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 0, 0), (100, 100, 50, 50))
    pygame.display.flip()
pygame.quit()
