import pygame

from jogo.configuracoes import PASTA_ASSETS, TAMANHO_CELULA


def _carregar(nome, com_alpha=False):
    # carrega uma imagem da pasta assets e redimensiona para o tamanho da célula (40x40).
    imagem = pygame.image.load(PASTA_ASSETS + "/" + nome)
    # o convert_alpha() preserva o fundo transparente (usado no sprite do personagem).
    imagem = imagem.convert_alpha() if com_alpha else imagem.convert()
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


def _carregar_caminhada(nome):
    # Divide a folha em quatro poses e alinha os pes na mesma altura.
    folha = pygame.image.load(PASTA_ASSETS + "/" + nome).convert_alpha()
    largura = folha.get_width() // 4
    poses = [folha.subsurface((i * largura, 0, largura, folha.get_height()))
             for i in range(4)]
    # Ignora pixels quase transparentes nas margens da imagem gerada.
    limites = [pose.get_bounding_rect(min_alpha=128) for pose in poses]
    referencia = _carregar("movimento_jogador/personagem.png", com_alpha=True).get_bounding_rect()
    escala = referencia.height / max(area.height for area in limites)
    quadros = []
    for pose, area in zip(poses, limites):
        tamanho = (max(1, round(area.width * escala)),
                   max(1, round(area.height * escala)))
        quadro = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
        imagem = pygame.transform.scale(pose.subsurface(area), tamanho)
        quadro.blit(imagem, (referencia.centerx - tamanho[0] // 2,
                            referencia.bottom - tamanho[1]))
        quadros.append(quadro)
    return quadros


def _carregar_costas():
    imagem = pygame.image.load(PASTA_ASSETS + "/movimento_jogador/personagem_costas.png").convert_alpha()
    area = imagem.get_bounding_rect(min_alpha=128)
    referencia = _carregar("movimento_jogador/personagem.png", com_alpha=True).get_bounding_rect()
    tamanho = (round(area.width * referencia.height / area.height), referencia.height)
    quadro = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    quadro.blit(pygame.transform.scale(imagem.subsurface(area), tamanho),
                (referencia.centerx - tamanho[0] // 2, referencia.top))
    return quadro


def _carregar_respiracao_direita():
    # Exportacao do Piskel: 16 quadros em ordem de leitura, numa grade 4x4.
    folha = pygame.image.load(PASTA_ASSETS + "/New Piskel.png").convert_alpha()
    largura = folha.get_width() // 4
    altura = folha.get_height() // 4
    quadros = []
    for linha in range(4):
        for coluna in range(4):
            pose = folha.subsurface((coluna * largura, linha * altura, largura, altura))
            # Mantem a celula inteira para preservar o deslocamento da respiracao.
            quadros.append(pygame.transform.scale(pose, (TAMANHO_CELULA, TAMANHO_CELULA)))
    return quadros


def _aplicar_paleta_piskel(quadros):
    # Usa apenas cores presentes na referencia, evitando variacoes entre estados.
    referencia = pygame.image.load(PASTA_ASSETS + "/New Piskel.png").convert_alpha()
    paleta = set()
    for y in range(referencia.get_height()):
        for x in range(referencia.get_width()):
            cor = referencia.get_at((x, y))
            if cor.a >= 128:
                paleta.add((cor.r, cor.g, cor.b))
    paleta = sorted(paleta)
    conversoes = {}
    for quadro in quadros:
        for y in range(quadro.get_height()):
            for x in range(quadro.get_width()):
                cor = quadro.get_at((x, y))
                if cor.a > 0:
                    rgb = (cor.r, cor.g, cor.b)
                    if rgb not in conversoes:
                        conversoes[rgb] = min(
                            paleta, key=lambda p: (p[0] - rgb[0]) ** 2
                            + (p[1] - rgb[1]) ** 2 + (p[2] - rgb[2]) ** 2
                        )
                    quadro.set_at((x, y), (*conversoes[rgb], cor.a))
    return quadros


def carregar_imagens():
    # carrega todas as texturas do jogo uma única vez e guarda em um dicionário.
    return {
        "respiracao_direita": _carregar_respiracao_direita(),
        "caminhada_frente": _carregar_caminhada("movimento_jogador/personagem_andando_frente.png"),
        "caminhada_direita": _aplicar_paleta_piskel(_carregar_caminhada("movimento_jogador/personagem_andando_direita.png")),
        "caminhada_esquerda": _aplicar_paleta_piskel(_carregar_caminhada("movimento_jogador/personagem_andando_esquerda.png")),
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
        "personagem": _carregar("movimento_jogador/personagem.png", com_alpha=True),
        "personagem_costas": _carregar_costas(),
    }
