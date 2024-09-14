import pytest
from unittest.mock import patch, MagicMock, Mock
import pygame
from main_pattern import Game, Target, get_random_color


def test_get_random_color():
    with patch('random.randint', return_value=100):
        color = get_random_color()
        assert color == (100, 100, 100)


class TestTarget:
    @patch('main_pattern.pygame.image.load')
    def test_initialization(self, mock_load):
        mock_image = MagicMock()
        mock_rect = MagicMock()
        mock_load.return_value = mock_image
        mock_image.get_rect.return_value = mock_rect
        mock_rect.width = 50
        mock_rect.height = 50

        target = Target()
        mock_load.assert_called_once_with("Images/target3.png")
        assert target.rect == mock_rect

    @patch('main_pattern.pygame.image.load')
    @patch('main_pattern.pygame.time.get_ticks', return_value=1000)
    def test_update(self, mock_ticks, mock_load):
        mock_image = MagicMock()
        mock_rect = MagicMock()
        mock_load.return_value = mock_image
        mock_image.get_rect.return_value = mock_rect
        mock_rect.x = 100
        mock_rect.y= 100
        mock_rect.width = 50
        mock_rect.height = 50

        target = Target()
        target.speed_x = 5
        target.speed_y = 5

        with patch('main_pattern.pygame.time.get_ticks', return_value=3000):
            target.update()

        assert target.rect.x == 105
        assert target.rect.y == 105

        target.rect.x = -1
        target.update()
        assert target.speed_x == -5

        target.rect.y = -1
        target.update()
        assert target.speed_y == -5


class TestGame:
    @patch('main_pattern.pygame.image.load')
    @patch('main_pattern.pygame.display.set_mode')
    def test_initialization(self, mock_set_mode, mock_load_image):
        mock_surface = Mock()
        mock_load_image.return_value = mock_surface

        game = Game()

        assert isinstance(game, Game)
        assert game.is_game_active is False
        assert game.is_paused is False
        assert game.total_clicks == 0
        assert game.total_hits == 0

    def test_singleton(self):
        game1 = Game()
        game2 = Game()
        assert game1 is game2


    @patch('main_pattern.pygame.Rect.collidepoint', return_value=True)
    def test_handle_event(self, mock_collidepoint):
        game = Game()
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.pos = (100, 100)

        assert game.handle_event(event) is True
        assert game.total_clicks == 1

        event.type = pygame.QUIT
        assert game.handle_event(event) is False


if __name__ == "__main__":
    pytest.main()