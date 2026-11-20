import pygame
import random
from .blocos import SOLIDOS

from jogo.configuracoes import (
    ALTURA, FPS, LARGURA, SLOTS_INVENTARIO,
    TAMANHO_CELULA, TAMANHO_MAPA, TITULO, ZOOM_CAMERA,
)
from jogo.jogador import Jogador
from jogo.mundos import criar_mundos
from jogo.recursos import carregar_imagens
from jogo.blocos import BAU_ABERTO, TORRE_ALTAR
from jogo.mapa import atualizar_porta, desenhar_mapa, obter_bau_proximo
from jogo.textos import carregar_fonte, renderizar_texto
from jogo.inimigos import inimigos
from jogo.audio import TrilhaSonora


TECLAS_MOVIMENTO = (
    pygame.K_w, pygame.K_UP,
    pygame.K_s, pygame.K_DOWN,
    pygame.K_a, pygame.K_LEFT,
    pygame.K_d, pygame.K_RIGHT,
)


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
        self.fonte = carregar_fonte(20)
        self.imagens = carregar_imagens()
        self.icones_inventario = {
            "Espada": pygame.transform.scale(self.imagens["ataque_direita"], (28, 28)),
        }
        self.mundos = criar_mundos()
        self.mundo = self.mundos["lobby"]
        self.trilha = TrilhaSonora()
        self.jogador = self._criar_jogador()
        self.rodando = True
        self.vitoria = False
        self.mensagem_bau = ""
        self.tempo_mensage = 0.0
        self.opcao_game_over = 0
        self.fonte_titulo = carregar_fonte(52, negrito=True)
        self.fonte_opcao = carregar_fonte(28, negrito=True)
        self.fonte_tutorial = carregar_fonte(20)
        self.fonte_tutorial_rotulo = carregar_fonte(16, negrito=True)
        self.fonte_tutorial_destaque = carregar_fonte(20, negrito=True)
        self.fonte_tutorial_titulo = carregar_fonte(28, negrito=True)
        self.tutorial_aberto = False
        self.inventario_aberto = False
        self.historico_teclas = []

    def _criar_jogador(self):
        return Jogador(
            TAMANHO_MAPA // 2, TAMANHO_MAPA - 3,
            self.imagens["personagem"], self.imagens["personagem_costas"],
            self.imagens["caminhada_direita"], self.imagens["caminhada_esquerda"],
            self.imagens["caminhada_costas"], self.imagens["caminhada_frente"],
            self.imagens["respiracao_direita"],
            self.imagens["respiracao_esquerda"],
            ataque_direita=self.imagens["ataque_direita"],
            ataque_esquerda=self.imagens["ataque_esquerda"],
            ataque_costas=self.imagens["ataque_costas"],
        )

    def executar(self):
        self.trilha.tocar_mapa(self.mundo.ident)

        # loop principal do jogo: processa eventos, atualiza a lógica e redesenha a tela a cada quadro.
        while self.rodando:
            # o dt (delta time) mede o tempo em segundos desde o último quadro (limitado a 0.05s).
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._eventos()
            if not (self.vitoria or self.jogador.game_over or self._tutorial_visivel()
                    or self.inventario_aberto):
                # atualiza as plataformas moveis antes do jogador para sincronizar a carona.
                for plataforma in self.mundo.plataformas:
                    plataforma.atualizar(dt, self.jogador)

                self.jogador.atualizar(
                    dt, pygame.key.get_pressed(), self.mundo, self.historico_teclas
                )
                atualizar_porta(self.mundo, self.jogador, dt)

                for inimigo in self.mundo.inimigos:
                    inimigo.atualizar(dt, self.mundo)
                    if not inimigo.morto and (inimigo.grade_x, inimigo.grade_y) == (self.jogador.grade_x, self.jogador.grade_y):
                        self.jogador.levar_dano(1.0)

                self._verificar_escada()
            if self.jogador.game_over:
                self.trilha.parar()
            self.trilha.atualizar(dt)
            self._desenhar()
            if self.tempo_mensage > 0 and not self._tutorial_visivel() and not self.inventario_aberto:
                self.tempo_mensage -= dt
                if self.tempo_mensage <= 0:
                    self.mensagem_bau = ""
        self.trilha.encerrar()
        pygame.quit()

    def _eventos(self):
        # verifica os eventos da janela e a navegação no menu de game over.
        for evento in pygame.event.get():
            if evento.type == pygame.KEYDOWN and evento.key in TECLAS_MOVIMENTO:
                if evento.key in self.historico_teclas:
                    self.historico_teclas.remove(evento.key)
                self.historico_teclas.append(evento.key)
            elif evento.type == pygame.KEYUP and evento.key in TECLAS_MOVIMENTO:
                if evento.key in self.historico_teclas:
                    self.historico_teclas.remove(evento.key)

            if evento.type == pygame.QUIT:
                self.rodando = False
            elif self.vitoria:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        self._reiniciar()
                    elif evento.key == pygame.K_ESCAPE:
                        self.rodando = False
            elif evento.type == pygame.KEYDOWN and self.jogador.game_over:
                if evento.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    # alterna entre 0 (restart) e 1 (quit).
                    self.opcao_game_over = 1 - self.opcao_game_over
                elif evento.key == pygame.K_RETURN:
                    if self.opcao_game_over == 0:
                        self._reiniciar()
                    else:
                        self.rodando = False
            elif evento.type == pygame.MOUSEWHEEL:
                if not self.jogador.game_over and not self._tutorial_visivel():
                    self.jogador.slot_selecionado = (
                        self.jogador.slot_selecionado - evento.y
                    ) % SLOTS_INVENTARIO
            elif evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_h and self.mundo.ident == "lobby" and not self.inventario_aberto:
                    self.tutorial_aberto = not self.tutorial_aberto

                elif self._tutorial_visivel():
                    if evento.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        self.tutorial_aberto = False

                elif evento.key == pygame.K_e:
                    self.inventario_aberto = not self.inventario_aberto

                elif pygame.K_1 <= evento.key < pygame.K_1 + SLOTS_INVENTARIO:
                    self.jogador.slot_selecionado = evento.key - pygame.K_1

                elif self.inventario_aberto:
                    if evento.key == pygame.K_ESCAPE:
                        self.inventario_aberto = False

                elif evento.key == pygame.K_f:
                    if self._perto_do_altar():
                        self.vitoria = True
                        self.trilha.parar()
                    else:
                        self._interagir_bau()

                elif evento.key == pygame.K_SPACE:
                    self.jogador.ataque(self.mundo.inimigos)

                elif evento.key == pygame.K_SPACE:
                    self.jogador.ataque(self.mundo.inimigos)

    def _tutorial_visivel(self):
        return self.tutorial_aberto and self.mundo.ident == "lobby" and not self.jogador.game_over

    def _perto_do_altar(self):
        if self.mundo.ident != "torre" or self.jogador.em_movimento:
            return False
        x, y = self.jogador.grade_x, self.jogador.grade_y
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            coluna, linha = x + dx, y + dy
            if 0 <= coluna < TAMANHO_MAPA and 0 <= linha < TAMANHO_MAPA:
                if self.mundo.grade[linha][coluna] == TORRE_ALTAR:
                    return True
        return False

    def _interagir_bau(self):
        pos_bau = obter_bau_proximo(self.mundo, self.jogador)
        if not pos_bau:
            return
        bx, by = pos_bau
        itens = self.mundo.baus[pos_bau]
        self.tempo_mensage = 4.0
        if len(self.jogador.inventario) + len(itens) > SLOTS_INVENTARIO:
            self.mensagem_bau = "Inventário cheio!"
            return

        self.mundo.grade[by][bx] = BAU_ABERTO
        self.jogador.inventario.extend(itens)
        if "Espada" in itens:
            self.mensagem_bau = "Espada obtida! Pressione Espaço para atacar."
        else:
            texto_itens = ", ".join(itens) if itens else "vazio"
            self.mensagem_bau = f"Baú aberto! Você encontrou: {texto_itens}"

    def _verificar_escada(self):
        # troca de andar caso o personagem tenha parado exatamente sobre uma célula de escada.
        if self.jogador.em_movimento:
            return
        posicao = (self.jogador.grade_x, self.jogador.grade_y)
        if posicao not in self.mundo.escadas:
            return
        escada = self.mundo.escadas[posicao]
        destino = self.mundos.get(escada["destino"])
        if destino is None:
            return
        if self.mundo.ident == "lobby":
            self.mundo.abertura_porta = 0.0
        self.mundo = destino
        self.trilha.tocar_mapa(self.mundo.ident)
        self.jogador.definir_posicao(escada["x"], escada["y"])
        self.tutorial_aberto = False

    def _reiniciar(self):
        # recria os andares e reposiciona o jogador no centro do lobby com vida cheia.
        self.mundos = criar_mundos()
        self.mundo = self.mundos["lobby"]
        self.jogador = self._criar_jogador()
        self.vitoria = False
        self.mensagem_bau = ""
        self.tempo_mensage = 0.0
        self.opcao_game_over = 0
        self.tutorial_aberto = False
        self.inventario_aberto = False
        self.historico_teclas.clear()
        self.trilha.tocar_mapa(self.mundo.ident, reiniciar=True)

    def _desenhar(self):
        if self.vitoria:
            self._desenhar_creditos()
            pygame.display.flip()
            return

        # limpa a tela e desenha todas as camadas na ordem: mapa, jogador e interface (hud).
        self.cena.fill((0, 0, 0))
        desenhar_mapa(self.cena, self.mundo, self.imagens)
        for inimigo in self.mundo.inimigos:
            inimigo.desenhar(self.cena, self.imagens["esqueleto"])
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
        self._desenhar_contador_inimigos()
        self._desenhar_inventario()
        self._desenhar_mensagem_bau()
        if not self.jogador.game_over:
            if self._tutorial_visivel():
                self._desenhar_tutorial()
            elif self.inventario_aberto:
                self._desenhar_inventario_expandido()
            else:
                self._desenhar_ajuda()
                self._desenhar_dica_interacao()
        if self.jogador.game_over:
            self._desenhar_game_over()
        pygame.display.flip()

    def _desenhar_ajuda(self):
        if self.mundo.ident == "lobby":
            texto = renderizar_texto(self.fonte_tutorial, "[H] Tutorial", (238, 215, 165))
            fundo = texto.get_rect(topleft=(22, 58)).inflate(20, 12)
            pygame.draw.rect(self.tela, (24, 23, 29), fundo)
            pygame.draw.rect(self.tela, (111, 96, 65), fundo, 2)
            self.tela.blit(texto, texto.get_rect(center=fundo.center))

    def _desenhar_dica_interacao(self):
        if self.jogador.em_movimento:
            return
        if self._perto_do_altar():
            dica = "[F] Ativar altar"
        elif obter_bau_proximo(self.mundo, self.jogador):
            dica = "[F] Abrir baú"
        else:
            return
        texto = renderizar_texto(self.fonte, dica, (255, 224, 148))
        fundo = texto.get_rect(center=(LARGURA // 2, ALTURA - 82)).inflate(28, 16)
        pygame.draw.rect(self.tela, (24, 23, 29), fundo)
        pygame.draw.rect(self.tela, (155, 120, 66), fundo, 2)
        self.tela.blit(texto, texto.get_rect(center=fundo.center))

    def _desenhar_creditos(self):
        self.tela.fill((17, 17, 22))
        painel = self.tela.get_rect().inflate(-64, -64)
        centro = painel.centerx
        ouro = (224, 183, 108)
        claro = (248, 238, 216)
        pygame.draw.rect(self.tela, (28, 27, 32), painel)
        pygame.draw.rect(self.tela, (115, 96, 66), painel, 2)
        pygame.draw.rect(self.tela, (60, 53, 48), painel.inflate(-12, -12), 1)

        for y in (224, 546):
            pygame.draw.line(self.tela, (115, 96, 66), (centro - 200, y), (centro + 200, y), 2)
            pygame.draw.polygon(self.tela, ouro, (
                (centro, y - 6), (centro + 6, y), (centro, y + 6), (centro - 6, y),
            ))

        linhas = (
            (self.fonte_titulo, "Vitória!", ouro, 112),
            (self.fonte, TITULO, claro, 166),
            (self.fonte_opcao, "Créditos finais", ouro, 266),
            (self.fonte, "Cadeira: Introdução à Programação", claro, 304),
            (self.fonte, "Matehus Mesquita", claro, 350),
            (self.fonte, "Felipe Manoel", claro, 380),
            (self.fonte, "Karllos Braga", claro, 410),
            (self.fonte, "Mateus Juan", claro, 440),
            (self.fonte, "Rodrigo Negreiros", claro, 470),
            (self.fonte, "Thalisson Matias", claro, 500),
            (self.fonte, "Trilha sonora escrita por matewx_j", claro, 578),
            (self.fonte, "[Enter] Jogar novamente     [Esc] Sair", ouro, 620),
        )
        for fonte, mensagem, cor, y in linhas:
            texto = renderizar_texto(fonte, mensagem, cor)
            self.tela.blit(texto, texto.get_rect(center=(centro, y)))
        if obter_bau_proximo(self.mundo, self.jogador):
            texto = renderizar_texto(self.fonte, "[F] Abrir baú", (255, 224, 148))
            fundo = texto.get_rect(center=(LARGURA // 2, ALTURA - 82)).inflate(28, 16)
            pygame.draw.rect(self.tela, (24, 23, 29), fundo)
            pygame.draw.rect(self.tela, (155, 120, 66), fundo, 2)
            self.tela.blit(texto, texto.get_rect(center=fundo.center))

    def _desenhar_tutorial(self):
        # Pausa a exploracao enquanto o jogador le as instrucoes da entrada.
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((7, 10, 16, 190))
        self.tela.blit(camada, (0, 0))
        painel = pygame.Rect(0, 0, 620, 652)
        painel.center = (LARGURA // 2, ALTURA // 2)
        # A moldura de pedra tambem e ampliada sem suavizacao, em pixels de 2x2.
        pedra = pygame.Surface((painel.width // 2, painel.height // 2), pygame.SRCALPHA)
        largura, altura = pedra.get_size()
        contorno = (
            (4, 0), (largura - 5, 0), (largura - 1, 4), (largura - 1, altura - 5),
            (largura - 5, altura - 1), (4, altura - 1), (0, altura - 5), (0, 4),
        )
        pygame.draw.polygon(pedra, (30, 33, 35), contorno)
        pygame.draw.polygon(pedra, (152, 126, 77), contorno, 2)
        pygame.draw.rect(pedra, (76, 73, 58), (5, 5, largura - 10, altura - 10), 1)
        for linha in range(12, altura - 12, 13):
            for coluna in range(12, largura - 12, 19):
                if (coluna + linha) % 3 == 0:
                    pygame.draw.rect(pedra, (34, 37, 38), (coluna, linha, 2, 1))
        self.tela.blit(pygame.transform.scale(pedra, painel.size), painel)
        x, y = painel.x + 24, painel.y
        rotulo = renderizar_texto(
            self.fonte_tutorial_rotulo, "INSCRIÇÕES DAS RUÍNAS  /  TUTORIAL", (210, 169, 99)
        )
        self.tela.blit(rotulo, (x, y + 22))
        titulo = renderizar_texto(self.fonte_tutorial_titulo, "Sabedoria das ruínas", (248, 238, 216))
        self.tela.blit(titulo, (x, y + 44))
        subtitulo = renderizar_texto(
            self.fonte_tutorial, "Um guia para explorar a masmorra.", (184, 184, 167)
        )
        self.tela.blit(subtitulo, (x, y + 80))

        instrucoes = (
            ("WASD", "Movimente-se", (
                "Use W, A, S, D ou as setas para andar.",
            )),
            ("VIDA", "Cuidado com os buracos", (
                "Você tem 3 corações. Cair tira meio",
                "coração e leva você a um ponto seguro.",
            )),
            ("DANO", "Observe o personagem", (
                "Após sofrer dano, você para um instante.",
                "Enquanto pisca, você fica protegido.",
            )),
            ("F", "Abra os baús", (
                "Ao lado do baú, pressione F para abrir.",
            )),
            ("ESPAÇO", "Ataque com a espada", (
                "Pegue a espada no baú da entrada.",
                "Com a espada selecionada, use Espaço.",
            )),
            ("E", "Abra o inventário", (
                "E abre e fecha o inventário ampliado.",
                "Use 1 a 5 ou a roda do mouse para selecionar.",
            )),
            ("SAÍDA", "Avance pela masmorra", (
                "Siga o caminho até o portão ao norte.",
                "Chegue perto para abrir e subir.",
            )),
        )
        for indice, (tecla, assunto, linhas) in enumerate(instrucoes):
            topo = y + 110 + indice * 66
            selo = pygame.Rect(x, topo + 4, 72, 32)
            pygame.draw.rect(self.tela, (47, 48, 44), selo)
            pygame.draw.rect(self.tela, (115, 103, 74), selo, 2)
            texto_tecla = renderizar_texto(self.fonte_tutorial_rotulo, tecla, (239, 207, 145))
            self.tela.blit(texto_tecla, texto_tecla.get_rect(center=selo.center))
            destaque = renderizar_texto(self.fonte_tutorial_destaque, assunto, (240, 232, 214))
            self.tela.blit(destaque, (x + 88, topo))
            for numero, linha in enumerate(linhas):
                texto = renderizar_texto(self.fonte_tutorial, linha, (198, 197, 178))
                self.tela.blit(texto, (x + 88, topo + 23 + numero * 20))

        pygame.draw.line(self.tela, (107, 96, 68), (x, y + 580), (painel.right - 24, y + 580), 2)
        botao = pygame.Rect(x, y + 600, 280, 44)
        pygame.draw.rect(self.tela, (211, 171, 103), botao)
        pygame.draw.rect(self.tela, (248, 216, 151), botao, 2)
        texto_botao = renderizar_texto(
            self.fonte_tutorial_destaque, "ENTER  Voltar ao jogo", (27, 26, 29)
        )
        self.tela.blit(texto_botao, texto_botao.get_rect(center=botao.center))
        atalho = renderizar_texto(self.fonte_tutorial, "[H] / [ESC] Fechar", (184, 184, 167))
        self.tela.blit(atalho, atalho.get_rect(midright=(painel.right - 24, botao.centery)))

    def _desenhar_nome(self):
        # desenha uma etiqueta com o nome do andar atual no canto superior direito.
        texto = renderizar_texto(self.fonte, self.mundo.nome, (238, 222, 182))
        fundo = texto.get_rect(topright=(LARGURA - 8, 8)).inflate(12, 8)
        pygame.draw.rect(self.tela, (0, 0, 0), fundo)
        self.tela.blit(texto, texto.get_rect(center=fundo.center))

    def _desenhar_contador_inimigos(self):
        if self.mundo.inimigos:
            restantes = sum(not inimigo.morto for inimigo in self.mundo.inimigos)
            contador = renderizar_texto(self.fonte, f"Inimigos restantes: {restantes}", (238, 222, 182))
            painel = contador.get_rect().inflate(12, 8)
            painel.topleft = (12, 50)
            pygame.draw.rect(self.tela, (0, 0, 0), painel)
            self.tela.blit(contador, contador.get_rect(center=painel.center))

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

    def _desenhar_inventario(self):
        tamanho = 40
        largura = SLOTS_INVENTARIO * (tamanho + 4) - 4
        self._desenhar_slots(LARGURA - 12 - largura, 46, tamanho, 4)

    def _desenhar_inventario_expandido(self):
        painel = self.tela.get_rect().inflate(-32, -32)
        pygame.draw.rect(self.tela, (24, 23, 29), painel)
        pygame.draw.rect(self.tela, (152, 126, 77), painel, 3)

        titulo = renderizar_texto(self.fonte_titulo, "Inventário", (248, 238, 216))
        self.tela.blit(titulo, titulo.get_rect(center=(painel.centerx, painel.top + 90)))
        tamanho = 96
        espaco = 14
        largura = SLOTS_INVENTARIO * (tamanho + espaco) - espaco
        self._desenhar_slots(painel.centerx - largura // 2, painel.centery - tamanho // 2,
                             tamanho, espaco, expandido=True)
        item = self.jogador.item_selecionado or "Slot vazio"
        nome = renderizar_texto(self.fonte_opcao, item, (248, 238, 216))
        self.tela.blit(nome, nome.get_rect(center=(painel.centerx, painel.centery + 90)))
        ajuda = renderizar_texto(
            self.fonte, "[E] / [Esc] Fechar    [1 a 5] / Roda do mouse Selecionar", (238, 215, 165)
        )
        self.tela.blit(ajuda, ajuda.get_rect(center=(painel.centerx, painel.bottom - 50)))

    def _desenhar_slots(self, x, y, tamanho, espaco, expandido=False):
        for indice in range(SLOTS_INVENTARIO):
            slot = pygame.Rect(x + indice * (tamanho + espaco), y, tamanho, tamanho)
            selecionado = indice == self.jogador.slot_selecionado
            fundo = (54, 45, 32) if selecionado else (32, 31, 37)
            borda = (248, 216, 151) if selecionado else (111, 96, 65)
            pygame.draw.rect(self.tela, fundo, slot)
            pygame.draw.rect(self.tela, borda, slot, 3 if selecionado else 2)
            if indice < len(self.jogador.inventario):
                item = self.jogador.inventario[indice]
                icone = self.icones_inventario.get(item)
                if icone is None:
                    icone = renderizar_texto(self.fonte, item[:1], (238, 215, 165))
                elif expandido:
                    icone = pygame.transform.scale(icone, (56, 56))
                self.tela.blit(icone, icone.get_rect(center=slot.center))
            if expandido:
                numero = renderizar_texto(self.fonte, str(indice + 1), borda)
                self.tela.blit(numero, (slot.x + 8, slot.y + 4))

    def _desenhar_mensagem_bau(self):
        if not self.mensagem_bau:
            return
        texto = renderizar_texto(self.fonte, self.mensagem_bau, (238, 222, 182))
        fundo = texto.get_rect(center=(LARGURA // 2, ALTURA - 32)).inflate(12, 8)
        pygame.draw.rect(self.tela, (0, 0, 0), fundo)
        self.tela.blit(texto, texto.get_rect(center=fundo.center))

    def _desenhar_game_over(self):
        # cria uma camada escura semitransparente por cima do jogo e desenha o menu de derrota.
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 185))
        self.tela.blit(camada, (0, 0))

        titulo = renderizar_texto(self.fonte_titulo, "GAME OVER", (220, 40, 60))
        retangulo_titulo = titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 60))
        self.tela.blit(titulo, retangulo_titulo)

        opcoes = ["Restart", "Quit"]
        for indice, texto_opcao in enumerate(opcoes):
            # destaca em amarelo a opção selecionada no momento.
            if indice == self.opcao_game_over:
                cor = (255, 220, 90)
                rotulo = "> " + texto_opcao + " <"
            else:
                cor = (180, 180, 180)
                rotulo = texto_opcao

            superficie = renderizar_texto(self.fonte_opcao, rotulo, cor)
            retangulo = superficie.get_rect(center=(LARGURA // 2, ALTURA // 2 + 15 + indice * 44))
            self.tela.blit(superficie, retangulo)
            
def atualizar_inimigos(mundo):
    if not hasattr(mundo, "inimigos"):
        return
        
    for inimigo in mundo.inimigos:
        inimigo["tempo"] += 1
        # A cada ~60 frames (1 segundo), o inimigo tenta mover-se
        if inimigo["tempo"] > 60:
            inimigo["tempo"] = 0
            # Escolhe uma direção aleatória (cima, baixo, esquerda, direita)
            direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            dx, dy = random.choice(direcoes)
            
            novo_x = inimigo["x"] + dx
            novo_y = inimigo["y"] + dy
            
            # Verifica se a célula de destino é caminhável (não é parede nem entulho)
            if 0 <= novo_x < TAMANHO_MAPA and 0 <= novo_y < TAMANHO_MAPA:
                if mundo.grade[novo_y][novo_x] not in SOLIDOS:
                    inimigo["x"] = novo_x
                    inimigo["y"] = novo_y
