import pygame

from jogo.configuracoes import TAMANHO_CELULA, VELOCIDADE
from jogo.mapa import identificando_buraco, pode_andar


class Jogador:
    # representa o personagem controlado pelo jogador, sua posição, vida e cronômetros.
    def __init__(
        self, grade_x, grade_y, imagem, imagem_costas, caminhada_direita,
        caminhada_esquerda, caminhada_costas, respiracao_direita, respiracao_esquerda,
        # --- NOVOS ARGUMENTOS PARA AS IMAGENS DE ATAQUE ---
        ataque_direita=None, ataque_esquerda=None, ataque_costas=None
    
    ):
        # posição lógica na matriz (0 a 16).
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.imagem = imagem
        self.imagem_esquerda = pygame.transform.flip(imagem, True, False)
        self.imagem_costas = imagem_costas
        self.caminhada_costas = caminhada_costas
        self.caminhada_direita = caminhada_direita
        self.caminhada_esquerda = caminhada_esquerda
        self.tempo_animacao = 0.0
        self.respiracao_direita = respiracao_direita
        self.respiracao_esquerda = respiracao_esquerda
        self.tempo_respiracao = 0.0
        self.direcao_olhar = (1, 0)
        # Lembra o lado do personagem tambem durante deslocamentos verticais.
        self.direcao_lateral = 1
        # posição visual em pixels na tela (permite deslize suave entre células).
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        # célula para onde o personagem está caminhando no momento.
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.em_movimento = False
        # Mantem a animacao no quadro em que o personagem termina um passo.
        self.movendo_neste_quadro = False
        # sistema de vida (3 corações, permitindo frações de 0.5).
        self.vida_max = 3.0
        self.vida = 3.0
        # cronômetros em segundos para piscar (invulnerável) e travar movimento (parado).
        self.tempo_invulneravel = 0.0
        self.tempo_parado = 0.0
        # lista que guarda as últimas células seguras pisadas (para voltar antes da beirada).
        self.passos_seguros = [(grade_x, grade_y)]
        self.game_over = False

        self.inventario = []

        # --- ATRIBUTOS DE ATAQUE ---
        self.tempo_cooldown_ataque = 0.0  # Tempo restante para o próximo ataque
        self.duracao_cooldown = 0.5      # Intervalo em segundos entre os ataques
        self.atacando = False             # Flag para indicar se está executando o ataque
        self.tempo_animacao_ataque = 0.5  # Para controlar animações de ataque futuras
        # ---------------------------------
        
        # --- IMAGENS DE ATAQUE BLINDADAS ---
        def _garantir_lista(val, padrao):
            if val is None:
                return [padrao]
            if isinstance(val, list):
                # Se for uma lista de listas, pega o primeiro elemento interno
                if len(val) > 0 and isinstance(val[0], list):
                    return val[0]
                return val
            return [val]

        self.ataque_direita = _garantir_lista(ataque_direita, imagem)
        self.ataque_esquerda = _garantir_lista(ataque_esquerda, self.imagem_esquerda)
        self.ataque_costas = _garantir_lista(ataque_costas, imagem_costas)
        self.tempo_animacao_ataque = 0.0

    def definir_posicao(self, grade_x, grade_y):
        # teletransporta o jogador imediatamente para a célula (grade_x, grade_y).
        self.grade_x = grade_x
        self.grade_y = grade_y
        self.destino_x = grade_x
        self.destino_y = grade_y
        self.x = float(grade_x * TAMANHO_CELULA)
        self.y = float(grade_y * TAMANHO_CELULA)
        self.em_movimento = False
        self.movendo_neste_quadro = False
        self.tempo_animacao = 0.0
        self.tempo_respiracao = 0.0

    def levar_dano(self, quantidade):
        # desconta vida caso o jogador não esteja invulnerável e ativa o tempo de proteção.
        if self.tempo_invulneravel <= 0.0:
            self.vida = self.vida - quantidade
            if self.vida <= 0:
                self.vida = 0
                self.game_over = True
            else:
                self.tempo_invulneravel = 1.2
                self.tempo_parado = 0.5
            return True
        return False

    def atualizar(self, dt, teclas, mundo):
        # atualiza o deslize do personagem quadro a quadro usando 'dt' (tempo decorrido).
        self.movendo_neste_quadro = False
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
                    self.movendo_neste_quadro = True
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

        if self.movendo_neste_quadro:
            self.tempo_animacao += dt
            self.tempo_respiracao = 0.0
        else:
            self.tempo_animacao = 0.0
            self.tempo_respiracao += dt

        # desconta o tempo dos cronômetros de invulnerabilidade e paralisação.
        self.tempo_invulneravel -= dt / 1.5
        self.tempo_parado -= dt / 1.5
        if self.tempo_invulneravel < 0:
            self.tempo_invulneravel = 0.0
        if self.tempo_parado < 0:
            self.tempo_parado = 0.0
        
        # --- ATUALIZAÇÃO DO COOLDOWN E ANIMAÇÃO DE ATAQUE ---
        if self.tempo_cooldown_ataque > 0:
            self.tempo_cooldown_ataque -= dt
            self.tempo_animacao_ataque += dt
            if self.tempo_cooldown_ataque <= 0:
                self.tempo_cooldown_ataque = 0.0
                self.atacando = False

    def desenhar(self, tela):
        # desenha o personagem na tela, alternando a visibilidade para piscar quando invulnerável.
        if self.tempo_invulneravel <= 0 or int(self.tempo_invulneravel * 12) % 2 == 0:
            
            # 1. Desenha o personagem 
            imagem = self.imagem if self.direcao_lateral == 1 else self.imagem_esquerda
            if self.movendo_neste_quadro and self.direcao_olhar == (0, -1):
                quadros = self.caminhada_costas
                imagem = quadros[int(self.tempo_animacao * 10) % len(quadros)]
            elif self.movendo_neste_quadro and self.direcao_olhar[0] != 0:
                quadros = self.caminhada_direita
                if self.direcao_olhar == (-1, 0):
                    quadros = self.caminhada_esquerda
                imagem = quadros[int(self.tempo_animacao * 10) % len(quadros)]
            elif self.direcao_olhar == (0, -1):
                imagem = self.imagem_costas
            elif not self.movendo_neste_quadro:
                quadros = self.respiracao_direita
                if self.direcao_lateral == -1:
                    quadros = self.respiracao_esquerda
                imagem = quadros[int(self.tempo_respiracao * 8) % len(quadros)]

            # Desenha a imagem na tela
            tela.blit(imagem, (round(self.x), round(self.y)))

            if self.atacando:
                dx, dy = self.direcao_olhar
                
                # Seleciona a imagem da espada de acordo com a direção do olhar
                if dx == 1:   # Direita
                    img_espada = self.ataque_direita[0] if isinstance(self.ataque_direita, list) else self.ataque_direita
                elif dx == -1: # Esquerda
                    img_espada = self.ataque_esquerda[0] if isinstance(self.ataque_esquerda, list) else self.ataque_esquerda
                elif dy == -1: # Cima / Costas
                    img_espada = self.ataque_costas[0] if isinstance(self.ataque_costas, list) else self.ataque_costas
                else:          # Baixo / Frente (usa a direita ou costas rotacionada, dependendo do seu setup)
                    img_espada = self.ataque_direita[0] if isinstance(self.ataque_direita, list) else self.ataque_direita

                # Calcula a posição exata 1 bloco (TAMANHO_CELULA) adiante na direção do olhar
                pos_espada_x = round(self.x + (dx * TAMANHO_CELULA))
                pos_espada_y = round(self.y + (dy * TAMANHO_CELULA))

                # Blita a espada na tela na célula da frente
                if isinstance(img_espada, pygame.Surface):
                    tela.blit(img_espada, (pos_espada_x, pos_espada_y))

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
        if self.tempo_parado > 0:
            return False

        # Vira mesmo diante de uma parede e mantem esse lado quando para.
        if self.direcao_olhar != (dx, dy):
            self.tempo_animacao = 0.0
            self.tempo_respiracao = 0.0
        self.direcao_olhar = (dx, dy)
        if dx != 0:
            self.direcao_lateral = dx

        proximo_x = self.grade_x + dx
        proximo_y = self.grade_y + dy
        if not pode_andar(mundo, proximo_x, proximo_y):
            self.movendo_neste_quadro = False
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
            self.tempo_parado = 1.2
            self.em_movimento = False

    def ataque(self):
        """
        Executa um ataque básico na célula adjacente para a qual o jogador está olhando.
        Retorna True se desferiu o golpe com sucesso (respeitando o cooldown).
        """
        if (
            "Espada" not in self.inventario
            or self.tempo_cooldown_ataque > 0.0
            or self.tempo_parado > 0
        ):
            return False

        # Ativa o cooldown e o estado de ataque
        self.tempo_cooldown_ataque = self.duracao_cooldown
        self.atacando = True

        # Calcula a posição da célula atingida com base na direção do olhar
        dx, dy = self.direcao_olhar
        celula_alvo_x = self.grade_x + dx
        celula_alvo_y = self.grade_y + dy

        return True
        # Exemplo de verificação de acerto em inimigos baseada em grade
    """ for inimigo in lista_inimigos:
            if inimigo.grade_x == celula_alvo_x and inimigo.grade_y == celula_alvo_y:
                # Supondo que o inimigo possua um método levar_dano ou similar
                if hasattr(inimigo, 'levar_dano'):
                    inimigo.levar_dano(1.0) # Aplica 1 de dano ao inimigo """

        
    
    