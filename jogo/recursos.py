import pygame

from jogo.arte_inimigo import carregar_esqueleto
from jogo.configuracoes import PASTA_ASSETS, TAMANHO_CELULA


def _carregar(nome, com_alpha=False):
    # carrega uma imagem da pasta assets e redimensiona para o tamanho da célula (40x40).
    imagem = pygame.image.load(PASTA_ASSETS + "/" + nome)
    # o convert_alpha() preserva o fundo transparente (usado no sprite do personagem).
    imagem = imagem.convert_alpha() if com_alpha else imagem.convert()
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


def _carregar_costas():
    imagem = pygame.image.load(PASTA_ASSETS + "/movimento_jogador/parado_costas.png").convert_alpha()
    area = imagem.get_bounding_rect(min_alpha=128)
    referencia = _carregar("movimento_jogador/parado_direita.png", com_alpha=True).get_bounding_rect()
    tamanho = (round(area.width * referencia.height / area.height), referencia.height)
    quadro = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    quadro.blit(pygame.transform.scale(imagem.subsurface(area), tamanho),
                (referencia.centerx - tamanho[0] // 2, referencia.top))
    return quadro


def _carregar_animacao_piskel(nome, colunas, linhas, largura_em_celulas=1):
    # Le os quadros na ordem de exportacao, preservando a celula e o movimento dos pes.
    folha = pygame.image.load(PASTA_ASSETS + "/" + nome).convert_alpha()
    largura = folha.get_width() // colunas
    altura = folha.get_height() // linhas
    quadros = []
    for linha in range(linhas):
        for coluna in range(colunas):
            pose = folha.subsurface((coluna * largura, linha * altura, largura, altura))
            # Algumas folhas têm células vazias depois do último quadro.
            if pose.get_bounding_rect().width > 0:
                tamanho = (largura_em_celulas * TAMANHO_CELULA, TAMANHO_CELULA)
                quadros.append(pygame.transform.scale(pose, tamanho))
    return quadros

def _carregar_espada(nome):
    # Carrega a imagem da espada da pasta assets e garante transparência
    imagem = pygame.image.load(PASTA_ASSETS + "/" + nome).convert_alpha()
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


def carregar_imagens():
    # carrega todas as texturas do jogo uma única vez e guarda em um dicionário.
    respiracao_direita = _carregar_animacao_piskel(
        "movimento_jogador/respiracao_direita.png", 4, 4
    )
    caminhada_direita = _carregar_animacao_piskel(
        "movimento_jogador/corrida_direita.png", 3, 4
    )
    caminhada_direita = _carregar_animacao_piskel(
        "movimento_jogador/corrida_direita.png", 3, 4
    )
    
    # Carrega a espada base (apontando para a direita) caso utilize
    espada_base = _carregar_espada("espada.png")
    return {
        "esqueleto": carregar_esqueleto(),
        "respiracao_direita": respiracao_direita,
        "respiracao_esquerda": [pygame.transform.flip(quadro, True, False)
                               for quadro in respiracao_direita],
        "caminhada_costas": _carregar_animacao_piskel(
            "movimento_jogador/caminhada_costas.png", 3, 4
        ),
        "caminhada_frente": _carregar_animacao_piskel(
            "movimento_jogador/caminhada_frente.png", 3, 4
        ),
        "caminhada_direita": caminhada_direita,
        "caminhada_esquerda": [pygame.transform.flip(quadro, True, False)
                              for quadro in caminhada_direita],
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
        "personagem": _carregar("movimento_jogador/parado_direita.png", com_alpha=True),
        "personagem_costas": _carregar_costas(),
        "muro_labirinto": _carregar("muro_labirinto.jpg"),
        # Imagens da espada integradas sem perder nada
        "espada": espada_base,
        "ataque_direita": _carregar_animacao_piskel(
            "movimento_jogador/espada_direita.png", 2, 4, largura_em_celulas=2
        ),
        "ataque_esquerda": _carregar_animacao_piskel(
            "movimento_jogador/espada_esquerda.png", 2, 4, largura_em_celulas=2
        ),
        "ataque_costas": pygame.transform.rotate(espada_base, 90),
    }



