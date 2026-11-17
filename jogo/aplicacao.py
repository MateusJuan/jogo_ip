import pygame

from jogo.configuracoes import (
    ALTURA, FPS, LARGURA, TAMANHO_CELULA, TAMANHO_MAPA, TITULO, ZOOM_CAMERA,
)
from jogo.jogador import Jogador
from jogo.mapa import atualizar_porta, desenhar_mapa
from jogo.mundos import criar_mundos
from jogo.recursos import carregar_imagens
from jogo.blocos import BAU_ABERTO, BAU_FECHADO
from jogo.mapa import atualizar_porta, desenhar_mapa, obter_bau_proximo


class Aplicacao:
    # gerencia a janela do pygame, o loop principal, as trocas de andar e o desenho do hud.
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        tamanho_mundo = TAMANHO_MAPA * TAMANHO_CELULA
        self.cena = pygame.Surface((tamanho_mundo, tamanho_mundo)).convert()
        self.camera = pygame.Rect(0, 0, LARGURA // ZOOM_CAMERA, ALTURA // ZOOM_CAMERA)
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont("arial", 20)
        self.imagens = carregar_imagens()
        self.mundos = criar_mundos()
        self.mundo = self.mundos["lobby"]
        centro = TAMANHO_MAPA // 2
        self.jogador = Jogador(
            centro, TAMANHO_MAPA - 3, self.imagens["personagem"], self.imagens["personagem_costas"],
            self.imagens["caminhada_direita"], self.imagens["caminhada_esquerda"],
            self.imagens["caminhada_frente"], self.imagens["respiracao_direita"]
        )
        self.rodando = True
        self.mensagem_bau = ""
        self.tempo_mensage = 0.0

    def executar(self):
        # loop principal do jogo: processa eventos, atualiza a lógica e redesenha a tela a cada quadro.
        while self.rodando:
            # o dt (delta time) mede o tempo em segundos desde o último quadro (limitado a 0.05s).
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._eventos()
            atualizar_porta(self.mundo, self.jogador, dt)
            self.jogador.atualizar(dt, pygame.key.get_pressed(), self.mundo)
            self._verificar_escada()
            self._desenhar()
            if self.tempo_mensage > 0:
                self.tempo_mensage -= dt
                if self.tempo_ensagem <= 0:
                    self.mensaagem_bau = ""
        pygame.quit()

    def _eventos(self):
        # verifica os eventos da janela (como clicar no botão x para fechar o jogo).
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_f:
                self._interagir_bau()
    def _interagir_bau(self):
        pos_bau = obter_bau_proximo(self.mundo, self.jogador)
        if not pos_bau:
            return
        bx, by = pos_bau
        #abre o baú
        self.mundo.grade[by][bx] = BAU_ABERTO
        itens = self.mundo.baus.get[pos_bau]
        texto_itens = ", ".join(itens) if itens else "vazio"
        self.mensagem_bau = f"Baú aberto! Você encontrou: {texto_itens}"
        self.tempo_mensage = 4.0 #deixa visivle por 4 segundos
    
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
        self.cena.fill((0, 0, 0))
        desenhar_mapa(self.cena, self.mundo, self.imagens)
        self.jogador.desenhar(self.cena)

        # acompanha o centro do personagem e limita a camera nas bordas do mapa.
        self.camera.center = (
            round(self.jogador.x + TAMANHO_CELULA / 2),
            round(self.jogador.y + TAMANHO_CELULA / 2),
        )
        self.camera.clamp_ip(self.cena.get_rect())
        pygame.transform.scale(
            self.cena.subsurface(self.camera), self.tela.get_size(), self.tela
        )
        self._desenhar_nome()
        self._desenhar_vida()
        self._desenhar_mensagem_bau()
        pygame.display.flip()

    def _desenhar_nome(self):
        # desenha uma etiqueta com o nome do andar atual no canto superior direito.
        texto = self.fonte.render(self.mundo.nome, True, (255, 255, 255))
        fundo = texto.get_rect(topright=(LARGURA - 8, 8)).inflate(12, 8)
        pygame.draw.rect(self.tela, (0, 0, 0), fundo)
        self.tela.blit(texto, texto.get_rect(center=fundo.center))

    def _desenhar_vida(self):
        # Cada caractere representa um pixel de 3x3, sem suavizacao.
        desenho = (
            "..###.###..",
            ".#rrr#rrr#.",
            "#rHHrrrrrr#",
            "#rHrrrrrrr#",
            "#rrrrrrrrr#",
            ".#rrrrrrr#.",
            "..#rsssr#..",
            "...#sss#...",
            "....#s#....",
            ".....#.....",
        )
        cores = {
            "#": (28, 15, 27),
            "r": (230, 48, 73),
            "H": (255, 158, 164),
            "s": (163, 28, 55),
        }
        tamanho_pixel = 3
        for i in range(int(self.jogador.vida_max)):
            preenchimento = max(0.0, min(1.0, self.jogador.vida - i))
            x = 12 + i * 39
            for linha, pixels in enumerate(desenho):
                for coluna, pixel in enumerate(pixels):
                    if pixel != ".":
                        cor = cores[pixel]
                        if pixel != "#" and coluna >= len(pixels) * preenchimento:
                            cor = (65, 43, 56) if pixel != "s" else (45, 29, 40)
                        pygame.draw.rect(
                            self.tela, cor,
                            (x + coluna * tamanho_pixel, 12 + linha * tamanho_pixel,
                             tamanho_pixel, tamanho_pixel),
                        )
    def _desenhar_mensagem_bau(self):
        if not self.mensagem_bau:
            return
        texto = self.fonte.render(self.mensagem_bau, True, (255, 255, 255))
        fundo = texto.get_rect(center=(LARGURA // 2, ALTURA - 32)).inflate(12, 8)
        pygame.draw.rect(self.tela, (0, 0, 0), fundo)
        self.tela.blit(texto, texto.get_rect(center=fundo.center))