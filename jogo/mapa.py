import pygame

from jogo.blocos import BURACOS, IMAGENS, SOLIDOS
from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA


def pode_andar(mundo, x, y):
    # verifica se a célula (x, y) está dentro do mapa e não é um obstáculo sólido.
    # impede sair dos limites da matriz 17x17.
    if x < 0 or y < 0 or x >= TAMANHO_MAPA or y >= TAMANHO_MAPA:
        return False
    # escadas ficam na borda (onde normalmente há parede), mas permitem passagem.
    if (x, y) in mundo.escadas:
        return True
    # na matriz usamos [y][x], pois 'y' representa a linha e 'x' a coluna.
    return mundo.grade[y][x] not in SOLIDOS


def desenhar_mapa(tela, mundo, imagens):
    # percorre a matriz do andar atual e desenha cada bloco e escada na tela.
    for y, linha in enumerate(mundo.grade):
        for x, bloco in enumerate(linha):
            nome_imagem = IMAGENS[bloco]
            tela.blit(imagens[nome_imagem], (x * TAMANHO_CELULA, y * TAMANHO_CELULA))

    # desenha as escadas por cima do piso nas posições cadastradas no mundo.
    for (x, y), escada in mundo.escadas.items():
        _desenhar_escada(tela, x, y, escada["sobe"])


def _desenhar_escada(tela, x, y, sobe):
    # desenha visualmente os degraus da escada e uma seta indicando se sobe ou desce.
    px = x * TAMANHO_CELULA
    py = y * TAMANHO_CELULA

    # tons mais claros para escada que sobe; tons mais escuros para escada que desce.
    base = (98, 90, 76) if sobe else (62, 56, 48)
    degrau = (146, 136, 116) if sobe else (44, 40, 36)

    pygame.draw.rect(tela, base, (px, py, TAMANHO_CELULA, TAMANHO_CELULA))
    for indice in range(4):
        pygame.draw.rect(tela, degrau, (px + 5, py + 4 + indice * 9, TAMANHO_CELULA - 10, 5))

    # desenha um triângulo apontando para cima (sobe) ou para baixo (desce).
    if sobe:
        ponta = [(px + 20, py + 6), (px + 14, py + 14), (px + 26, py + 14)]
        pygame.draw.polygon(tela, (196, 184, 156), ponta)
    else:
        ponta = [(px + 20, py + 34), (px + 14, py + 26), (px + 26, py + 26)]
        pygame.draw.polygon(tela, (28, 24, 20), ponta)


def identificando_buraco(mundo, x, y):
    # retorna true se a célula (x, y) for um buraco no chão.
    if x < 0 or y < 0 or x >= TAMANHO_MAPA or y >= TAMANHO_MAPA:
        return False
    return mundo.grade[y][x] in BURACOS