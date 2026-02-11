import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Image Display")

# Load image
img = pygame.image.load("50px-Machine_Gun_Stratagem_Icon.png").convert_alpha()

# Scale to specific width/height
scaled_img = pygame.transform.scale_by(img, 1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    screen.blit(scaled_img, (0, 0))  # draw scaled image
    pygame.display.flip()

pygame.quit()