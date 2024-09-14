import os

import pygame
import sys
import random
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация Pygame
pygame.init()

# Установка размеров экрана
screen_width, screen_height = 800, 650
game_field_height = 550  # Высота игрового поля
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Игра с мишенью")

# Установка шрифта и цветов
font = pygame.font.Font(None, 36)
white = (255, 255, 255)
black = (0, 0, 0)

# Загрузка изображений
def load_image(image_path):
    if os.path.exists(image_path):
        try:
            return pygame.image.load(image_path)
        except pygame.error as e:
            logger.error(f"Ошибка загрузки изображения {image_path}: {e}")
            sys.exit(1)
    else:
        logger.error(f"Файл изображения {image_path} не существует.")
        sys.exit(1)

target_image = load_image("Images/target3.png")
icon_image = load_image("Images/icon.jpg")
pygame.display.set_icon(icon_image)
logger.info("Изображения успешно загружены.")

def get_random_color():
    """Возвращает случайный цвет в формате RGB."""
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

class Target:
    def __init__(self):
        """Инициализирует мишень с изображением, позицией и скоростью."""
        self.image = target_image
        self.rect = self.image.get_rect()
        self.reset_position()
        self.speed_x = random.uniform(-6, 6)
        self.speed_y = random.uniform(-6, 6)
        self.change_direction_time = pygame.time.get_ticks() + random.randint(2000, 4000)
        logger.info("Мишень создана с начальной позицией и скоростью.")

    def reset_position(self):
        """Сбрасывает позицию мишени на случайную позицию на экране."""
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(0, game_field_height - self.rect.height)
        logger.info("Позиция мишени сброшена.")

    def update(self):
        """Обновляет позицию мишени и проверяет на выход за границы."""
        try:
            # Обновление позиции мишени
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            # Проверка выхода за границы и изменение направления
            if self.rect.left <= 0 or self.rect.right >= screen_width:
                self.speed_x *= -1
                logger.debug("Изменение направления по оси X.")

            if self.rect.top <= 0 or self.rect.bottom >= game_field_height:
                self.speed_y *= -1
                logger.debug("Изменение направления по оси Y.")

            # Изменение направления через случайные интервалы времени
            current_time = pygame.time.get_ticks()
            if current_time >= self.change_direction_time:
                self.speed_x = random.uniform(-6, 6)
                self.speed_y = random.uniform(-6, 6)
                self.change_direction_time = current_time + random.randint(2000, 4000)
                logger.debug("Изменение направления через случайный интервал времени.")
        except Exception as error:
            logger.error(f"Ошибка обновления мишени: {error}")


class Game:
    """Класс для управления состоянием игры.

        Применяется паттерн Singleton для обеспечения единственного экземпляра игры.
        """
    _instance = None

    def __new__(cls):
        """
        Создает или возвращает существующий экземпляр класса Game.

        **Singleton** - паттерн используется в классе `Game`, чтобы гарантировать, что существует только один
        экземпляр игрового состояния. Это удобно для управления состоянием игры, так как нет необходимости беспокоиться
        о создании нескольких экземпляров, которые могут привести к несогласованному состоянию.

        **Initialization-on-demand holder idiom**: Используется в методе `__new__` класса `Game` для ленивой
        инициализации единственного экземпляра. Это облегчает управление ресурсами и обеспечивает потокобезопасность
        в многопоточном окружении.

        Магический метод `__new__` используется для контроля создания нового экземпляра класса.
        В контексте Singleton, этот метод переопределен, чтобы гарантировать создание только одного экземпляра `Game`.
        Этот подход экономит память и поддерживает целостность состояния игры, так как все изменения применяются
        к единственному экземпляру.

        """
        if cls._instance is None:
            cls._instance = super(Game, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Инициализирует состояние игры, если это ещё не было сделано.

        **Ленивая инициализация**: Применяется в методе `__init__` класса `Game`, чтобы убедиться, что инициализация
        выполняется только один раз после создания экземпляра. Это предотвращает повторную настройку
        атрибутов при каждом вызове конструктора, что важно для Singleton.

        """
        # Применение ленивой инициализации: инициализация происходит только один раз
        if not hasattr(self, 'initialized'):  # Проверка на повторную инициализацию
            self.initialized = True
            self.is_game_active = False
            self.is_paused = False
            self.background_color = (255, 255, 255)
            self.target = Target()
            self.clock = pygame.time.Clock()
            self.total_clicks = 0
            self.total_hits = 0

            # Размещение кнопок
            button_y = game_field_height + 25
            self.start_button = pygame.Rect(50, button_y, 100, 50)
            self.pause_button = pygame.Rect(350, button_y, 100, 50)
            self.end_button = pygame.Rect(650, button_y, 100, 50)
            logger.info("Игра успешно инициализирована.")

    def reset_game_state(self):
        """Сброс состояния игры до начальных значений."""
        self.is_game_active = False
        self.is_paused = False
        self.background_color = get_random_color()
        self.target.reset_position()
        self.total_clicks = 0
        self.total_hits = 0
        logger.info("Состояние игры сброшено до начальных значений.")

    def handle_event(self, event):
        """Обрабатывает входные события.

              Args:
                  event (pygame.event.Event): Событие, которое нужно обработать.

              Returns:
                  bool: False, если получено событие выхода из игры, иначе True.
              """
        if event.type == pygame.QUIT:
            logger.info("Получено событие выхода из игры.")
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.collidepoint(event.pos):
                self.is_game_active = True
                self.is_paused = False
                logger.info("Игра начата.")
            elif self.pause_button.collidepoint(event.pos):
                self.is_paused = not self.is_paused
                logger.info(f"Игра {'поставлена на паузу' if self.is_paused else 'возобновлена'}.")
            elif self.end_button.collidepoint(event.pos):
                self.reset_game_state()
                logger.info("Игра остановлена и состояние сброшено.")
            elif self.is_game_active and not self.is_paused:
                self.total_clicks += 1
                logger.info(f"Клик зарегистрирован. Всего кликов: {self.total_clicks}.")
                if self.target.rect.collidepoint(event.pos):
                    self.total_hits += 1
                    self.background_color = get_random_color()
                    self.target.reset_position()
                    self.target.speed_x = random.uniform(-6, 6)
                    self.target.speed_y = random.uniform(-6, 6)
                    self.target.change_direction_time = pygame.time.get_ticks() + random.randint(2000, 4000)
                    logger.info(f"Попадание! Всего попаданий: {self.total_hits}.")
        return True

    def update(self):
        """Обновляет состояние игры."""
        self.clock.tick(60)
        if self.is_game_active and not self.is_paused:
            self.target.update()  # Обновление состояния мишени

    def draw(self):
        """Отрисовывает все элементы игры на экране."""
        # Рисование фона
        screen.fill(self.background_color)

        # Рисование цели, если игра активна
        if self.is_game_active:
            screen.blit(self.target.image, self.target.rect)

        # Рисование кнопок
        pygame.draw.rect(screen, white, self.start_button)
        pygame.draw.rect(screen, white, self.pause_button)
        pygame.draw.rect(screen, white, self.end_button)

        # Отображение текста на кнопках
        start_text = font.render("Старт", True, black)
        pause_text = font.render("Пауза", True, black)
        end_text = font.render("Стоп", True, black)

        screen.blit(start_text, (self.start_button.x + 10, self.start_button.y + 10))
        screen.blit(pause_text, (self.pause_button.x + 10, self.pause_button.y + 10))
        screen.blit(end_text, (self.end_button.x + 10, self.end_button.y + 10))

        # Отображение статистики
        stats_text = font.render(f"Попадания: {self.total_hits} / Клики: {self.total_clicks}", True, black)
        screen.blit(stats_text, (10, screen_height - 30))

        pygame.display.flip()

def main():
    """Главная функция, запускающая игровой цикл."""
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if not game.handle_event(event):
                running = False

        game.update()
        game.draw()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()