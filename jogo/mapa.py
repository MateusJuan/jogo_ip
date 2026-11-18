import pygame

from jogo.blocos import BAU_FECHADO,BAU_ABERTO, BURACOS, IMAGENS, SOLIDOS
from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA


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
            # Na Parte 1, os espinhos bloqueiam sempre a passagem
            return False
            
        return mundo.ident != "lobby" or mundo.abertura_porta >= 1.0
    
    # na matriz usamos [y][x], pois 'y' representa a linha e 'x' a coluna.
    return mundo.grade[y][x] not in SOLIDOS


def desenhar_mapa(tela, mundo, imagens):
    # percorre a matriz do andar atual e desenha cada bloco e escada na tela.
    for y, linha in enumerate(mundo.grade):
        for x, bloco in enumerate(linha):
            nome_imagem = IMAGENS[bloco]
            tela.blit(imagens[nome_imagem], (x * TAMANHO_CELULA, y * TAMANHO_CELULA))
            if bloco == BAU_FECHADO:
                _desenhar_bau(tela, x, y)

    # desenha as escadas por cima do piso nas posições cadastradas no mundo.
    for (x, y), escada in mundo.escadas.items():
        tranca = escada.get("trancada")
        
        if tranca == "dourada":
            _desenhar_fechadura(tela, x, y, (243, 211, 114))  # Dourado
        elif tranca == "prata":
            _desenhar_fechadura(tela, x, y, (192, 192, 192))  # Prateado
        elif tranca == "espinhos":
            _desenhar_espinhos(tela, x, y)
        elif mundo.ident == "lobby":
            _desenhar_porta(tela, x, y, mundo.abertura_porta)
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
    return mundo.grade[y][x] in BURACOS


def atualizar_porta(mundo, jogador, dt):
    # Abre ao chegar a duas celulas da entrada e permanece aberta.
    if mundo.ident == "lobby":
        centro_x = (TAMANHO_MAPA // 2 + 0.5) * TAMANHO_CELULA
        centro_y = TAMANHO_CELULA / 2
        dx = jogador.x + TAMANHO_CELULA / 2 - centro_x
        dy = jogador.y + TAMANHO_CELULA / 2 - centro_y
        if dx * dx + dy * dy <= (2 * TAMANHO_CELULA) ** 2:
            mundo.porta_ativada = True
        if mundo.porta_ativada:
            mundo.abertura_porta = min(1.0, mundo.abertura_porta + dt * 2.5)


def _desenhar_porta(tela, x, y, abertura):
    # Portal aberto de pedra, alinhado com as tres celulas da saida.
    px, py = x * TAMANHO_CELULA, y * TAMANHO_CELULA
    pygame.draw.rect(tela, (19, 22, 28), (px, py, 40, 40))
    pygame.draw.rect(tela, (105, 109, 110), (px, py, 40, 6))
    pygame.draw.rect(tela, (173, 163, 137), (px, py + 34, 40, 6))
    if x == TAMANHO_MAPA // 2 - 1:
        pygame.draw.rect(tela, (119, 122, 118), (px, py, 6, 34))
        pygame.draw.rect(tela, (67, 73, 77), (px + 6, py + 6, 3, 28))
    if x == TAMANHO_MAPA // 2 + 1:
        pygame.draw.rect(tela, (119, 122, 118), (px + 34, py, 6, 34))
        pygame.draw.rect(tela, (67, 73, 77), (px + 31, py + 6, 3, 28))

    # Duas folhas de madeira deslizam para as laterais dentro do portal.
    inicio = (TAMANHO_MAPA // 2 - 1) * TAMANHO_CELULA + 6
    largura = 3 * TAMANHO_CELULA - 12
    folha = pygame.Surface((largura // 2, 28))
    folha.fill((61, 34, 29))
    for coluna in range(0, largura // 2, 9):
        pygame.draw.rect(folha, (128, 73, 39), (coluna + 1, 1, 7, 26))
        pygame.draw.line(folha, (178, 112, 54), (coluna + 2, 2), (coluna + 2, 25))
    for faixa in (5, 21):
        pygame.draw.rect(folha, (48, 48, 54), (0, faixa, largura // 2, 3))
        for rebite in range(4, largura // 2, 12):
            pygame.draw.rect(folha, (158, 153, 132), (rebite, faixa, 2, 2))
    pygame.draw.rect(folha, (212, 170, 74), (largura // 2 - 8, 12, 4, 5))
    recorte_anterior = tela.get_clip()
    tela.set_clip(recorte_anterior.clip(pygame.Rect(px, py + 6, 40, 28)))
    deslocamento = round(abertura * largura / 2)
    tela.blit(folha, (inicio - deslocamento, py + 6))
    tela.blit(pygame.transform.flip(folha, True, False),
              (inicio + largura // 2 + deslocamento, py + 6))
    tela.set_clip(recorte_anterior)


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
        if (bx, by) in mundo.baus:
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