import pygame

from jogo.configuracoes import PASTA_ASSETS, TAMANHO_CELULA


def carregar_lagarto():
    folha = pygame.image.load(PASTA_ASSETS + "/lagarto_poses.png").convert_alpha()
    largura = folha.get_width() // 3
    altura = folha.get_height() // 3
    tamanho = TAMANHO_CELULA + 20
    estados = ("preparacao", "ataque", "cooldown")
    poses = {estado: {} for estado in estados}

    for coluna, direcao in enumerate(((1, 0), (0, 1), (0, -1))):
        recortes = []
        for linha in range(3):
            celula = folha.subsurface((coluna * largura, linha * altura, largura, altura))
            recortes.append(celula.subsurface(celula.get_bounding_rect(min_alpha=128)))

        # As três poses de cada direção mantêm a mesma escala e linha de apoio.
        escala = (tamanho // 2 - 1) / max(max(recorte.get_size()) for recorte in recortes)
        for estado, recorte in zip(estados, recortes):
            pose = pygame.transform.scale(recorte, (round(recorte.get_width() * escala),
                                                     round(recorte.get_height() * escala)))
            quadro = pygame.Surface((tamanho // 2, tamanho // 2), pygame.SRCALPHA)
            quadro.blit(pose, pose.get_rect(midbottom=(tamanho // 4, tamanho // 2)))
            imagem = pygame.transform.scale(quadro, (tamanho, tamanho))
            poses[estado][direcao] = imagem
            if coluna == 0:
                poses[estado][(-1, 0)] = pygame.transform.flip(imagem, True, False)
    return poses
