from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA_ASSETS = RAIZ / "assets"

TAMANHO_CELULA = 40
TAMANHO_MAPA = 17

LARGURA = TAMANHO_MAPA * TAMANHO_CELULA
ALTURA = TAMANHO_MAPA * TAMANHO_CELULA

FPS = 60

# Pixels por segundo. Cada célula tem 40 px,
# então 270 deixa o ritmo perto do movimento antigo (uma célula a cada ~150 ms),
# só que o sprite desliza em vez de teletransportar.
VELOCIDADE = 270

TITULO = "Lost Ruins: Hords of Dooms"
