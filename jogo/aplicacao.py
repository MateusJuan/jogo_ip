import pygame

from jogo.configuracoes import ALTURA, FPS, LARGURA, TAMANHO_MAPA, TITULO
from jogo.jogador import Jogador
from jogo.mapa import desenhar_mapa
from jogo.mundos import criar_mundos
from jogo.recursos import carregar_imagens


class Aplicacao:
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
        while self.rodando:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._eventos()
            self.jogador.atualizar(dt, pygame.key.get_pressed(), self.mundo)
            self._verificar_escada()
            self._desenhar()
        pygame.quit()

    def _eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

    def _verificar_escada(self):
        if self.jogador.em_movimento:
            return
        escada = self.mundo.escadas.get((self.jogador.grade_x, self.jogador.grade_y))
        if escada is None:
            return
        self.mundo = self.mundos[escada["destino"]]
        self.jogador.definir_posicao(escada["x"], escada["y"])

    def _desenhar(self):
        self.tela.fill((0, 0, 0))
        desenhar_mapa(self.tela, self.mundo, self.imagens)
        self.jogador.desenhar(self.tela)
        self._desenhar_nome()
        pygame.display.flip()

    def _desenhar_nome(self):
        texto = self.fonte.render(self.mundo.nome, True, (255, 255, 255))
        fundo = texto.get_rect(topleft=(8, 8)).inflate(12, 8)
        pygame.draw.rect(self.tela, (0, 0, 0), fundo)
        self.tela.blit(texto, (14, 12))
