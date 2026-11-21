import pygame

from jogo.blocos import SOLIDOS
from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA


class Flecha:
    # projétil disparado pelo arco na direção em que o jogador está olhando.
    def __init__(self, x, y, direcao, dano=1, velocidade=450.0):
        dx, dy = direcao
        if dx == 0 and dy == 0:
            dx, dy = 1, 0

        tamanho = (dx**2 + dy**2) ** 0.5
        self.vx = (dx / tamanho) * velocidade
        self.vy = (dy / tamanho) * velocidade

        self.x = x + TAMANHO_CELULA / 2
        self.y = y + TAMANHO_CELULA / 2
        self.dano = dano
        self.ativa = True
        self.tempo_vida = 1.5

    def _bateu_em_solido(self, mundo):
        if mundo is None:
            return False
        coluna = int(self.x // TAMANHO_CELULA)
        linha = int(self.y // TAMANHO_CELULA)
        if coluna < 0 or linha < 0 or coluna >= TAMANHO_MAPA or linha >= TAMANHO_MAPA:
            return True
        return mundo.grade[linha][coluna] in SOLIDOS

    def atualizar(self, dt, mundo=None, inimigos=None):
        if not self.ativa:
            return

        self.tempo_vida -= dt
        if self.tempo_vida <= 0:
            self.ativa = False
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self._bateu_em_solido(mundo):
            self.ativa = False
            return

        tamanho_flecha = max(8, round(TAMANHO_CELULA * 0.25))
        rect_flecha = pygame.Rect(
            round(self.x - tamanho_flecha / 2),
            round(self.y - tamanho_flecha / 2),
            tamanho_flecha,
            tamanho_flecha,
        )

        if inimigos is not None:
            acertou = False
            indice = 0
            while indice < len(inimigos) and not acertou:
                inimigo = inimigos[indice]
                if not inimigo.morto:
                    rect_inimigo = pygame.Rect(
                        round(inimigo.x),
                        round(inimigo.y),
                        TAMANHO_CELULA,
                        TAMANHO_CELULA,
                    )
                    if rect_flecha.colliderect(rect_inimigo):
                        inimigo.levar_dano(self.dano)
                        self.ativa = False
                        acertou = True
                indice += 1

    def desenhar(self, tela):
        if not self.ativa:
            return

        tamanho_flecha = max(8, round(TAMANHO_CELULA * 0.25))
        rect = pygame.Rect(
            round(self.x - tamanho_flecha / 2),
            round(self.y - tamanho_flecha / 2),
            tamanho_flecha,
            tamanho_flecha,
        )
        pygame.draw.rect(tela, (240, 210, 90), rect)