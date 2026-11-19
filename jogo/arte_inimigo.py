import pygame

from jogo.configuracoes import TAMANHO_CELULA


# Marfim e cobre envelhecido, com contorno escuro para os pisos das ruínas.
PALETA = {
    "#": (32, 27, 29),
    "s": (112, 92, 73),
    "o": (190, 165, 124),
    "l": (240, 220, 173),
    "*": (255, 170, 66),
}

ESQUELETO = (
    ".......######.......",
    "......#lllloo#......",
    ".....#llllooos#.....",
    ".....#lollooss#.....",
    ".....#l##o##os#.....",
    ".....#l#*o#*os#.....",
    "......#oo#os##......",
    ".......#lolo#.......",
    ".......######.......",
    "....###..#o#..###...",
    "...#lo###lol###os#..",
    "...#o###ooooo###s#..",
    "...#o#.#l#o#s#.#o#..",
    "..#os#.#ooooo#.#s#..",
    "..###...#oo#...###..",
    ".......#loos#.......",
    "......##o##s##......",
    ".....#lo#..#os#.....",
    "....#ooo#..####.....",
    "....#####...........",
)


def carregar_esqueleto():
    largura = len(ESQUELETO[0])
    altura = len(ESQUELETO)
    pose = pygame.Surface((largura, altura), pygame.SRCALPHA)
    for y, linha in enumerate(ESQUELETO):
        for x, pixel in enumerate(linha):
            if pixel in PALETA:
                pose.set_at((x, y), PALETA[pixel])

    tamanho = round(TAMANHO_CELULA * 0.85)
    pose = pygame.transform.scale(pose, (tamanho, tamanho))
    quadros = []
    for imagem, altura_passo in ((pose, 0), (pygame.transform.flip(pose, True, False), 2)):
        quadro = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
        sombra = pygame.Rect(0, 0, tamanho * 3 // 4, max(1, tamanho // 5))
        sombra.midbottom = (TAMANHO_CELULA // 2, TAMANHO_CELULA)
        pygame.draw.ellipse(quadro, (23, 17, 20, 135), sombra)
        area = imagem.get_rect(midbottom=(TAMANHO_CELULA // 2, TAMANHO_CELULA - 2 - altura_passo))
        quadro.blit(imagem, area)
        quadros.append(quadro)
    return quadros
