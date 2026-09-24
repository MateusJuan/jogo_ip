import pygame

# ============================================================
# INICIALIZAÇÃO
# ============================================================

pygame.init()

# ============================================================
# CONFIGURAÇÕES
# ============================================================

TAMANHO_CELULA = 40
TAMANHO_MAPA = 17

LARGURA = TAMANHO_MAPA * TAMANHO_CELULA
ALTURA = TAMANHO_MAPA * TAMANHO_CELULA

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Lost Ruins: Hords of Dooms")

clock = pygame.time.Clock()

# ============================================================
# CARREGAR IMAGENS
# ============================================================

grama = pygame.image.load(
    "assets/grama.png"
).convert()

pedra = pygame.image.load(
    "assets/pedra.png"
).convert_alpha()

personagem = pygame.image.load(
    "assets/personagem.png"
).convert_alpha()

# ============================================================
# REDIMENSIONAR IMAGENS
# ============================================================

grama = pygame.transform.scale(
    grama,
    (TAMANHO_CELULA, TAMANHO_CELULA)
)

pedra = pygame.transform.scale(
    pedra,
    (TAMANHO_CELULA, TAMANHO_CELULA)
)

personagem = pygame.transform.scale(
    personagem,
    (TAMANHO_CELULA, TAMANHO_CELULA)
)

# ============================================================
# CRIAR MAPA
# ============================================================

# 0 = grama
# 1 = pedra

mapa = [
    [0 for _ in range(TAMANHO_MAPA)]
    for _ in range(TAMANHO_MAPA)
]

# ============================================================
# COLOCAR PEDRAS NAS BORDAS
# ============================================================

# Borda superior e inferior

for x in range(TAMANHO_MAPA):
    mapa[0][x] = 1
    mapa[TAMANHO_MAPA - 1][x] = 1

# Borda esquerda e direita

for y in range(TAMANHO_MAPA):
    mapa[y][0] = 1
    mapa[y][TAMANHO_MAPA - 1] = 1

# ============================================================
# CRIAR AS 4 ENTRADAS
# ============================================================

# Vamos usar duas células para cada entrada.

centro = TAMANHO_MAPA // 2 - 1

# ============================================================
# CRIAR AS 4 ENTRADAS
# ============================================================

# Cada entrada terá 3 células de largura.

# Entrada de cima
mapa[0][centro] = 0
mapa[0][centro + 1] = 0
mapa[0][centro + 2] = 0

# Entrada de baixo
mapa[TAMANHO_MAPA - 1][centro] = 0
mapa[TAMANHO_MAPA - 1][centro + 1] = 0
mapa[TAMANHO_MAPA - 1][centro + 2] = 0

# Entrada da esquerda
mapa[centro][0] = 0
mapa[centro + 1][0] = 0
mapa[centro + 2][0] = 0

# Entrada da direita
mapa[centro][TAMANHO_MAPA - 1] = 0
mapa[centro + 1][TAMANHO_MAPA - 1] = 0
mapa[centro + 2][TAMANHO_MAPA - 1] = 0

# ============================================================
# JOGADOR
# ============================================================

# Começa no centro do mapa

player_x = TAMANHO_MAPA // 2
player_y = TAMANHO_MAPA // 2

# ============================================================
# CONTROLE DE MOVIMENTO
# ============================================================

# Tempo entre cada movimento do personagem.
#
# 150 = mais rápido
# 200 = médio
# 250 = mais lento

TEMPO_MOVIMENTO = 150

ultimo_movimento = 0

# ============================================================
# VERIFICAR SE PODE ANDAR
# ============================================================

def pode_andar(x, y):

    # Não pode sair do mapa

    if x < 0:
        return False

    if x >= TAMANHO_MAPA:
        return False

    if y < 0:
        return False

    if y >= TAMANHO_MAPA:
        return False

    # Não pode andar sobre pedra

    if mapa[y][x] == 1:
        return False

    return True


# ============================================================
# LOOP PRINCIPAL
# ============================================================

rodando = True

while rodando:

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    for evento in pygame.event.get():

        # Fechar janela

        if evento.type == pygame.QUIT:
            rodando = False

    # --------------------------------------------------------
    # TECLAS PRESSIONADAS
    # --------------------------------------------------------

    teclas = pygame.key.get_pressed()

    # Tempo atual

    agora = pygame.time.get_ticks()

    # Verifica se já passou tempo suficiente
    # para realizar outro movimento.

    if agora - ultimo_movimento >= TEMPO_MOVIMENTO:

        novo_x = player_x
        novo_y = player_y

        # ====================================================
        # CIMA
        # ====================================================

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:

            novo_y -= 1

        # ====================================================
        # BAIXO
        # ====================================================

        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:

            novo_y += 1

        # ====================================================
        # ESQUERDA
        # ====================================================

        elif teclas[pygame.K_a] or teclas[pygame.K_LEFT]:

            novo_x -= 1

        # ====================================================
        # DIREITA
        # ====================================================

        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:

            novo_x += 1

        # ====================================================
        # VERIFICAR MOVIMENTO
        # ====================================================

        if pode_andar(novo_x, novo_y):

            player_x = novo_x
            player_y = novo_y

            ultimo_movimento = agora

    # --------------------------------------------------------
    # DESENHAR
    # --------------------------------------------------------

    tela.fill((0, 0, 0))

    # --------------------------------------------------------
    # DESENHAR MAPA
    # --------------------------------------------------------

    for y in range(TAMANHO_MAPA):

        for x in range(TAMANHO_MAPA):

            # Posição em pixels

            pos_x = x * TAMANHO_CELULA
            pos_y = y * TAMANHO_CELULA

            # Se for pedra

            if mapa[y][x] == 1:

                tela.blit(
                    pedra,
                    (pos_x, pos_y)
                )

            # Se for grama

            else:

                tela.blit(
                    grama,
                    (pos_x, pos_y)
                )

    # --------------------------------------------------------
    # DESENHAR PERSONAGEM
    # --------------------------------------------------------

    pos_player_x = player_x * TAMANHO_CELULA
    pos_player_y = player_y * TAMANHO_CELULA

    tela.blit(
        personagem,
        (
            pos_player_x,
            pos_player_y
        )
    )

    # --------------------------------------------------------
    # ATUALIZAR TELA
    # --------------------------------------------------------

    pygame.display.flip()

    # Limita para 60 FPS

    clock.tick(60)


# ============================================================
# ENCERRAR PYGAME
# ============================================================

pygame.quit()