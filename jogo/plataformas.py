import pygame

from jogo.configuracoes import TAMANHO_CELULA, TAMANHO_MAPA


class Plataforma:
    # representa uma plataforma movel horizontal que transporta o jogador sobre o abismo.
    def __init__(self, x, y, largura, altura, x_min, x_max, direcao, intervalo_passo, pausa_borda=0.35):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.x_min = x_min
        self.x_max = x_max
        self.direcao = direcao
        self.intervalo_passo = intervalo_passo
        self.pausa_borda = pausa_borda
        self.tempo_passo = 0.0
        self.tempo_pausa = 0.0

    def contem(self, gx, gy):
        # verifica se a celula (gx, gy) esta sobre esta plataforma.
        return (
            self.x <= gx < self.x + self.largura
            and self.y <= gy < self.y + self.altura
        )

    def atualizar(self, dt, jogador):
        # avanca a plataforma na horizontal e carrega o jogador se ele estiver em cima.
        if self.tempo_pausa > 0.0:
            self.tempo_pausa = max(0.0, self.tempo_pausa - dt)
            return

        self.tempo_passo += dt
        if self.tempo_passo < self.intervalo_passo:
            return

        self.tempo_passo -= self.intervalo_passo
        dx = self.direcao

        # verifica se atingiu uma das bordas para inverter o sentido e pausar.
        if self.x + dx < self.x_min or self.x + dx > self.x_max:
            self.direcao = -self.direcao
            self.tempo_pausa = self.pausa_borda
            return

        # move o jogador junto caso ele esteja pisando na plataforma.
        if jogador is not None and self.contem(jogador.grade_x, jogador.grade_y):
            novo_destino = jogador.destino_x + dx
            if 1 <= novo_destino < TAMANHO_MAPA - 1:
                jogador.grade_x += dx
                jogador.destino_x = novo_destino
                jogador.x += dx * TAMANHO_CELULA

        self.x += dx

    def desenhar(self, tela, imagem_chao):
        # desenha os blocos de chao que formam a plataforma na posicao atual.
        for linha in range(self.altura):
            for coluna in range(self.largura):
                px = (self.x + coluna) * TAMANHO_CELULA
                py = (self.y + linha) * TAMANHO_CELULA
                tela.blit(imagem_chao, (px, py))