import pygame

from jogo.blocos import BAU_FECHADO,BAU_ABERTO, BURACOS, IMAGENS, SOLIDOS
from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA
from jogo.entrada import desenhar_entrada


def _espinhos_ativos(mundo):
    return mundo.ident == "salao" and any(not inimigo.morto for inimigo in mundo.inimigos)


def pode_andar(mundo, x, y, jogador=None):
    # verifica se a célula (x, y) está dentro do mapa e não é um obstáculo sólido.
    # impede sair dos limites da matriz 17x17.
    
    if x < 0 or y < 0 or x >= TAMANHO_MAPA or y >= TAMANHO_MAPA:
        return False
    
    # escadas ficam na borda (onde normalmente há parede), mas permitem passagem.    
    if (x, y) in mundo.escadas:
        escada = mundo.escadas[(x, y)]
        tranca = escada.get("trancada")
        
        if tranca == "dourada":
            if jogador is None or not jogador.tem_chave_dourada:
                return False
        elif tranca == "prata":
            if jogador is None or not jogador.tem_chave_prata:
                return False
        elif tranca == "espinhos":
            if _espinhos_ativos(mundo):
                return False
            
        return mundo.ident != "lobby" or mundo.abertura_porta >= 1.0
    
    # na matriz usamos [y][x], pois 'y' representa a linha e 'x' a coluna.
    return mundo.grade[y][x] not in SOLIDOS


def desenhar_mapa(tela, mundo, imagens):
    # percorre a matriz do andar atual e desenha cada bloco e escada na tela.
    lobby = mundo.ident == "lobby"
    if lobby:
        desenhar_entrada(tela, tuple(tuple(linha) for linha in mundo.grade))
        # copia um bloco do proprio chao do lobby para manter o mesmo visual nas balsas.
        bloco_lobby = tela.subsurface(
            (8 * TAMANHO_CELULA, 14 * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
        ).copy()
        for plataforma in mundo.plataformas:
            plataforma.desenhar(tela, bloco_lobby)

    for y, linha in enumerate(mundo.grade):
        for x, bloco in enumerate(linha):
            if not lobby:
                nome_imagem = IMAGENS[bloco]
                tela.blit(imagens[nome_imagem], (x * TAMANHO_CELULA, y * TAMANHO_CELULA))
            if bloco == BAU_FECHADO:
                _desenhar_bau(tela, x, y)
            elif bloco == BAU_ABERTO:
                _desenhar_bau_aberto(tela, x, y)

    if lobby:
        _desenhar_porta(tela, mundo.abertura_porta)
        return

    # Cada célula exibe a tranca ou os degraus da passagem.
    for (x, y), escada in mundo.escadas.items():
        tranca = escada.get("trancada")
        
        if tranca == "dourada":
            _desenhar_fechadura(tela, x, y, (243, 211, 114))  # Dourado
        elif tranca == "prata":
            _desenhar_fechadura(tela, x, y, (192, 192, 192))  # Prateado
        elif tranca == "espinhos" and _espinhos_ativos(mundo):
            _desenhar_espinhos(tela, x, y)
        else:
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

# verifica primeiro se alguma plataforma esta cobrindo esta celula.
    for plataforma in mundo.plataformas:
        if plataforma.contem(x, y):
            return False

    # caso contrario, verifica se o bloco fixo da matriz e um buraco.
    return mundo.grade[y][x] in BURACOS


def atualizar_porta(mundo, jogador, dt):
    # Abre a ate duas celulas do centro do portao e fecha ao se afastar.
    if mundo.ident == "lobby":
        centro_x = (TAMANHO_MAPA // 2 + 0.5) * TAMANHO_CELULA
        centro_y = TAMANHO_CELULA / 2
        dx = jogador.x + TAMANHO_CELULA / 2 - centro_x
        dy = jogador.y + TAMANHO_CELULA / 2 - centro_y
        if dx * dx + dy * dy <= (2 * TAMANHO_CELULA) ** 2:
            mundo.abertura_porta = min(1.0, mundo.abertura_porta + dt * 2.5)
        else:
            mundo.abertura_porta = max(0.0, mundo.abertura_porta - dt * 2.5)


def _desenhar_porta(tela, abertura):
    px = (TAMANHO_MAPA // 2 - 1) * TAMANHO_CELULA
    pygame.draw.rect(tela, (10, 18, 22), (px, 0, 120, 40))
    for y in (18, 24, 30):
        pygame.draw.rect(tela, (37, 48, 46), (px + 12, y, 96, 3))
    # Duas folhas de madeira deslizam para as laterais dentro do portal.
    inicio = px + 8
    largura = 104
    folha = pygame.Surface((largura // 2, 28))
    folha.fill((32, 29, 25))
    for coluna in range(0, largura // 2, 9):
        pygame.draw.rect(folha, (91, 60, 37), (coluna + 1, 1, 7, 26))
        pygame.draw.line(folha, (128, 89, 51), (coluna + 2, 2), (coluna + 2, 25))
    for faixa in (5, 21):
        pygame.draw.rect(folha, (48, 48, 54), (0, faixa, largura // 2, 3))
        for rebite in range(4, largura // 2, 12):
            pygame.draw.rect(folha, (158, 153, 132), (rebite, faixa, 2, 2))
    pygame.draw.rect(folha, (212, 170, 74), (largura // 2 - 8, 12, 4, 5))
    recorte_anterior = tela.get_clip()
    tela.set_clip(recorte_anterior.clip(pygame.Rect(inicio, 6, largura, 28)))
    deslocamento = round(abertura * largura / 2)
    tela.blit(folha, (inicio - deslocamento, 6))
    tela.blit(pygame.transform.flip(folha, True, False),
              (inicio + largura // 2 + deslocamento, 6))
    tela.set_clip(recorte_anterior)

    perfil = ((0, 34), (0, 18), (12, 7), (37, 0), (83, 0), (108, 7),
              (120, 18), (120, 34), (110, 34), (110, 22), (102, 15),
              (81, 8), (39, 8), (18, 15), (10, 22), (10, 34))
    pygame.draw.polygon(tela, (111, 117, 98), [(px + x, y) for x, y in perfil])
    for x, y, fim_x, fim_y in ((12, 7, 18, 15), (36, 0, 39, 8), (84, 0, 81, 8),
                               (108, 7, 102, 15), (0, 25, 10, 25), (110, 25, 120, 25)):
        pygame.draw.line(tela, (53, 61, 55), (px + x, y), (px + fim_x, fim_y), 2)
    pygame.draw.polygon(tela, (170, 151, 100),
                        ((px + 54, 0), (px + 66, 0), (px + 64, 8), (px + 56, 8)))
    pygame.draw.rect(tela, (124, 124, 97), (px, 34, 120, 3))
    pygame.draw.rect(tela, (57, 66, 59), (px, 37, 120, 3))


def _desenhar_bau(tela, x, y):
    # Bau fechado decorativo: madeira, ferragens douradas e fechadura.
    px, py = x * TAMANHO_CELULA, y * TAMANHO_CELULA
    detalhes = (
        ((27, 25, 31), (4, 30, 32, 6)),
        ((33, 24, 27), (4, 10, 32, 23)),
        ((33, 24, 27), (7, 7, 26, 6)),
        ((167, 94, 44), (7, 10, 26, 10)),
        ((201, 131, 58), (10, 10, 20, 3)),
        ((110, 57, 35), (7, 22, 26, 8)),
        ((55, 32, 30), (7, 19, 26, 3)),
        ((218, 177, 80), (10, 10, 3, 20)),
        ((218, 177, 80), (27, 10, 3, 20)),
        ((243, 211, 114), (16, 18, 8, 8)),
        ((54, 39, 30), (19, 20, 2, 4)),
    )
    for cor, (dx, dy, largura, altura) in detalhes:
        pygame.draw.rect(tela, cor, (px + dx, py + dy, largura, altura))


#verificar se há algum baú perto
def obter_bau_proximo(mundo, jogador):
    jx, jy = jogador.grade_x, jogador.grade_y
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        bx, by = jx + dx, jy + dy
        if (bx, by) in mundo.baus and mundo.grade[by][bx] == BAU_FECHADO:
            return (bx, by)
    return None


def _desenhar_bau_aberto(tela, x, y):
    px, py = x * TAMANHO_CELULA, y * TAMANHO_CELULA
    detalhes = (
        ((27, 25, 31), (4, 39, 32, 6)),
        ((33, 24, 27), (4, 16, 32, 17)), #base do baú
        ((20, 12, 15), (7, 17, 26, 5)), #interior escuro aberto
        ((110, 57, 35), (7, 22, 26, 8)), #madeira frontal
        ((218, 177, 80), (10, 20, 3, 10)), #ferragem esuerda
        ((218, 177, 80), (27, 20, 3, 10)), #ferragem direita
    )
    for cor, (dx, dy, largura, altura) in detalhes:
        pygame.draw.rect(tela, cor, (px + dx, py + dy, largura, altura))

# Desenha a fechadura para os cadeados dourado (norte) e prateado (leste)
def _desenhar_fechadura(tela, x, y, cor):
    px, py = x * TAMANHO_CELULA, y * TAMANHO_CELULA
    pygame.draw.rect(tela, (30, 30, 30), (px, py, TAMANHO_CELULA, TAMANHO_CELULA))
    
    # Cor prata para a porta lado leste
    if cor == (192, 192, 192):  
        cor_base = (200, 205, 215)      
        cor_brilho = (245, 248, 255)    
        cor_sombra = (120, 125, 135)    
    # Cor dourada para a porta lado norte
    else:  
        cor_base = cor
        cor_brilho = (255, 255, 200)
        cor_sombra = (150, 130, 50)

    # Corpo do cadeado com efeito metálico
    pygame.draw.rect(tela, cor_sombra, (px + 12, py + 15, 16, 14), border_radius=2)
    pygame.draw.rect(tela, cor_base, (px + 12, py + 14, 16, 13), border_radius=2)
    
    # Arco do cadeado
    pygame.draw.arc(tela, cor_base, (px + 14, py + 6, 12, 14), 0, 3.14, 3)
    
    # Detalhe de brilho (reflexo no metal)
    pygame.draw.line(tela, cor_brilho, (px + 14, py + 15), (px + 14, py + 22), 2)
    
    # Buraco da fechadura
    pygame.draw.rect(tela, (20, 20, 20), (px + 18, py + 18, 4, 6))
    
# Desenha a fechadura de espinhos para a porta oeste
def _desenhar_espinhos(tela, x, y):
    px, py = x * TAMANHO_CELULA, y * TAMANHO_CELULA
    pygame.draw.rect(tela, (30, 30, 30), (px, py, TAMANHO_CELULA, TAMANHO_CELULA))
    
    # Desenha os espinhos na horizontal (apontando para a direita, saindo da parede oeste)
    for offset_y in [6, 18]:
        pontos = [
            (px + 4, py + offset_y),         # Base esquerda (junto à parede)
            (px + 26, py + offset_y + 4),    # Ponta afiada à direita
            (px + 4, py + offset_y + 8)      # Base esquerda
        ]
        pygame.draw.polygon(tela, (150, 160, 170), pontos)
        # Linha de reflexo de luz no espinho
        pygame.draw.line(tela, (220, 230, 240), (px + 4, py + offset_y + 4), (px + 22, py + offset_y + 4), 1)
