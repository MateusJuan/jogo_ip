import pygame

from jogo.configuracoes import TAMANHO_CELULA, VELOCIDADE
from jogo.mapa import pode_andar, identificando_buraco


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
        self.vida_max = 3.0
        self.vida = 3.0
        self.tempo_invulneravel = 0.0
        self.tempo_parado = 0.0
        self.passos_seguros = [(grade_x, grade_y)]

    def definir_posicao(self, grade_x, grade_y):
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        self.em_movimento = False

    def levar_dano(self, quantidade):
        if self.tempo_invulneravel <= 0.0:
            self.vida = self.vida - quantidade
            if self.vida <= 0:
                self.vida = 0
            else:
                self.tempo_invulneravel = 1.2
                self.tempo_parado = 0.5
        else:
            return False

    def _desenhar_vida(self):
        for i in range(3):
            x = 12 + i * 32
            y = 12

            if self.jogador.vida >= i + 1:
                pygame.draw.rect(self.tela, (220, 40, 60), (x, y, 24, 24))
            elif self.jogador.vida >= i + 0.5:
                pygame.draw.rect(self.tela, (60, 40, 45), (x, y, 24, 24))
                pygame.draw.rect(self.tela, (220, 40, 60), (x, y, 12, 24))
            else:
                pygame.draw.rect(self.tela, (60, 40, 45), (x, y, 24, 24))

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
                self._chegar(mundo)
                continue

            passo = VELOCIDADE * restante
            if distancia <= passo:
                self.x = float(alvo_x)
                self.y = float(alvo_y)
                self._chegar(mundo)
                restante -= distancia / VELOCIDADE
            else:
                proporcao = passo / distancia
                self.x += diferenca_x * proporcao
                self.y += diferenca_y * proporcao
                restante = 0

        self.tempo_invulneravel -= dt/1.5
        self.tempo_parado -= dt
        if self.tempo_invulneravel < 0:
            self.tempo_invulneravel = 0.0
        if self.tempo_parado < 0:
            self.tempo_parado = 0.0

    def desenhar(self, tela):
        tela.blit(self.imagem, (round(self.x), round(self.y)))
        if self.tempo_invulneravel <= 0 or int(self.tempo_invulneravel * 12) % 2 == 0:
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

        if self.tempo_parado > 0:
            return False

        self.destino_x = proximo_x
        self.destino_y = proximo_y
        self.em_movimento = True
        return True

    def _chegar(self, mundo):
        if identificando_buraco(mundo, self.destino_x, self.destino_y) == False:
            self.grade_x = self.destino_x
            self.grade_y = self.destino_y
            self.passos_seguros.append((self.grade_x, self.grade_y))
            self.em_movimento = False
        else:
            self.levar_dano(0.5)
            if len(self.passos_seguros) >= 2:
                destino_seguro = self.passos_seguros[-2]
            else:
                destino_seguro = self.passos_seguros[0]
            self.definir_posicao(*destino_seguro)
            self.passos_seguros = [destino_seguro]
            self.tempo_parado = 1.0
            self.em_movimento = False
