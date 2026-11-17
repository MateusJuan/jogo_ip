import pygame

from jogo.configuracoes import ALTURA, FPS, LARGURA, TAMANHO_MAPA, TITULO
from jogo.jogador import (
    atualizar_jogador,
    criar_jogador,
    definir_posicao_jogador,
    desenhar_jogador,
)
from jogo.mapa import desenhar_mapa
from jogo.mundos import criar_mundos
from jogo.recursos import carregar_imagens


def criar_aplicacao():
    # inicializa o pygame, cria a janela e monta o estado inicial completo do jogo.
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption(TITULO)
    clock = pygame.time.Clock()
    fonte = pygame.font.SysFont("arial", 20)
    imagens = carregar_imagens()
    mundos = criar_mundos()
    mundo = mundos["lobby"]
    centro = TAMANHO_MAPA // 2
    jogador = criar_jogador(centro, centro, imagens["personagem"])

    return {
        "tela": tela,
        "clock": clock,
        "fonte": fonte,
        "imagens": imagens,
        "mundos": mundos,
        "mundo": mundo,
        "jogador": jogador,
        "rodando": True,
    }


def executar_aplicacao():
    # loop principal do jogo: processa eventos, atualiza a lógica e redesenha a tela a cada quadro.
    app = criar_aplicacao()
    while app["rodando"]:
        # o dt (delta time) mede o tempo em segundos desde o último quadro (limitado a 0.05s).
        dt = min(app["clock"].tick(FPS) / 1000.0, 0.05)
        _eventos(app)
        atualizar_jogador(app["jogador"], dt, pygame.key.get_pressed(), app["mundo"])
        _verificar_escada(app)
        _desenhar(app)
    pygame.quit()


def _eventos(app):
    # verifica os eventos da janela (como clicar no botão x para fechar o jogo).
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            app["rodando"] = False


def _verificar_escada(app):
    # troca de andar caso o personagem tenha parado exatamente sobre uma célula de escada.
    if app["jogador"]["em_movimento"]:
        return
    posicao = (app["jogador"]["grade_x"], app["jogador"]["grade_y"])
    if posicao not in app["mundo"]["escadas"]:
        return
    escada = app["mundo"]["escadas"][posicao]
    app["mundo"] = app["mundos"][escada["destino"]]
    definir_posicao_jogador(app["jogador"], escada["x"], escada["y"])


def _desenhar(app):
    # limpa a tela e desenha todas as camadas na ordem: mapa, jogador e interface (hud).
    app["tela"].fill((0, 0, 0))
    desenhar_mapa(app["tela"], app["mundo"], app["imagens"])
    desenhar_jogador(app["jogador"], app["tela"])
    _desenhar_nome(app)
    _desenhar_vida(app)
    pygame.display.flip()


def _desenhar_nome(app):
    # desenha uma etiqueta com o nome do andar atual no canto superior direito.
    texto = app["fonte"].render(app["mundo"]["nome"], True, (255, 255, 255))
    fundo = texto.get_rect(topright=(LARGURA - 8, 8)).inflate(12, 8)
    pygame.draw.rect(app["tela"], (0, 0, 0), fundo)
    app["tela"].blit(texto, texto.get_rect(center=fundo.center))


def _desenhar_vida(app):
    # desenha os 3 corações no canto superior esquerdo (cheio, meio ou vazio).
    for i in range(3):
        x = 12 + i * 32
        y = 12

        if app["jogador"]["vida"] >= i + 1:
            # coração inteiro (quadrado vermelho).
            pygame.draw.rect(app["tela"], (220, 40, 60), (x, y, 24, 24))
        elif app["jogador"]["vida"] >= i + 0.5:
            # meio coração (fundo escuro com metade esquerda vermelha).
            pygame.draw.rect(app["tela"], (60, 40, 45), (x, y, 24, 24))
            pygame.draw.rect(app["tela"], (220, 40, 60), (x, y, 12, 24))
        else:
            # coração vazio (quadrado escuro).
            pygame.draw.rect(app["tela"], (60, 40, 45), (x, y, 24, 24))