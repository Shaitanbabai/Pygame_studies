import pygame
import sys
import random

pygame.init()

screen_width, screen_height = 800, 650
game_field_height = 550  # Высота игрового поля
screen = pygame.display.set_mode((screen_width, screen_height))

font = pygame.font.Font(None, 36)
white = (255, 255, 255)
black = (0, 0, 0)

target_image = pygame.image.load("Images/target3.png")
target_rect = target_image.get_rect()
icon_image = pygame.image.load("Images/icon.jpg")
pygame.display.set_icon(icon_image)


def get_random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def random_speed(min_speed, max_speed):
    return random.randint(min_speed, max_speed) * (
        1 if random.randint(0, 1) == 0 else -1
    )


def draw_button(button, text, color):
    pygame.draw.rect(screen, color, button)
    text_surf = font.render(text, True, white)
    text_rect = text_surf.get_rect(center=button.center)
    screen.blit(text_surf, text_rect)


is_game_active = False
is_paused = False
background_color = get_random_color()
target_speed = [random_speed(1, 3), random_speed(1, 3)]
target_rect.x = random.randint(0, screen_width - target_rect.width)
target_rect.y = random.randint(0, game_field_height - target_rect.height)
clock = pygame.time.Clock()
last_speed_change = pygame.time.get_ticks()
total_clicks = 0
total_hits = 0

# Размещаем кнопки ниже игрового поля симметрично по ширине экрана
button_y = game_field_height + 25  # Высота плюс небольшой отступ
start_button = pygame.Rect(50, button_y, 100, 50)
pause_button = pygame.Rect(350, button_y, 100, 50)
end_button = pygame.Rect(650, button_y, 100, 50)

running = True  # Основной цикл игры
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                is_game_active = True
                is_paused = False
            elif pause_button.collidepoint(event.pos):
                is_paused = not is_paused
            elif end_button.collidepoint(event.pos):
                running = False
            elif is_game_active and not is_paused:
                total_clicks += 1
                if target_rect.collidepoint(event.pos):
                    total_hits += 1
                    background_color = get_random_color()
                    target_rect.x = random.randint(0, screen_width - target_rect.width)
                    target_rect.y = random.randint(
                        0, game_field_height - target_rect.height
                    )

    if is_game_active and not is_paused:
        if current_time - last_speed_change > 2000:
            target_speed = [random_speed(2, 4), random_speed(2, 4)]
            last_speed_change = current_time
        target_rect = target_rect.move(target_speed)
        if target_rect.left < 0 or target_rect.right > screen_width:
            target_speed[0] = -target_speed[0]
        if target_rect.top < 0 or target_rect.bottom > game_field_height:
            target_speed[1] = -target_speed[1]

    screen.fill(background_color)
    if is_game_active and not is_paused:
        screen.blit(target_image, target_rect)

    draw_button(start_button, "Start", black)
    draw_button(pause_button, "Pause", black)
    draw_button(end_button, "End", black)

    accuracy = (total_hits / total_clicks * 100) if total_clicks > 0 else 0
    pygame.display.set_caption(f"Тир - Точность: {accuracy:.2f}%")
    pygame.display.flip()

pygame.quit()
sys.exit()
