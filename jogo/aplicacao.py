import pygame

from jogo.configuracoes import ALTURA, FPS, LARGURA, TAMANHO_MAPA, TITULO
from jogo.jogador import Jogador
from jogo.mapa import desenhar_mapa
from jogo.mundos import criar_mundos
from jogo.recursos import carregar_imagens


class Aplicacao:
    # gerencia a janela do pygame, o loop principal, as trocas de andar e o desenho do hud.
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("arial", 20)
        self.imagens = carregar_imagens()
        self.mundos = criar_mundos()
        self.mundo = self.mundos["lobby"]
        centro = TAMANHO_MAPA // 2
        self.jogador = Jogador(centro, centro, self.imagens["personagem"])
        self.rodando = True

    def executar(self):
        # loop principal do jogo: processa eventos, atualiza a lógica e redesenha a tela a cada quadro.
        while self.rodando:
            # o dt (delta time) mede o tempo em segundos desde o último quadro (limitado a 0.05s).
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._eventos()
            self.jogador.atualizar(dt, pygame.key.get_pressed(), self.mundo)
            self._verificar_escada()
            self._desenhar()
        pygame.quit()

    def _eventos(self):
        # verifica os eventos da janela (como clicar no botão x para fechar o jogo).
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

    def _verificar_escada(self):
        # troca de andar caso o personagem tenha parado exatamente sobre uma célula de escada.
        if self.jogador.em_movimento:
            return
        posicao = (self.jogador.grade_x, self.jogador.grade_y)
        if posicao not in self.mundo.escadas:
            return
        escada = self.mundo.escadas[posicao]
        self.mundo = self.mundos[escada["destino"]]
        self.jogador.definir_posicao(escada["x"], escada["y"])

    def _desenhar(self):
        # limpa a tela e desenha todas as camadas na ordem: mapa, jogador e interface (hud).
        self.tela.fill((0, 0, 0))
        desenhar_mapa(self.tela, self.mundo, self.imagens)
        self.jogador.desenhar(self.tela)
        self._desenhar_nome()
        self._desenhar_vida()
        pygame.display.flip()

    def _desenhar_nome(self):
        # desenha uma etiqueta com o nome do andar atual no canto superior direito.
        texto = self.fonte.render(self.mundo.nome, True, (255, 255, 255))
        fundo = texto.get_rect(topright=(LARGURA - 8, 8)).inflate(12, 8)
        pygame.draw.rect(self.tela, (0, 0, 0), fundo)
        self.tela.blit(texto, texto.get_rect(center=fundo.center))

    def _desenhar_vida(self):
        # desenha os 3 corações no canto superior esquerdo (cheio, meio ou vazio).
        for i in range(3):
            x = 12 + i * 32
            y = 12

            if self.jogador.vida >= i + 1:
                # coração inteiro (quadrado vermelho).
                pygame.draw.rect(self.tela, (220, 40, 60), (x, y, 24, 24))
            elif self.jogador.vida >= i + 0.5:
                # meio coração (fundo escuro com metade esquerda vermelha).
                pygame.draw.rect(self.tela, (60, 40, 45), (x, y, 24, 24))
                pygame.draw.rect(self.tela, (220, 40, 60), (x, y, 12, 24))
            else:
                # coração vazio (quadrado escuro).
                pygame.draw.rect(self.tela, (60, 40, 45), (x, y, 24, 24))