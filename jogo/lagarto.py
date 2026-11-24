from functools import lru_cache

import pygame

from jogo.configuracoes import ALTURA, LARGURA, TAMANHO_CELULA


DURACOES = {"preparacao": 1.2, "ataque": 0.8, "cooldown": 2.4}
INTERVALO_FOGO = 0.2
FOGOS_POR_RAJADA = 4


def criar_lagarto(grade_x, grade_y):
    return {
        "x": float(grade_x * TAMANHO_CELULA),
        "y": float(grade_y * TAMANHO_CELULA),
        "vida": 6, "vida_max": 6, "morto": False,
        "estado": "preparacao", "tempo_estado": 0.0,
        "direcao": (-1.0, 0.0), "mirando": False,
        "fogos_disparados": 0, "tempo_invulneravel": 0.0,
        "tempo_bloqueio": 0.0, "recompensa_criada": False,
    }


def retangulo_lagarto(lagarto):
    return pygame.Rect(round(lagarto["x"]), round(lagarto["y"]),
                       TAMANHO_CELULA, TAMANHO_CELULA)


def _mirar(lagarto, jogador):
    dx = jogador.x - lagarto["x"]
    dy = jogador.y - lagarto["y"]
    distancia = (dx * dx + dy * dy) ** 0.5
    if distancia > 0:
        lagarto["direcao"] = (dx / distancia, dy / distancia)
    lagarto["mirando"] = True


def atualizar_lagarto(lagarto, dt, jogador):
    # A mira fica fixa desde a preparacao, dando tempo para sair da linha de fogo.
    disparos = []
    if lagarto["morto"]:
        return disparos
    if not lagarto["mirando"]:
        _mirar(lagarto, jogador)
    lagarto["tempo_invulneravel"] = max(0.0, lagarto["tempo_invulneravel"] - dt)
    lagarto["tempo_bloqueio"] = max(0.0, lagarto["tempo_bloqueio"] - dt)
    restante = max(0.0, dt)
    while restante > 0:
        estado = lagarto["estado"]
        duracao = DURACOES[estado]
        passo = min(restante, duracao - lagarto["tempo_estado"])
        lagarto["tempo_estado"] += passo
        restante = max(0.0, restante - passo)
        if estado == "ataque":
            while (lagarto["fogos_disparados"] < FOGOS_POR_RAJADA
                   and lagarto["fogos_disparados"] * INTERVALO_FOGO
                   < lagarto["tempo_estado"] + 1e-9):
                disparos.append((lagarto["x"], lagarto["y"], lagarto["direcao"]))
                lagarto["fogos_disparados"] += 1
        if lagarto["tempo_estado"] >= duracao - 1e-9:
            lagarto["tempo_estado"] = 0.0
            if estado == "preparacao":
                lagarto["estado"] = "ataque"
                lagarto["fogos_disparados"] = 0
            elif estado == "ataque":
                lagarto["estado"] = "cooldown"
            else:
                lagarto["estado"] = "preparacao"
                _mirar(lagarto, jogador)
    return disparos


def ferir_lagarto(lagarto, quantidade, tipo_dano):
    if lagarto["morto"]:
        return False
    if lagarto["estado"] != "cooldown" or tipo_dano != "espada":
        lagarto["tempo_bloqueio"] = 0.35
        return False
    if lagarto["tempo_invulneravel"] > 0:
        return False
    lagarto["vida"] = max(0, lagarto["vida"] - quantidade)
    lagarto["tempo_invulneravel"] = 0.5
    if lagarto["vida"] == 0:
        lagarto["morto"] = True
        lagarto["estado"] = "morto"
        lagarto["tempo_estado"] = 0.0
    return True


def _desenhar_trajetoria(tela, centro, direcao, atacando, tempo):
    origem = pygame.Vector2(centro)
    rumo = pygame.Vector2(direcao)
    lateral = pygame.Vector2(-rumo.y, rumo.x)
    arena = pygame.Rect(TAMANHO_CELULA, TAMANHO_CELULA,
                        LARGURA - 2 * TAMANHO_CELULA, ALTURA - 2 * TAMANHO_CELULA)
    linha = arena.clipline(origem + rumo * 30, origem + rumo * (LARGURA + ALTURA))
    if not linha:
        return

    inicio, fim = linha
    sombra, cor = ((98, 38, 28), (255, 110, 53)) if atacando else ((87, 53, 34), (249, 180, 81))
    pygame.draw.line(tela, sombra, inicio, fim, 6)
    pygame.draw.line(tela, cor, inicio, fim, 2)
    distancia = 38 + int(tempo * 32) % 28
    alcance = origem.distance_to(fim) - 7
    while distancia < alcance:
        ponta = origem + rumo * distancia
        base = ponta - rumo * 7
        pygame.draw.lines(tela, cor, False, (base + lateral * 5, ponta, base - lateral * 5), 2)
        distancia += 28


@lru_cache(maxsize=3)
def _luz_lagarto(estado):
    cores = {"preparacao": (241, 144, 57), "ataque": (249, 109, 52), "cooldown": (136, 202, 162)}
    luz = pygame.Surface((48, 32), pygame.SRCALPHA)
    for margem, alpha in ((0, 12), (3, 19), (6, 27), (9, 35)):
        pygame.draw.ellipse(luz, (*cores[estado], alpha),
                            luz.get_rect().inflate(-2 * margem, -margem))
    return pygame.transform.scale(luz, (96, 64))


def desenhar_lagarto(tela, lagarto, imagens):
    if lagarto["morto"]:
        return
    area = retangulo_lagarto(lagarto)
    dx, dy = lagarto["direcao"]
    estado = lagarto["estado"]
    tempo = lagarto["tempo_estado"]
    luz = _luz_lagarto(estado)
    tela.blit(luz, luz.get_rect(center=(area.centerx, area.centery + 3)))
    if estado != "cooldown":
        _desenhar_trajetoria(tela, area.center, (dx, dy), estado == "ataque", tempo)

    sombra = pygame.Rect(0, 0, 52, 23)
    sombra.center = (area.centerx, area.centery + 8)
    pygame.draw.ellipse(tela, (25, 29, 33), sombra)

    if estado == "cooldown":
        pygame.draw.ellipse(tela, (65, 121, 107), sombra.inflate(6, 6), 2)
        pygame.draw.ellipse(tela, (151, 226, 185), sombra.inflate(2, 2), 2)

    if int(lagarto["tempo_invulneravel"] * 12) % 2 == 0:
        if abs(dx) >= abs(dy):
            direcao = (1 if dx > 0 else -1, 0)
        else:
            direcao = (0, 1 if dy > 0 else -1)
        imagem = imagens["lagarto"][estado][direcao]
        respiracao = 2 * (int(tempo * 6) % 2) if estado == "cooldown" else 0
        posicao = imagem.get_rect(midbottom=(area.centerx, area.centery + 21 - respiracao))
        tela.blit(imagem, posicao)

    if lagarto["tempo_bloqueio"] > 0:
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x = area.centerx + dx * 26
            y = area.centery + dy * 22
            pygame.draw.lines(tela, (255, 227, 142), False,
                              ((x - dx * 6, y), (x, y), (x, y - dy * 6)), 2)
