from random import choice, randint

import pygame

from jogo.configuracoes import TAMANHO_CELULA, VELOCIDADE
from jogo.mapa import identificando_buraco, pode_andar


FPS_CAMINHADA = 18
MULTIPLICADOR_VELOCIDADE = 0.5


class inimigos:
    # representa um inimigo na matriz, sua posição, vida e cronômetros.
    def __init__(self, grade_x, grade_y):
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.em_movimento = False
        self.direcao = (0, 0)
        self.passos_restantes = 0
        self.tempo_invulneravel = 0.0
        self.tempo_parado = 0.0
        self.vida = 3
        self.morto = False

    def levar_dano(self, quantidade):
        # desconta vida caso o inimigo não esteja invulnerável e ativa o tempo de proteção.
        if self.tempo_invulneravel <= 0.0:
            self.vida = self.vida - quantidade
            if self.vida <= 0:
                self.vida = 0
                self.morto = True
            else:
                self.tempo_invulneravel = 0.2
                self.tempo_parado = 0.5
            return True
        return False

    def atualizar(self, dt, mundo):
        # atualiza o movimento em sequência na grade e os cronômetros do inimigo.
        if self.morto:
            return

        velocidade = VELOCIDADE * MULTIPLICADOR_VELOCIDADE

        # inicia um novo trajeto ou continua na direção atual se não estiver pausado.
        if not self.em_movimento and self.tempo_parado <= 0.0:
            if self.passos_restantes <= 0:
                self.direcao = choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
                self.passos_restantes = randint(2, 5)

            proximo_x = self.grade_x + self.direcao[0]
            proximo_y = self.grade_y + self.direcao[1]

            if pode_andar(mundo, proximo_x, proximo_y) and not identificando_buraco(mundo, proximo_x, proximo_y):
                self.destino_x = proximo_x
                self.destino_y = proximo_y
                self.em_movimento = True
            else:
                # interrompe a sequência e pausa ao encontrar parede ou buraco.
                self.passos_restantes = 0
                self.tempo_parado = 0.8

        # desliza suavemente até o centro da célula de destino.
        if self.em_movimento:
            alvo_x = self.destino_x * TAMANHO_CELULA
            alvo_y = self.destino_y * TAMANHO_CELULA
            diferenca_x = alvo_x - self.x
            diferenca_y = alvo_y - self.y
            distancia = (diferenca_x ** 2 + diferenca_y ** 2) ** 0.5

            passo = velocidade * dt
            if distancia <= passo:
                self.x = float(alvo_x)
                self.y = float(alvo_y)
                self.grade_x = self.destino_x
                self.grade_y = self.destino_y
                self.em_movimento = False
                self.passos_restantes -= 1
                if self.passos_restantes <= 0:
                    self.tempo_parado = 0.8
            else:
                proporcao = passo / distancia
                self.x += diferenca_x * proporcao
                self.y += diferenca_y * proporcao

        # reduz os cronômetros de invulnerabilidade e pausa.
        self.tempo_invulneravel -= dt
        if self.tempo_invulneravel < 0:
            self.tempo_invulneravel = 0.0

        self.tempo_parado -= dt
        if self.tempo_parado < 0:
            self.tempo_parado = 0.0

    def desenhar(self, tela):
        # desenha o retângulo do inimigo na tela, piscando enquanto estiver invulnerável.
        if not self.morto:
            if self.tempo_invulneravel <= 0 or int(self.tempo_invulneravel * 12) % 2 == 0:
                pygame.draw.rect(
                    tela,
                    (200, 50, 50),
                    (round(self.x), round(self.y), TAMANHO_CELULA, TAMANHO_CELULA),
                )