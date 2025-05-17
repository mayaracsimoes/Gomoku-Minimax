import pygame
import sys
import os

# Constantes de interface
CELL_SIZE = 40
MARGIN = 50


def load_image(path, size=None):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size) if size else img
    return None


class GomokuGUI:
    def __init__(self, game):
        pygame.init()
        self.game = game
        self.screen_width = game.board_size * CELL_SIZE + 2 * MARGIN
        self.screen_height = self.screen_width + 50
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Gomoku com IA")
        self.clock = pygame.time.Clock()
        self.current_screen = "menu"
        self.settings = {
            'depth': game.search_depth,
            'time': game.time_limit
        }
        # Fontes
        try:
            self.font = pygame.font.Font("assets/fonts/IrishGrover-Regular.ttf", 24)
            self.title_font = pygame.font.Font("assets/fonts/IrishGrover-Regular.ttf", 50)
        except:
            self.font = pygame.font.SysFont('Arial', 24)
            self.title_font = pygame.font.SysFont('Arial', 36, bold=True)

        # Cores
        self.colors = {
            'wood': (210, 180, 140),
            'dark_wood': (139, 69, 19),
            'black_stone': (45, 45, 45),
            'white_stone': (240, 240, 240),
            'highlight': (255, 215, 0),
            'text': (50, 50, 50),
            'button': (34, 139, 34),
            'button_hover': (50, 205, 50),
            'red': (200, 50, 50),
            'light_gray': (230, 230, 230),
            'white': (255, 255, 255),
            'green': (9, 92, 39)
        }

        # Imagens
        self.background_menu = load_image("assets/images/menu_background.png", (self.screen_width, self.screen_height))
        self.background_board = load_image("assets/images/board_background.png", (self.screen_width, self.screen_height))

    def draw_menu(self):
        if self.background_menu:
            self.screen.blit(self.background_menu, (0, 0))
        else:
            self.screen.fill(self.colors['wood'])

        # Título
        title = self.title_font.render("GOMOKU", True, self.colors['wood'])
        title_x = self.screen_width // 2 - title.get_width() // 2
        title_y = 100
        self.screen.blit(title, (title_x, title_y))

        # Botões centralizados
        button_width, button_height = 240, 50
        spacing = 20
        num_buttons = 2
        total_height = num_buttons * button_height + (num_buttons - 1) * spacing

        start_y = self.screen_height // 2 - total_height // 2 + 30  # +30 para empurrar um pouco para baixo

        play_button = self.draw_rounded_button("JOGAR",
                                               self.screen_width // 2 - button_width // 2,
                                               start_y,
                                               button_width,
                                               button_height)

        settings_button = self.draw_rounded_button("CONFIGURAÇÕES",
                                                   self.screen_width // 2 - button_width // 2,
                                                   start_y + button_height + spacing,
                                                   button_width,
                                                   button_height)

        pygame.display.flip()
        return play_button, settings_button

    def draw_board(self):
        if self.background_board:
            self.screen.blit(self.background_board, (0, 0))
        else:
            self.screen.fill(self.colors['wood'])

        # Grade
        for i in range(self.game.board_size):
            for j in range(self.game.board_size):
                pygame.draw.line(self.screen, self.colors['dark_wood'],
                                 (MARGIN + j * CELL_SIZE, MARGIN),
                                 (MARGIN + j * CELL_SIZE, MARGIN + (self.game.board_size - 1) * CELL_SIZE), 2)
                pygame.draw.line(self.screen, self.colors['dark_wood'],
                                 (MARGIN, MARGIN + i * CELL_SIZE),
                                 (MARGIN + (self.game.board_size - 1) * CELL_SIZE, MARGIN + i * CELL_SIZE), 2)

        # Estrelas
        star_points = [3, 7, 11]
        for i in star_points:
            for j in star_points:
                pygame.draw.circle(self.screen, self.colors['dark_wood'],
                                   (MARGIN + i * CELL_SIZE, MARGIN + j * CELL_SIZE), 5)

        # Pedras
        for i in range(self.game.board_size):
            for j in range(self.game.board_size):
                if self.game.board[i, j] == self.game.human_player:
                    self.draw_stone(i, j, self.colors['black_stone'])
                elif self.game.board[i, j] == self.game.ai_player:
                    self.draw_stone(i, j, self.colors['white'])

        # Mensagem
        msg = self.font.render(self.game.message, True, self.colors['text'])
        self.screen.blit(msg, (20, self.screen_height - 40))

        # Botão voltar
        back_button = self.draw_rounded_button("Voltar", 4, 5, 120, 40)
        pygame.display.flip()
        return back_button

    def draw_stone(self, row, col, color):
        x = MARGIN + col * CELL_SIZE
        y = MARGIN + row * CELL_SIZE
        pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 2 - 4)

    def draw_rounded_button(self, text, x, y, width, height):
        button_rect = pygame.Rect(x, y, width, height)
        color = self.colors['dark_wood']

        pygame.draw.rect(self.screen, color, button_rect, border_radius=20)
        pygame.draw.rect(self.screen, self.colors['dark_wood'], button_rect, 2, border_radius=20)

        text_surf = self.font.render(text, True, self.colors['white'])
        self.screen.blit(text_surf, (
            x + width // 2 - text_surf.get_width() // 2,
            y + height // 2 - text_surf.get_height() // 2
        ))

        return button_rect

    def draw_settings(self):
        """Desenha a tela de configurações"""
        self.screen.fill(self.colors['wood'])

        # Título
        title = self.title_font.render("Configurações", True, self.colors['black_stone'])
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 30))

        # Configuração de profundidade
        depth_text = self.font.render(f"Profundidade: {self.settings['depth']}", True, self.colors['black_stone'])
        self.screen.blit(depth_text, (50, 100))

        # Botões de profundidade
        depth_down = pygame.Rect(250, 100, 30, 30)
        pygame.draw.rect(self.screen, self.colors['red'], depth_down)
        self.screen.blit(self.font.render("-", True, self.colors['white']), (depth_down.x + 10, depth_down.y))

        depth_up = pygame.Rect(300, 100, 30, 30)
        pygame.draw.rect(self.screen, self.colors['green'], depth_up)
        self.screen.blit(self.font.render("+", True, self.colors['white']), (depth_up.x + 10, depth_up.y))

        # Configuração de tempo
        time_text = self.font.render(f"Tempo (seg): {self.settings['time']}", True, self.colors['black_stone'])
        self.screen.blit(time_text, (50, 150))

        # Botões de tempo
        time_down = pygame.Rect(250, 150, 30, 30)
        pygame.draw.rect(self.screen, self.colors['red'], time_down)
        self.screen.blit(self.font.render("-", True, self.colors['white']), (time_down.x + 10, time_down.y))

        time_up = pygame.Rect(300, 150, 30, 30)
        pygame.draw.rect(self.screen, self.colors['green'], time_up)
        self.screen.blit(self.font.render("+", True, self.colors['white']), (time_up.x + 10, time_up.y))

        # Botão Voltar
        back_button = pygame.Rect(
            self.screen_width // 2 - 100,
            220,
            200,
            50
        )
        pygame.draw.rect(self.screen, self.colors['dark_wood'], back_button)
        back_text = self.font.render("Voltar", True, self.colors['white'])
        self.screen.blit(back_text, (
            back_button.x + 100 - back_text.get_width() // 2,
            back_button.y + 25 - back_text.get_height() // 2
        ))

        pygame.display.flip()

        return depth_down, depth_up, time_down, time_up, back_button

    def draw_menu_button(self, text, x, y, width, height, color, hover_color):
        """Desenha um botão estilizado, com efeito, e hover"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, width, height)

        # Verifica hover
        current_color = hover_color if button_rect.collidepoint(mouse_pos) else color

        # Desenha o botão
        pygame.draw.rect(self.screen, current_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['dark_wood'], button_rect, 2, border_radius=10)

        # Texto do botão
        text_surf = self.font.render(text, True, self.colors['white'])
        self.screen.blit(text_surf, (
            x + width // 2 - text_surf.get_width() // 2,
            y + height // 2 - text_surf.get_height() // 2
        ))

        return button_rect

    def handle_menu_events(self):
        """Processa eventos do menu principal"""
        play_button, settings_button = self.draw_menu()

        while self.current_screen == "menu":
            self.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if play_button.collidepoint(mouse_pos):
                        self.current_screen = "game"
                        return

                    if settings_button.collidepoint(mouse_pos):
                        self.current_screen = "settings"
                        self.handle_settings_events()

            self.clock.tick(30)

    def handle_settings_events(self):
        """Processa eventos da tela de configurações"""
        while self.current_screen == "settings":
            depth_down, depth_up, time_down, time_up, back_button = self.draw_settings()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if depth_down.collidepoint(mouse_pos) and self.settings['depth'] > 1:
                        self.settings['depth'] -= 1
                    elif depth_up.collidepoint(mouse_pos) and self.settings['depth'] < 10:
                        self.settings['depth'] += 1
                    elif time_down.collidepoint(mouse_pos) and self.settings['time'] > 1:
                        self.settings['time'] -= 1
                    elif time_up.collidepoint(mouse_pos) and self.settings['time'] < 30:
                        self.settings['time'] += 1
                    elif back_button.collidepoint(mouse_pos):
                        # Aplica as configurações e sai completamente do loop
                        self.game.set_difficulty(
                            search_depth=self.settings['depth'],
                            time_limit=self.settings['time']
                        )
                        self.current_screen = "menu"
                        self.draw_menu()  # Redesenha o menu imediatamente
                        return  # Sai da função completamente

            self.clock.tick(30)

    def handle_game_events(self):
        """Processa eventos durante o jogo"""
        back_button = self.draw_board()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if back_button.collidepoint(mouse_pos):
                    self.game.reset_game()
                    self.current_screen = "menu"
                    self.draw_menu()  # Redesenha o menu imediatamente
                    return  # Sai da função completamente

                # Lógica original do jogo
                if not self.game.game_over and self.game.current_player == self.game.human_player:
                    x, y = pygame.mouse.get_pos()
                    col = (x - MARGIN) // CELL_SIZE
                    row = (y - MARGIN) // CELL_SIZE

                    if 0 <= row < self.game.board_size and 0 <= col < self.game.board_size:
                        if self.game.make_move(row, col, self.game.human_player):
                            if not self.game.game_over:
                                self.game.current_player = self.game.ai_player
                                self.game.message = "IA pensando..."
                                self.draw_board()
                                pygame.time.delay(300)
                                self.game.ai_move()
                                self.game.current_player = self.game.human_player
                            else:
                                self.game.message = "Você venceu! Clique para reiniciar."
                elif self.game.game_over:
                    self.game.reset_game()

                    return

    def run(self):
        """‘Loop’ principal do jogo"""
        self.handle_menu_events()  # Mostra o menu primeiro

        while True:
            if self.current_screen == "game":
                self.handle_game_events()
            elif self.current_screen == "menu":
                self.handle_menu_events()
            elif self.current_screen == "settings":
                self.handle_settings_events()

            self.clock.tick(30)
