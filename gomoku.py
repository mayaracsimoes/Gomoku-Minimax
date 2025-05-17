import time
import numpy as np

class GomokuGame:
    """Classe principal que gerencia o estado do jogo"""

    def __init__(self, board_size=15):
        """Inicializa o jogo com tabuleiro vazio"""
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.human_player = 1  # Jogador humano usa 1
        self.ai_player = 2  # IA usa 2
        self.current_player = self.human_player
        self.game_over = False
        self.winner = None
        self.message = "Sua vez de jogar"

        # Configurações da IA
        self.search_depth = 9  # Profundidade da busca
        self.time_limit = 5  # Tempo máximo de cálculo (segundos)

        # Área de busca otimizada
        self.search_area = set()
        self.update_search_area()

        # Padrões estratégicos com seus respectivos pesos
        self.patterns = self._create_pattern_weights()

    def _create_pattern_weights(self):
        """Define os pesos para cada padrão estratégico - Versão mais agressiva"""
        return {
            # Padrões ofensivos (IA) - Valores aumentados
            (self.ai_player, 5): 1000000,  # Vitória (valor aumentado)
            (self.ai_player, 4): 50000,  # Quase vitória (valor aumentado)
            (self.ai_player, 3): 3000,  # Sequência de 3 (valor aumentado)
            (self.ai_player, 2): 200,  # Sequência de 2 (valor aumentado)

            # Padrões defensivos (Jogador) - Valores mais negativos
            (self.human_player, 5): -1000000,
            (self.human_player, 4): -100000,
            (self.human_player, 3): -5000,
            (self.human_player, 2): -300,

            # Padrões abertos (mais valiosos)
            (self.ai_player, 4, 'open'): 100000,
            (self.ai_player, 3, 'open'): 5000,
            (self.human_player, 4, 'open'): -150000,
            (self.human_player, 3, 'open'): -10000,

            # Novos padrões adicionados
            (self.ai_player, 3, 'split'): 4000,  # Sequência com espaço no meio
            (self.human_player, 3, 'split'): -8000  # Penaliza sequências com espaço
        }

    def update_search_area(self):
        """Atualiza a área de busca para incluir apenas células próximas a peças existentes"""
        self.search_area = set()

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j] != 0:
                    for di in range(-2, 3):
                        for dj in range(-2, 3):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                                if self.board[ni, nj] == 0:
                                    self.search_area.add((ni, nj))

        # Se não houver peças no tabuleiro, começa pelo centro
        if not self.search_area and self.board[self.board_size // 2][self.board_size // 2] == 0:
            self.search_area.add((self.board_size // 2, self.board_size // 2))

    def make_move(self, row, col, player):
        """Faz uma jogada no tabuleiro"""
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False

        if self.board[row, col] != 0:
            return False

        self.board[row, col] = player
        self.update_search_area()

        if self.check_win(row, col):
            self.game_over = True
            self.winner = player
            return True

        return True

    def check_win(self, row, col):
        """Verifica se a última jogada resultou em vitória"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        player = self.board[row, col]

        for dr, dc in directions:
            count = 1

            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True

        return False

    def get_valid_moves(self):
        """Retorna todas as jogadas válidas na área de busca"""
        return list(self.search_area) if self.search_area else \
            [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.board[i, j] == 0]

    def evaluate_board(self):
        """Avalia o tabuleiro e retorna uma pontuação"""
        score = 0

        for i in range(self.board_size):
            score += self._evaluate_row(i)

        for j in range(self.board_size):
            score += self._evaluate_column(j)

        score += self._evaluate_diagonals()

        # Bônus adicional para o centro no início do jogo
        total_pieces = np.sum(self.board != 0)
        if total_pieces < 4:
            center = self.board_size // 2
            if self.board[center, center] == self.ai_player:
                score += 100  # Bônus maior para ocupar o centro
            elif self.board[center, center] == 0:
                score += 50  # Incentivo maior para ir para o centro

        ai_pieces = np.sum(self.board == self.ai_player)
        human_pieces = np.sum(self.board == self.human_player)

        if ai_pieces + human_pieces < 6:
            center = self.board_size // 2
            if self.board[center, center] == self.ai_player:
                score += 50
            elif self.board[center, center] == 0:
                score += 30

        return score

    def _evaluate_row(self, row):
        """Avalia uma linha específica do tabuleiro"""
        score = 0
        for j in range(self.board_size - 4):
            segment = list(self.board[row, j:j + 5])
            score += self._evaluate_segment(segment)
        return score

    def _evaluate_column(self, col):
        """Avalia uma coluna específica do tabuleiro"""
        score = 0
        for i in range(self.board_size - 4):
            segment = list(self.board[i:i + 5, col])
            score += self._evaluate_segment(segment)
        return score

    def _evaluate_diagonals(self):
        """Avalia todas as diagonais do tabuleiro"""
        score = 0

        for i in range(self.board_size - 4):
            for j in range(self.board_size - 4):
                segment = [self.board[i + k, j + k] for k in range(5)]
                score += self._evaluate_segment(segment)

        for i in range(self.board_size - 4):
            for j in range(4, self.board_size):
                segment = [self.board[i + k, j - k] for k in range(5)]
                score += self._evaluate_segment(segment)

        return score

    def _evaluate_segment(self, segment):
        """Avalia um segmento de 5 células"""
        score = 0

        if segment.count(self.ai_player) == 5:
            return self.patterns[(self.ai_player, 5)]
        elif segment.count(self.human_player) == 5:
            return self.patterns[(self.human_player, 5)]

        if segment.count(self.ai_player) == 4 and segment.count(0) == 1:
            return self.patterns.get((self.ai_player, 4, 'open'), self.patterns[(self.ai_player, 4)])
        elif segment.count(self.human_player) == 4 and segment.count(0) == 1:
            return self.patterns.get((self.human_player, 4, 'open'), self.patterns[(self.human_player, 4)])

        for player in [self.ai_player, self.human_player]:
            for size in [4, 3, 2]:
                if segment.count(player) == size and segment.count(0) == 5 - size:
                    score += self.patterns.get((player, size), 0)

        return score

    def minimax(self, depth, alpha, beta, maximizing_player, start_time):
        """Implementação do algoritmo Minimax com poda Alpha-Beta"""
        if time.time() - start_time > self.time_limit:
            return None

        if depth == 0 or self.game_over:
            return self.evaluate_board()

        valid_moves = self.get_valid_moves()

        if maximizing_player:
            max_eval = -float('inf')
            for (i, j) in valid_moves:
                self.board[i, j] = self.ai_player
                current_eval = self.minimax(depth - 1, alpha, beta, False, start_time)
                self.board[i, j] = 0

                if current_eval is None:
                    return None

                max_eval = max(max_eval, current_eval)
                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for (i, j) in valid_moves:
                self.board[i, j] = self.human_player
                current_eval = self.minimax(depth - 1, alpha, beta, True, start_time)
                self.board[i, j] = 0

                if current_eval is None:
                    return None

                min_eval = min(min_eval, current_eval)
                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self):
        """Encontra a melhor jogada para a IA com bloqueio agressivo"""
        start_time = time.time()
        best_move = None
        best_score = -float('inf')

        # 1. Prioridade máxima: Vitória imediata da IA
        for (i, j) in self.get_valid_moves():
            self.board[i, j] = self.ai_player
            if self.check_win(i, j):
                self.board[i, j] = 0
                return i, j
            self.board[i, j] = 0

        # 2. Prioridade alta: Bloquear vitória iminente do jogador (4 em linha)
        for (i, j) in self.get_valid_moves():
            self.board[i, j] = self.human_player
            if self.check_win(i, j):
                self.board[i, j] = 0
                return i, j
            self.board[i, j] = 0

        # 3. Prioridade média: Bloquear sequências de 3 do jogador
        for (i, j) in self.get_valid_moves():
            self.board[i, j] = self.human_player
            if self.count_consecutive(i, j) >= 3:  # Detecta 3 peças consecutivas
                self.board[i, j] = 0
                # Verifica se este bloqueio também cria uma ameaça para a IA
                self.board[i, j] = self.ai_player
                if self.count_consecutive(i, j) >= 3:
                    return i, j  # Bloqueia E cria ameaça
                self.board[i, j] = 0
                best_move = (i, j)  # Guarda o movimento de bloqueio
            else:
                self.board[i, j] = 0

        # 4. Se encontrou um movimento para bloquear 3 peças, retorna ele
        if best_move:
            return best_move

        # 5. Estratégia ofensiva usando Minimax
        for (i, j) in self.get_valid_moves():
            self.board[i, j] = self.ai_player
            score = self.minimax(self.search_depth - 1, -float('inf'), float('inf'), False, start_time)
            self.board[i, j] = 0

            if score is None:  # Tempo esgotado
                break

            if score > best_score:
                best_score = score
                best_move = (i, j)

            # Verifica o tempo para não exceder o limite
            if time.time() - start_time > self.time_limit / 2:
                break

        return best_move if best_move else self.get_valid_moves()[0]

    def ai_move(self):
        """Executa a jogada da IA e atualiza o estado do jogo"""
        move = self.find_best_move()

        if move:
            i, j = move
            self.make_move(i, j, self.ai_player)

        if not self.game_over:
            self.message = "Sua vez de jogar"
        else:
            self.message = "IA venceu! Clique para reiniciar."

    def reset_game(self):
        """Reinicia o jogo para o estado inicial"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = self.human_player
        self.game_over = False
        self.winner = None
        self.message = "Sua vez de jogar"
        self.update_search_area()

    def count_consecutive(self, row, col):
        """Conta o máximo de peças consecutivas que esta jogada criaria"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        max_count = 1
        player = self.board[row, col]

        for dr, dc in directions:
            count = 1
            # Verifica em uma direção
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
                count += 1
                r += dr
                c += dc
            # Verifica na direção oposta
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == player:
                count += 1
                r -= dr
                c -= dc

            if count > max_count:
                max_count = count

        return max_count

    def set_difficulty(self, search_depth=None, time_limit=None):
        """Configura a dificuldade da IA"""
        if search_depth is not None:
            self.search_depth = search_depth
        if time_limit is not None:
            self.time_limit = time_limit

    def get_difficulty(self):
        """Retorna as configurações atuais de dificuldade"""
        return {
            'search_depth': self.search_depth,
            'time_limit': self.time_limit
        }