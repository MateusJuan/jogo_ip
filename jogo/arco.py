import pygame

from jogo.blocos import SOLIDOS
from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA
from jogo.lagarto import ferir_lagarto, retangulo_lagarto


class Projetil:
    # Base compartilhada pelas flechas do jogador e pelo fogo hostil do lagarto.
    def __init__(self, x, y, direcao, dano=1, velocidade=450.0,
                 dono="jogador", tipo_dano="flecha", tempo_vida=1.5):
        dx, dy = direcao
        if dx == 0 and dy == 0:
            dx, dy = 1, 0

        tamanho = (dx**2 + dy**2) ** 0.5
        self.direcao = (dx / tamanho, dy / tamanho)
        self.vx = self.direcao[0] * velocidade
        self.vy = self.direcao[1] * velocidade

        self.x = x + TAMANHO_CELULA / 2
        self.y = y + TAMANHO_CELULA / 2
        self.dano = dano
        self.dono = dono
        self.tipo_dano = tipo_dano
        self.ativa = True
        self.tempo_vida = tempo_vida

    def retangulo(self):
        tamanho = 14 if self.tipo_dano == "fogo" else 10
        return pygame.Rect(round(self.x - tamanho / 2), round(self.y - tamanho / 2),
                           tamanho, tamanho)

    def _bateu_em_solido(self, mundo):
        coluna = int(self.x // TAMANHO_CELULA)
        linha = int(self.y // TAMANHO_CELULA)
        if coluna < 0 or linha < 0 or coluna >= TAMANHO_MAPA or linha >= TAMANHO_MAPA:
            return True
        if mundo is None:
            return False
        return mundo.grade[linha][coluna] in SOLIDOS

    def atualizar(self, dt, mundo=None, inimigos=None, jogador=False, chefe=False):
        if not self.ativa:
            return
        if self.tempo_vida <= 0:
            self.ativa = False
            return
        intervalo = min(max(0.0, dt), self.tempo_vida)
        # Subpassos evitam atravessar paredes ou alvos entre dois quadros.
        distancia = (self.vx ** 2 + self.vy ** 2) ** 0.5 * intervalo
        passos = max(1, int(distancia / (TAMANHO_CELULA / 4)) + 1)
        indice = 0
        while indice < passos and self.ativa:
            self.x += self.vx * intervalo / passos
            self.y += self.vy * intervalo / passos
            if self._bateu_em_solido(mundo):
                self.ativa = False
            else:
                self._atingir_alvos(inimigos, jogador, chefe)
            indice += 1
        self.tempo_vida = max(0.0, self.tempo_vida - max(0.0, dt))
        if self.tempo_vida == 0:
            self.ativa = False

    def _atingir_alvos(self, inimigos, jogador, chefe):
        area = self.retangulo()
        if self.dono != "jogador":
            if jogador and not jogador.game_over:
                alvo = pygame.Rect(round(jogador.x), round(jogador.y),
                                   TAMANHO_CELULA, TAMANHO_CELULA)
                if area.colliderect(alvo):
                    jogador.levar_dano(self.dano)
                    self.ativa = False
        elif chefe and not chefe["morto"] and area.colliderect(retangulo_lagarto(chefe)):
            ferir_lagarto(chefe, self.dano, self.tipo_dano)
            self.ativa = False
        elif inimigos is not None:
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
                    if area.colliderect(rect_inimigo):
                        inimigo.levar_dano(self.dano)
                        self.ativa = False
                        acertou = True
                indice += 1

    def desenhar(self, tela):
        if not self.ativa:
            return

        if self.tipo_dano == "fogo":
            self._desenhar_fogo(tela)
        else:
            pygame.draw.rect(tela, (240, 210, 90), self.retangulo())

    def _desenhar_fogo(self, tela):
        centro = pygame.Vector2(self.x, self.y)
        rumo = pygame.Vector2(self.direcao)
        lateral = pygame.Vector2(-rumo.y, rumo.x)
        oscilacao = int(self.tempo_vida * 24) % 3
        pygame.draw.polygon(tela, (163, 50, 32),
                            (centro + rumo * 8, centro + lateral * 7, centro - rumo * 22,
                             centro - rumo * 12 + lateral * 2, centro - lateral * 7))
        pygame.draw.polygon(tela, (255, 129, 45),
                            (centro + rumo * 7, centro + lateral * 5, centro - rumo * 15,
                             centro - lateral * 5))
        pygame.draw.polygon(tela, (255, 228, 134),
                            (centro + rumo * 5, centro + lateral * 3, centro - rumo * 7,
                             centro - lateral * 3))
        for distancia, desvio in ((19, -4), (25, 3), (29, -2)):
            faisca = centro - rumo * (distancia + oscilacao) + lateral * desvio
            pygame.draw.rect(tela, (214, 83, 37), (round(faisca.x), round(faisca.y), 2, 2))


# Preserva a interface ja usada pelo arco.
Flecha = Projetil
