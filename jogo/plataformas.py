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

    def contem(self, gx, gy, offset_x=0):
        # verifica se a celula (gx, gy) esta sobre esta plataforma (com deslocamento opcional).
        x_base = self.x + offset_x
        return (
            x_base <= gx < x_base + self.largura
            and self.y <= gy < self.y + self.altura
        )

    def _deve_carregar_jogador(self, jogador, dx):
        if jogador is None:
            return False

        na_origem = self.contem(jogador.grade_x, jogador.grade_y)
        if not jogador.em_movimento:
            return na_origem

        no_destino = self.contem(jogador.destino_x, jogador.destino_y)

        # Caminhando dentro da propria plataforma: acompanha o deslocamento.
        if na_origem and no_destino:
            return True

        # Saindo da plataforma para o chao fixo ou abismo: nao arrasta no meio do passo.
        if na_origem and not no_destino:
            return False

        # Entrando na plataforma vindo de fora: se ela sair debaixo do destino depois
        # de o jogador ja ter cruzado metade do passo, carrega-o junto para pousar nela.
        if not na_origem and no_destino and not self.contem(jogador.destino_x, jogador.destino_y, offset_x=dx):
            dist_x = (jogador.destino_x - jogador.grade_x) * TAMANHO_CELULA
            dist_y = (jogador.destino_y - jogador.grade_y) * TAMANHO_CELULA
            dist_total = (dist_x ** 2 + dist_y ** 2) ** 0.5
            if dist_total > 0:
                restante_x = jogador.destino_x * TAMANHO_CELULA - jogador.x
                restante_y = jogador.destino_y * TAMANHO_CELULA - jogador.y
                dist_restante = (restante_x ** 2 + restante_y ** 2) ** 0.5
                progresso = 1.0 - (dist_restante / dist_total)
                return progresso >= 0.5

        return False

    def atualizar(self, dt, jogador):
        # avanca a plataforma na horizontal e carrega o jogador se ele estiver em cima.
        if self.tempo_pausa > 0.0:
            self.tempo_pausa = max(0.0, self.tempo_pausa - dt)
            return

        self.tempo_passo += (dt / 1.5)
        if self.tempo_passo < self.intervalo_passo:
            return

        self.tempo_passo -= self.intervalo_passo
        dx = self.direcao

        # verifica se atingiu uma das bordas para inverter o sentido e pausar.
        if self.x + dx < self.x_min or self.x + dx > self.x_max:
            self.direcao = -self.direcao
            self.tempo_pausa = self.pausa_borda
            return

        # move o jogador junto apenas quando o passo estiver sincronizado com a plataforma.
        if self._deve_carregar_jogador(jogador, dx):
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