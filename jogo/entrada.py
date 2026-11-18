from functools import lru_cache
from random import Random

import pygame

from jogo.blocos import GALERIA_BURACO, GALERIA_PAREDE
from jogo.configuracoes import TAMANHO_CELULA


ESCALA = 2
CELULA = TAMANHO_CELULA // ESCALA
PEDRAS = ((67, 76, 71), (73, 81, 73), (79, 84, 73), (63, 72, 68))


def _laje(tela, x, y, largura, altura, sorte):
    cor = sorte.choice(PEDRAS)
    pygame.draw.rect(tela, (22, 33, 33), (x, y, largura, altura))
    pygame.draw.rect(tela, cor, (x + 1, y + 1, largura - 2, altura - 2))
    pygame.draw.line(tela, (96, 104, 87), (x + 1, y + 1), (x + largura - 3, y + 1))
    for _ in range(largura // 3):
        px = sorte.randrange(x + 2, x + largura - 2)
        py = sorte.randrange(y + 2, y + altura - 1)
        escolha = sorte.choice(((53, 62, 56), (95, 101, 83), (80, 94, 63)))
        pygame.draw.line(tela, escolha, (px, py), (px + 1, py))
    if sorte.random() < 0.35:
        meio = x + largura // 2
        pygame.draw.lines(tela, (39, 48, 44), False,
                          ((meio, y + 1), (meio - 2, y + 4), (meio + 1, y + 6)))


def _pilar(tela, x, y, sorte, quebrado=False):
    pygame.draw.ellipse(tela, (7, 15, 20), (x - 13, y + 1, 36, 14))
    _laje(tela, x - 10, y, 20, 7, sorte)
    _laje(tela, x - 7, y - 12, 14, 14, sorte)
    if quebrado:
        pygame.draw.polygon(tela, (127, 131, 103),
                            ((x - 7, y - 12), (x - 4, y - 17), (x + 1, y - 13),
                             (x + 4, y - 16), (x + 7, y - 11)))
    else:
        _laje(tela, x - 9, y - 20, 18, 10, sorte)


def _luzes(tela, pontos):
    brilho = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
    for x, y in pontos:
        for raio in range(30, 1, -1):
            alpha = round(88 * (1 - raio / 31) ** 2)
            pygame.draw.circle(brilho, (243, 137, 55, alpha), (x, y - 4), raio)
    tela.blit(brilho, (0, 0))


def _arco_desmoronado(tela, centro, base, sorte):
    for lado in (-1, 1):
        x = centro + lado * 39
        _pilar(tela, x, base - 12, sorte, quebrado=True)
        perfil = ((38, -15), (33, -9), (23, -5), (16, 0), (20, 3),
                  (13, 6), (25, 6), (39, 1), (46, -7))
        pygame.draw.polygon(tela, (33, 43, 40),
                            [(centro + lado * dx, base + dy + 3) for dx, dy in perfil])
        pygame.draw.polygon(tela, (92, 102, 85),
                            [(centro + lado * dx, base + dy) for dx, dy in perfil])
        for dx, dy, fim_x, fim_y in ((33, -9, 39, 1), (23, -5, 25, 6)):
            pygame.draw.line(tela, (43, 53, 48), (centro + lado * dx, base + dy),
                             (centro + lado * fim_x, base + fim_y))


def _chama(tela, x, y, alta):
    pygame.draw.rect(tela, (50, 34, 27), (x - 1, y - 4, 3, 8))
    pygame.draw.line(tela, (139, 99, 55), (x - 3, y), (x + 3, y))
    ponta = y - (12 if alta else 10)
    pygame.draw.polygon(tela, (220, 91, 37),
                        ((x - 4, y - 3), (x - 3, y - 8), (x, ponta),
                         (x + 1, y - 8), (x + 4, y - 5), (x + 2, y - 1)))
    pygame.draw.polygon(tela, (255, 192, 87),
                        ((x - 2, y - 3), (x, y - 9), (x + 2, y - 4), (x + 1, y - 2)))
    pygame.draw.line(tela, (255, 233, 151), (x, y - 5), (x, y - 3))
    pygame.draw.rect(tela, (211, 116, 54), (x + 2, ponta - 2, 1, 1))


@lru_cache(maxsize=2)
def _criar_entrada(grade):
    sorte = Random(83)
    largura = len(grade[0]) * CELULA
    altura = len(grade) * CELULA
    arte = pygame.Surface((largura, altura))
    arte.fill((13, 24, 29))
    for y in range(altura):
        c = round(5 * y / altura)
        pygame.draw.line(arte, (12 + c, 22 + c, 28 + c), (0, y), (largura, y))
    for _ in range(450):
        x, y = sorte.randrange(largura), sorte.randrange(altura)
        pygame.draw.line(arte, sorte.choice(((21, 34, 39), (13, 24, 30), (26, 39, 42))),
                         (x, y), (x + sorte.randrange(2, 12), y))

    # Cantaria de contenção abaixo da passarela e destroços no fundo do abismo.
    for coluna, linha in ((2, 3), (13, 5), (12, 10), (2, 12), (12, 13), (4, 14)):
        x, y = coluna * CELULA + 10, linha * CELULA + 10
        for _ in range(8):
            px, py = x + sorte.randrange(-13, 14), y + sorte.randrange(-8, 12)
            pygame.draw.polygon(arte, sorte.choice(((29, 42, 44), (39, 50, 49), (48, 58, 53))),
                                ((px - 3, py), (px, py - 3), (px + 5, py - 2),
                                 (px + 4, py + 2), (px - 2, py + 3)))
        _pilar(arte, x, y, sorte, quebrado=True)

    for linha, blocos in enumerate(grade):
        for coluna, bloco in enumerate(blocos):
            x, y = coluna * CELULA, linha * CELULA
            if bloco in (GALERIA_BURACO, GALERIA_PAREDE):
                continue
            if grade[linha + 1][coluna] == GALERIA_BURACO:
                pygame.draw.rect(arte, (9, 18, 23), (x, y + CELULA, CELULA + 3, 13))
                pygame.draw.rect(arte, (43, 53, 49), (x, y + CELULA, CELULA, 8))
                pygame.draw.line(arte, (27, 38, 39), (x + 8, y + CELULA), (x + 8, y + CELULA + 8))
            if grade[linha][coluna + 1] == GALERIA_BURACO:
                pygame.draw.rect(arte, (26, 39, 40), (x + CELULA, y + 2, 4, CELULA + 5))
            junta = sorte.randrange(7, 14)
            _laje(arte, x, y, CELULA, 10, sorte)
            _laje(arte, x, y + 10, junta, 10, sorte)
            _laje(arte, x + junta, y + 10, CELULA - junta, 10, sorte)

    for linha, blocos in enumerate(grade):
        for coluna, bloco in enumerate(blocos):
            if bloco != GALERIA_PAREDE:
                continue
            x, y = coluna * CELULA, linha * CELULA
            _laje(arte, x, y, CELULA, 12, sorte)
            _laje(arte, x, y + 12, CELULA, 8, sorte)
            if (linha + coluna) % 3 == 0:
                pygame.draw.rect(arte, (61, 79, 53), (x + 2, y + 10, 7, 3))
                pygame.draw.rect(arte, (51, 68, 49), (x + 4, y + 13, 3, 4))

    centro = largura // 2
    _arco_desmoronado(arte, centro, altura - 18, sorte)
    for x in (centro - 39, centro + 39):
        _pilar(arte, x, 27, sorte)
    for x, y in ((67, 218), (130, 166)):
        _laje(arte, x - 6, y + 1, 12, 7, sorte)
    pontos = ((centro - 36, altura - 39), (centro + 36, altura - 39),
              (67, 218), (130, 166), (centro - 39, 19), (centro + 39, 19))
    _luzes(arte, pontos)

    quadros = []
    for quadro in range(4):
        imagem = arte.copy()
        for indice, (x, y) in enumerate(pontos):
            _chama(imagem, x, y, (quadro + indice) % 4 in (0, 1))
        quadros.append(pygame.transform.scale(imagem, (largura * ESCALA, altura * ESCALA)))
    return quadros


def desenhar_entrada(tela, grade):
    quadros = _criar_entrada(grade)
    tela.blit(quadros[pygame.time.get_ticks() // 125 % len(quadros)], (0, 0))
