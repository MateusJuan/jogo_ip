import pygame

from jogo.configuracoes import PASTA_ASSETS, TAMANHO_CELULA


def _carregar(nome, com_alpha=False):
    # carrega uma imagem da pasta assets e redimensiona para o tamanho da célula (40x40).
    imagem = pygame.image.load(PASTA_ASSETS + "/" + nome)
    # o convert_alpha() preserva o fundo transparente (usado no sprite do personagem).
    imagem = imagem.convert_alpha() if com_alpha else imagem.convert()
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


def carregar_imagens():
    # carrega todas as texturas do jogo uma única vez e guarda em um dicionário.
    return {
        "grama": _carregar("grama.png"),
        "muro": _carregar("muro.png"),
        "salao_chao": _carregar("salao_chao.png"),
        "salao_entulho": _carregar("salao_entulho.png"),
        "salao_parede": _carregar("salao_parede.png"),
        "galeria_chao": _carregar("galeria_chao.png"),
        "galeria_buraco": _carregar("galeria_buraco.png"),
        "galeria_parede": _carregar("galeria_parede.png"),
        "torre_chao": _carregar("torre_chao.png"),
        "torre_pilar": _carregar("torre_pilar.png"),
        "torre_parede": _carregar("torre_parede.png"),
        "torre_altar": _carregar("torre_altar.png"),
        "personagem": _carregar("personagem.png", com_alpha=True),
    }