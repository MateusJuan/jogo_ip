# caminho da pasta onde ficam as imagens (.png) do jogo.
PASTA_ASSETS = "assets"

# dimensões da grade e da janela:
# cada célula tem 40x40 pixels e o mapa é uma matriz 17x17 (680x680 pixels).
TAMANHO_CELULA = 40
TAMANHO_MAPA = 17
LARGURA = TAMANHO_MAPA * TAMANHO_CELULA
ALTURA = TAMANHO_MAPA * TAMANHO_CELULA

# taxa de atualização da tela (quadros por segundo).
FPS = 60

SLOTS_INVENTARIO = 5

# aproxima a camera: cada pixel do mundo ocupa dois pixels na janela.
ZOOM_CAMERA = 1.5

# velocidade do personagem em pixels por segundo.
# como cada célula tem 40 px, 270 px/s faz ele atravessar uma casa em ~0,15 s,
# criando um deslize suave entre uma célula e outra.
VELOCIDADE = 270

# título exibido na barra superior da janela.
TITULO = "Lost Ruins: Hords of Doom"

RAIO_VISAO_PADRAO = 220  # em pixels na tela
RAIO_VISAO_REDUZIDO = 150