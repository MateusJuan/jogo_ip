import pygame

from jogo.configuracoes import TAMANHO_CELULA, VELOCIDADE
from jogo.mapa import identificando_buraco, pode_andar


def criar_jogador(grade_x, grade_y, imagem):
    # cria o dicionário com todo o estado do personagem (posição, vida, tempos e histórico).
    return {
        # posição lógica na matriz (0 a 16).
        "grade_x": grade_x,
        "grade_y": grade_y,
        "imagem": imagem,
        # posição visual em pixels na tela (permite deslize suave entre células).
        "x": float(grade_x * TAMANHO_CELULA),
        "y": float(grade_y * TAMANHO_CELULA),
        # célula para onde o personagem está caminhando no momento.
        "destino_x": grade_x,
        "destino_y": grade_y,
        "em_movimento": False,
        # sistema de vida (3 corações, permitindo frações de 0.5).
        "vida_max": 3.0,
        "vida": 3.0,
        # cronômetros em segundos para piscar (invulnerável) e travar movimento (parado).
        "tempo_invulneravel": 0.0,
        "tempo_parado": 0.0,
        # lista que guarda as últimas células seguras pisadas (para voltar antes da beirada).
        "passos_seguros": [(grade_x, grade_y)],
    }


def definir_posicao_jogador(jogador, grade_x, grade_y):
    # teletransporta o jogador imediatamente para a célula (grade_x, grade_y).
    jogador["grade_x"] = grade_x
    jogador["grade_y"] = grade_y
    jogador["destino_x"] = grade_x
    jogador["destino_y"] = grade_y
    jogador["x"] = float(grade_x * TAMANHO_CELULA)
    jogador["y"] = float(grade_y * TAMANHO_CELULA)
    jogador["em_movimento"] = False


def levar_dano(jogador, quantidade):
    # desconta vida caso o jogador não esteja invulnerável e ativa o tempo de proteção.
    if jogador["tempo_invulneravel"] <= 0.0:
        jogador["vida"] = jogador["vida"] - quantidade
        if jogador["vida"] <= 0:
            jogador["vida"] = 0
        else:
            jogador["tempo_invulneravel"] = 1.2
            jogador["tempo_parado"] = 0.5
        return True
    return False


def atualizar_jogador(jogador, dt, teclas, mundo):
    # atualiza o deslize do personagem quadro a quadro usando 'dt' (tempo decorrido).
    restante = dt
    # variável booleana de controle para encerrar o while sem usar 'break' ou 'continue'.
    continuar_loop = True

    while restante > 0 and continuar_loop:
        pode_mover = True

        # se estiver parado em uma célula, lê o teclado para iniciar o próximo passo.
        if not jogador["em_movimento"]:
            dx, dy = _direcao(teclas)
            if not _comecar_passo(jogador, dx, dy, mundo):
                continuar_loop = False
                pode_mover = False

        # se houver um passo ativo, desloca os pixels na direção da célula de destino.
        if pode_mover:
            alvo_x = jogador["destino_x"] * TAMANHO_CELULA
            alvo_y = jogador["destino_y"] * TAMANHO_CELULA
            diferenca_x = alvo_x - jogador["x"]
            diferenca_y = alvo_y - jogador["y"]
            distancia = (diferenca_x ** 2 + diferenca_y ** 2) ** 0.5

            if distancia == 0:
                _chegar(jogador, mundo)
            else:
                passo = VELOCIDADE * restante
                if distancia <= passo:
                    # alcançou ou ultrapassou o centro da célula de destino neste quadro.
                    jogador["x"] = float(alvo_x)
                    jogador["y"] = float(alvo_y)
                    _chegar(jogador, mundo)
                    restante -= distancia / VELOCIDADE
                else:
                    # ainda está no meio do caminho: avança proporcionalmente.
                    proporcao = passo / distancia
                    jogador["x"] += diferenca_x * proporcao
                    jogador["y"] += diferenca_y * proporcao
                    restante = 0

    # desconta o tempo dos cronômetros de invulnerabilidade e paralisação.
    jogador["tempo_invulneravel"] -= dt / 1.5
    jogador["tempo_parado"] -= dt
    if jogador["tempo_invulneravel"] < 0:
        jogador["tempo_invulneravel"] = 0.0
    if jogador["tempo_parado"] < 0:
        jogador["tempo_parado"] = 0.0


def desenhar_jogador(jogador, tela):
    # desenha o personagem na tela, alternando a visibilidade para piscar quando invulnerável.
    if jogador["tempo_invulneravel"] <= 0 or int(jogador["tempo_invulneravel"] * 12) % 2 == 0:
        tela.blit(jogador["imagem"], (round(jogador["x"]), round(jogador["y"])))


def _direcao(teclas):
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


def _comecar_passo(jogador, dx, dy, mundo):
    # inicia o movimento para a célula vizinha se ela for caminhável e o jogador não estiver travado.
    if dx == 0 and dy == 0:
        return False

    proximo_x = jogador["grade_x"] + dx
    proximo_y = jogador["grade_y"] + dy
    if not pode_andar(mundo, proximo_x, proximo_y):
        return False
    if jogador["tempo_parado"] > 0:
        return False

    jogador["destino_x"] = proximo_x
    jogador["destino_y"] = proximo_y
    jogador["em_movimento"] = True
    return True


def _chegar(jogador, mundo):
    # executa quando o jogador termina de deslizar até a célula de destino.
    if not identificando_buraco(mundo, jogador["destino_x"], jogador["destino_y"]):
        # chão firme: atualiza a posição atual e registra no histórico de passos seguros.
        jogador["grade_x"] = jogador["destino_x"]
        jogador["grade_y"] = jogador["destino_y"]
        jogador["passos_seguros"].append((jogador["grade_x"], jogador["grade_y"]))
        jogador["em_movimento"] = False
    else:
        # caiu em buraco: aplica dano, congela por 1s e volta para antes da beirada (-2).
        levar_dano(jogador, 0.5)
        if len(jogador["passos_seguros"]) >= 2:
            destino_seguro = jogador["passos_seguros"][-2]
        else:
            destino_seguro = jogador["passos_seguros"][0]
        definir_posicao_jogador(jogador, destino_seguro[0], destino_seguro[1])
        jogador["passos_seguros"] = [destino_seguro]
        jogador["tempo_parado"] = 1.0
        jogador["em_movimento"] = False