from functools import lru_cache
from random import Random

import pygame

from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA


CELULA = TAMANHO_CELULA // 2
PEDRAS = ((45, 51, 56), (48, 55, 59), (51, 57, 61), (53, 59, 63), (50, 55, 62))


def _laje(arte, x, y, cor, sorte):
    pygame.draw.rect(arte, (27, 32, 38), (x, y, CELULA, CELULA))
    pygame.draw.polygon(arte, cor, (
        (x + 2, y), (x + 15, y), (x + 19, y + 3), (x + 19, y + 16),
        (x + 16, y + 18), (x + 3, y + 18), (x, y + 15), (x, y + 3),
    ))
    pygame.draw.line(arte, (68, 73, 73), (x + 3, y), (x + 15, y))
    pygame.draw.line(arte, (36, 42, 48), (x + 3, y + 17), (x + 16, y + 17))
    for _ in range(4):
        px, py = x + sorte.randrange(3, 16), y + sorte.randrange(3, 16)
        pygame.draw.line(arte, (60, 65, 68), (px, py), (px + 1, py))
    if sorte.randrange(4) == 0:
        pygame.draw.lines(arte, (35, 41, 46), False, (
            (x + 10, y), (x + 9, y + 3), (x + 12, y + 6), (x + 11, y + 10),
        ))


def _parede(arte, x, y, sorte):
    pygame.draw.rect(arte, (19, 23, 29), (x, y, CELULA, CELULA))
    for dy, altura in ((1, 6), (8, 6), (15, 3)):
        junta = sorte.randrange(6, 15)
        for dx, largura in ((0, junta), (junta + 1, CELULA - junta - 1)):
            cor = sorte.choice(((65, 69, 71), (73, 75, 77), (79, 80, 79)))
            pygame.draw.rect(arte, cor, (x + dx, y + dy, largura, altura))
            pygame.draw.line(arte, (99, 99, 94), (x + dx, y + dy),
                             (x + dx + largura - 1, y + dy))


def _anel(arte, centro):
    cx, cy = centro
    octogono = ((-41, -101), (41, -101), (101, -41), (101, 41), (41, 101),
                (-41, 101), (-101, 41), (-101, -41))
    for escala, cor in ((1.04, (28, 32, 37)), (1, (109, 81, 64)), (0.99, (74, 62, 56)),
                        (0.93, (33, 37, 42)), (0.9, (67, 67, 63))):
        pontos = [(cx + round(x * escala), cy + round(y * escala)) for x, y in octogono]
        pygame.draw.lines(arte, cor, True, pontos, 2)
    # O mosaico e os encaixes de cobre são gravados no piso.
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        for passo in (13, 23, 34, 53, 79, 99):
            x, y = cx + dx * passo, cy + dy * passo
            cor = (161, 100, 60) if passo in (79, 99) else (88, 70, 59)
            pygame.draw.polygon(arte, cor, ((x, y - 3), (x + 3, y), (x, y + 3), (x - 3, y)), 1)
    for raio, cor in ((32, (34, 38, 42)), (26, (80, 67, 59))):
        pygame.draw.polygon(arte, cor, ((cx, cy - raio), (cx + raio, cy),
                                      (cx, cy + raio), (cx - raio, cy)), 1)


def _braseiro(arte, x, y, quadro):
    pygame.draw.ellipse(arte, (27, 25, 27), (x - 8, y - 2, 16, 6))
    pygame.draw.polygon(arte, (74, 58, 50),
                        ((x - 8, y - 4), (x + 8, y - 4), (x + 5, y + 2), (x - 5, y + 2)))
    pygame.draw.line(arte, (184, 128, 76), (x - 7, y - 4), (x + 7, y - 4))
    ponta = y - 12 - quadro % 3
    pygame.draw.polygon(arte, (213, 77, 35),
                        ((x - 5, y - 5), (x - 4, y - 10), (x - 1, y - 8),
                         (x + 1, ponta), (x + 5, y - 8), (x + 4, y - 5)))
    pygame.draw.polygon(arte, (255, 188, 82),
                        ((x - 3, y - 5), (x + 1, ponta + 4), (x + 3, y - 5)))
    pygame.draw.line(arte, (255, 230, 157), (x, y - 5), (x + 1, y - 7))
    arte.set_at((x + 5 - quadro, ponta - quadro % 2 - 1), (221, 128, 53))


@lru_cache(maxsize=1)
def _criar_covil():
    sorte = Random(53)
    tamanho = TAMANHO_MAPA * CELULA
    arte = pygame.Surface((tamanho, tamanho), depth=24)
    ultima = TAMANHO_MAPA - 1
    for linha in range(TAMANHO_MAPA):
        for coluna in range(TAMANHO_MAPA):
            x, y = coluna * CELULA, linha * CELULA
            if linha in (0, ultima) or coluna in (0, ultima):
                _parede(arte, x, y, sorte)
            else:
                _laje(arte, x, y, sorte.choice(PEDRAS), sorte)

    _anel(arte, (tamanho // 2, tamanho // 2))
    braseiros = ((90, 16), (250, 16), (90, tamanho - 4), (250, tamanho - 4),
                 (10, 110), (10, 230), (tamanho - 10, 110), (tamanho - 10, 230))
    luz = pygame.Surface(arte.get_size(), pygame.SRCALPHA)
    for x, y in braseiros:
        for raio in range(47, 2, -3):
            alpha = round(85 * (1 - raio / 50) ** 2)
            pygame.draw.circle(luz, (229, 105, 45, alpha), (x, y - 5), raio)
    arte.blit(luz, (0, 0))

    quadros = []
    for quadro in range(4):
        imagem = arte.copy()
        for indice, (x, y) in enumerate(braseiros):
            _braseiro(imagem, x, y, (quadro + indice) % 4)
        quadros.append(pygame.transform.scale(imagem, (tamanho * 2, tamanho * 2)))
    return quadros


def desenhar_covil(tela):
    quadros = _criar_covil()
    tela.blit(quadros[pygame.time.get_ticks() // 135 % len(quadros)], (0, 0))
