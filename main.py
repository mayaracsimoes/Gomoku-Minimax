from gomoku import GomokuGame
from gui import GomokuGUI

def main():
    # Cria o jogo com configurações padrão
    gomoku_game = GomokuGame()

    # Cria a interface com o jogo
    gomoku_gui = GomokuGUI(gomoku_game)

    # Inicia o jogo
    gomoku_gui.run()


if __name__ == "__main__":
    main()