# ponto de entrada do programa: importa e inicia o loop principal do jogo.
from jogo.aplicacao import executar_aplicacao


# garante que o jogo só rode quando este arquivo for executado diretamente.
if __name__ == "__main__":
    executar_aplicacao()