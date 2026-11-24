from functools import lru_cache

import pygame

from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA


METAIS = {
    "prata": ((79, 92, 106), (155, 179, 194), (216, 236, 236)),
    "dourada": ((112, 68, 39), (199, 146, 64), (254, 216, 130)),
    "cobre": ((78, 51, 45), (152, 92, 61), (221, 157, 101)),
}


def icone_chave(metal):
    sombra, cor, brilho = METAIS[metal]
    icone = pygame.Surface((14, 14), pygame.SRCALPHA)
    contorno = (27, 28, 33)
    pygame.draw.polygon(icone, contorno, ((6, 8), (9, 5), (13, 9), (13, 12), (11, 12), (10, 10), (8, 12)))
    pygame.draw.lines(icone, sombra, False, ((6, 6), (11, 11), (12, 10)), 3)
    pygame.draw.line(icone, cor, (6, 5), (12, 11), 2)
    pygame.draw.line(icone, brilho, (9, 8), (11, 10))
    pygame.draw.circle(icone, contorno, (5, 5), 5)
    pygame.draw.circle(icone, sombra, (5, 5), 4)
    pygame.draw.arc(icone, brilho, (1, 1, 8, 8), 1.1, 3.9, 2)
    pygame.draw.circle(icone, (0, 0, 0, 0), (5, 5), 2)
    return pygame.transform.scale(icone, (28, 28))


@lru_cache(maxsize=6)
def _arte_portao(metal, aberto, lado):
    sombra, cor, brilho = METAIS[metal]
    portal = pygame.Surface((60, 20))
    portal.fill((20, 23, 29))
    pygame.draw.rect(portal, (52, 55, 60), (0, 15, 60, 5))
    pygame.draw.line(portal, (87, 87, 86), (0, 16), (59, 16))
    pygame.draw.line(portal, sombra, (0, 18), (59, 18))

    if aberto:
        for y, tom in ((4, (32, 35, 41)), (7, (45, 46, 49)), (11, (58, 57, 58))):
            pygame.draw.rect(portal, tom, (5, y, 50, 2))
        pygame.draw.line(portal, cor, (9, 14), (50, 14))
    else:
        pygame.draw.rect(portal, (50, 34, 35), (5, 3, 50, 11))
        for x in range(8, 54, 5):
            pygame.draw.rect(portal, (79, 51, 43), (x, 3, 4, 11))
            pygame.draw.line(portal, (102, 66, 49), (x, 3), (x, 13))
        for y in (5, 11):
            pygame.draw.line(portal, sombra, (5, y), (54, y), 2)
            for x in range(8, 54, 7):
                portal.set_at((x, y), cor)
        pygame.draw.polygon(portal, sombra, ((25, 4), (34, 4), (37, 8), (34, 13), (25, 13), (22, 8)))
        pygame.draw.polygon(portal, cor, ((26, 4), (33, 4), (36, 8), (33, 12), (26, 12), (23, 8)))
        pygame.draw.line(portal, brilho, (26, 5), (33, 5))
        pygame.draw.circle(portal, (30, 28, 31), (29, 7), 2)
        pygame.draw.line(portal, (30, 28, 31), (29, 7), (29, 10), 2)

    for x in (0, 54):
        pygame.draw.rect(portal, (57, 60, 64), (x, 0, 6, 16))
        pygame.draw.rect(portal, (87, 88, 86), (x + 1, 2, 4, 12))
        pygame.draw.line(portal, sombra, (x + 1, 3), (x + 4, 3))
        pygame.draw.rect(portal, cor, (x + 2, 9, 2, 2))
        portal.set_at((x + 2, 9), brilho)
    giro = {"norte": 0, "leste": -90, "oeste": 90, "sul": 180}
    portal = pygame.transform.rotate(portal, giro[lado])
    largura, altura = portal.get_size()
    return pygame.transform.scale(portal, (largura * TAMANHO_CELULA // 20, altura * TAMANHO_CELULA // 20))


def desenhar_portao(tela, x, y, metal, aberto):
    centro = TAMANHO_MAPA // 2
    ultima = TAMANHO_MAPA - 1
    if x in (0, ultima) and y == centro:
        lado = "oeste" if x == 0 else "leste"
        tela.blit(_arte_portao(metal, aberto, lado), (x * TAMANHO_CELULA, (y - 1) * TAMANHO_CELULA))
    elif y in (0, ultima) and x == centro:
        lado = "norte" if y == 0 else "sul"
        tela.blit(_arte_portao(metal, aberto, lado), ((x - 1) * TAMANHO_CELULA, y * TAMANHO_CELULA))
