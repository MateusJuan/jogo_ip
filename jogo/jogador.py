import pygame

from jogo.configuracoes import TAMANHO_CELULA, VELOCIDADE
from jogo.mapa import pode_andar


class Jogador:
    def __init__(self, grade_x, grade_y, imagem):
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.imagem = imagem
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.em_movimento = False

    def definir_posicao(self, grade_x, grade_y):
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        self.em_movimento = False

    def atualizar(self, dt, teclas, mundo):
        restante = dt

        while restante > 0:
            if not self.em_movimento:
                dx, dy = self._direcao(teclas)
                if not self._comecar_passo(dx, dy, mundo):
                    break

            alvo_x = self.destino_x * TAMANHO_CELULA
            alvo_y = self.destino_y * TAMANHO_CELULA
            diferenca_x = alvo_x - self.x
            diferenca_y = alvo_y - self.y
            distancia = (diferenca_x ** 2 + diferenca_y ** 2) ** 0.5

            if distancia == 0:
                self._chegar()
                continue

            passo = VELOCIDADE * restante
            if distancia <= passo:
                self.x = float(alvo_x)
                self.y = float(alvo_y)
                self._chegar()
                restante -= distancia / VELOCIDADE
            else:
                proporcao = passo / distancia
                self.x += diferenca_x * proporcao
                self.y += diferenca_y * proporcao
                restante = 0

    def desenhar(self, tela):
        tela.blit(self.imagem, (round(self.x), round(self.y)))

    def _direcao(self, teclas):
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            return 0, -1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            return 0, 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            return -1, 0
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            return 1, 0
        return 0, 0

    def _comecar_passo(self, dx, dy, mundo):
        if dx == 0 and dy == 0:
            return False

        proximo_x = self.grade_x + dx
        proximo_y = self.grade_y + dy
        if not pode_andar(mundo, proximo_x, proximo_y):
            return False

        self.destino_x = proximo_x
        self.destino_y = proximo_y
        self.em_movimento = True
        return True

    def _chegar(self):
        self.grade_x = self.destino_x
        self.grade_y = self.destino_y
        self.em_movimento = False
