from pathlib import Path

import pygame


CAMINHO_FONTE = Path(__file__).resolve().parent.parent / "assets" / "fontes" / "Cinzel.ttf"
ESCALA_TEXTO = 2


def carregar_fonte(tamanho, negrito=False):
    # Desenha em baixa resolucao para que cada pixel ocupe 2x2 pixels na tela.
    fonte = pygame.font.Font(str(CAMINHO_FONTE), max(1, tamanho // ESCALA_TEXTO))
    fonte.set_bold(negrito)
    return fonte


def renderizar_texto(fonte, mensagem, cor):
    texto = fonte.render(mensagem, False, cor)
    return pygame.transform.scale(
        texto, (texto.get_width() * ESCALA_TEXTO, texto.get_height() * ESCALA_TEXTO)
    )
