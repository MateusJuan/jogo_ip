import pygame

from jogo.blocos import IMAGENS, SOLIDOS, BURACOS
from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA


def pode_andar(mundo, x, y):
    if x < 0 or y < 0 or x >= TAMANHO_MAPA or y >= TAMANHO_MAPA:
        return False
    if (x, y) in mundo.escadas:
        return True
    return mundo.grade[y][x] not in SOLIDOS


def desenhar_mapa(tela, mundo, imagens):
    for y, linha in enumerate(mundo.grade):
        for x, bloco in enumerate(linha):
            tela.blit(imagens[IMAGENS[bloco]], (x * TAMANHO_CELULA, y * TAMANHO_CELULA))

    for (x, y), escada in mundo.escadas.items():
        _desenhar_escada(tela, x, y, escada["sobe"])


def _desenhar_escada(tela, x, y, sobe):
    px = x * TAMANHO_CELULA
    py = y * TAMANHO_CELULA
    base = (98, 90, 76) if sobe else (62, 56, 48)
    degrau = (146, 136, 116) if sobe else (44, 40, 36)
    pygame.draw.rect(tela, base, (px, py, TAMANHO_CELULA, TAMANHO_CELULA))
    for indice in range(4):
        pygame.draw.rect(tela, degrau, (px + 5, py + 4 + indice * 9, TAMANHO_CELULA - 10, 5))
    if sobe:
        ponta = [(px + 20, py + 6), (px + 14, py + 14), (px + 26, py + 14)]
        pygame.draw.polygon(tela, (196, 184, 156), ponta)
    else:
        ponta = [(px + 20, py + 34), (px + 14, py + 26), (px + 26, py + 26)]
        pygame.draw.polygon(tela, (28, 24, 20), ponta)

def identificando_buraco(mundo, x, y):
    if x < 0 or y < 0 or x >= TAMANHO_MAPA or y >= TAMANHO_MAPA:
        return False
    return mundo.grade[y][x] in BURACOS
