# ponto de entrada do programa: instancia a aplicação e inicia o loop do jogo.
from jogo.aplicacao import Aplicacao


# garante que o jogo só rode quando este arquivo for executado diretamente.
if __name__ == "__main__":
    Aplicacao().executar()