import pygame

from jogo.configuracoes import TAMANHO_CELULA, VELOCIDADE
from jogo.mapa import identificando_buraco, pode_andar


class Jogador:
    # representa o personagem controlado pelo jogador, sua posição, vida e cronômetros.
    def __init__(self, grade_x, grade_y, imagem, imagem_costas):
        # posição lógica na matriz (0 a 16).
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.imagem = imagem
        self.imagem_costas = imagem_costas
        # posição visual em pixels na tela (permite deslize suave entre células).
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        # célula para onde o personagem está caminhando no momento.
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.em_movimento = False
        # sistema de vida (3 corações, permitindo frações de 0.5).
        self.vida_max = 3.0
        self.vida = 3.0
        # cronômetros em segundos para piscar (invulnerável) e travar movimento (parado).
        self.tempo_invulneravel = 0.0
        self.tempo_parado = 0.0
        # lista que guarda as últimas células seguras pisadas (para voltar antes da beirada).
        self.passos_seguros = [(grade_x, grade_y)]

    def definir_posicao(self, grade_x, grade_y):
        # teletransporta o jogador imediatamente para a célula (grade_x, grade_y).
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        self.em_movimento = False

    def levar_dano(self, quantidade):
        # desconta vida caso o jogador não esteja invulnerável e ativa o tempo de proteção.
        if self.tempo_invulneravel <= 0.0:
            self.vida = self.vida - quantidade
            if self.vida <= 0:
                self.vida = 0
            else:
                self.tempo_invulneravel = 1.2
                self.tempo_parado = 0.5
            return True
        return False

    def atualizar(self, dt, teclas, mundo):
        # atualiza o deslize do personagem quadro a quadro usando 'dt' (tempo decorrido).
        restante = dt
        # variável booleana de controle para encerrar o while sem usar 'break' ou 'continue'.
        continuar_loop = True

        while restante > 0 and continuar_loop:
            pode_mover = True

            # se estiver parado em uma célula, lê o teclado para iniciar o próximo passo.
            if not self.em_movimento:
                dx, dy = self._direcao(teclas)
                if not self._comecar_passo(dx, dy, mundo):
                    continuar_loop = False
                    pode_mover = False

            # se houver um passo ativo, desloca os pixels na direção da célula de destino.
            if pode_mover:
                alvo_x = self.destino_x * TAMANHO_CELULA
                alvo_y = self.destino_y * TAMANHO_CELULA
                diferenca_x = alvo_x - self.x
                diferenca_y = alvo_y - self.y
                distancia = (diferenca_x ** 2 + diferenca_y ** 2) ** 0.5

                if distancia == 0:
                    self._chegar(mundo)
                else:
                    passo = VELOCIDADE * restante
                    if distancia <= passo:
                        # alcançou ou ultrapassou o centro da célula de destino neste quadro.
                        self.x = float(alvo_x)
                        self.y = float(alvo_y)
                        self._chegar(mundo)
                        restante -= distancia / VELOCIDADE
                    else:
                        # ainda está no meio do caminho: avança proporcionalmente.
                        proporcao = passo / distancia
                        self.x += diferenca_x * proporcao
                        self.y += diferenca_y * proporcao
                        restante = 0

        # desconta o tempo dos cronômetros de invulnerabilidade e paralisação.
        self.tempo_invulneravel -= dt / 1.5
        self.tempo_parado -= dt
        if self.tempo_invulneravel < 0:
            self.tempo_invulneravel = 0.0
        if self.tempo_parado < 0:
            self.tempo_parado = 0.0

    def desenhar(self, tela):
        # desenha o personagem na tela, alternando a visibilidade para piscar quando invulnerável.
        if self.tempo_invulneravel <= 0 or int(self.tempo_invulneravel * 12) % 2 == 0:
            imagem = self.imagem
            if self.em_movimento and self.destino_y < self.grade_y:
                imagem = self.imagem_costas
            tela.blit(imagem, (round(self.x), round(self.y)))

    def _direcao(self, teclas):
        # converte as teclas wasd ou setas direcionais em deslocamento (dx, dy) na grade.
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
        # inicia o movimento para a célula vizinha se ela for caminhável e o jogador não estiver travado.
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
        # executa quando o jogador termina de deslizar até a célula de destino.
        if not identificando_buraco(mundo, self.destino_x, self.destino_y):
            # chão firme: atualiza a posição atual e registra no histórico de passos seguros.
            self.grade_x = self.destino_x
            self.grade_y = self.destino_y
            self.passos_seguros.append((self.grade_x, self.grade_y))
            self.em_movimento = False
        else:
            # caiu em buraco: aplica dano, congela por 1s e volta para antes da beirada (-2).
            self.levar_dano(0.5)
            if len(self.passos_seguros) >= 2:
                destino_seguro = self.passos_seguros[-2]
            else:
                destino_seguro = self.passos_seguros[0]
            self.definir_posicao(destino_seguro[0], destino_seguro[1])
            self.passos_seguros = [destino_seguro]
            self.tempo_parado = 1.0
            self.em_movimento = False
