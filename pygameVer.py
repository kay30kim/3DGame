import pygame
pygame.init()

screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

x, y = 300, 200
speed = 5

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        y -= speed
    if keys[pygame.K_s]:
        y += speed
    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 200, 255), (x, y, 50, 50))
    pygame.display.flip()

pygame.quit()