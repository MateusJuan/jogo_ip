from jogo.blocos import (
    BAU_FECHADO,
    GALERIA_BURACO,
    GALERIA_CHAO,
    GALERIA_PAREDE,
    GRAMA,
    MURO,
    SALAO_CHAO,
    SALAO_ENTULHO,
    SALAO_PAREDE,
    TORRE_ALTAR,
    TORRE_CHAO,
    TORRE_PAREDE,
    TORRE_PILAR,
    MURO_LABIRINTO,
)
from jogo.configuracoes import TAMANHO_MAPA
from jogo.inimigos import inimigos
from jogo.plataformas import Plataforma
from jogo.lagarto import criar_lagarto


class Mundo:
    # representa um andar do castelo com identificador, nome, matriz de blocos e escadas.
    def __init__(self, ident, nome, grade, escadas, baus=None, inimigos=None, plataformas = None,raio_visao=None):
        self.ident = ident
        self.nome = nome
        self.grade = grade
        self.escadas = escadas
        self.baus = baus or {} #depois colcoar a espada dentro do bau da entrada da masmorra
        self.abertura_porta = 0.0
        self.inimigos = inimigos or [] # lista de inimigos presentes neste mundo 
        self.plataformas = plataformas or []
        self.raio_visao = raio_visao
        self.visao_restaurada = False
        self.chefe = False

def criar_mundos():
    # instancia as salas e preserva seus estados durante toda a partida.
    lobby = _criar_lobby()
    salao = _criar_salao()
    galeria = _criar_galeria()
    torre = _criar_torre()
    labirinto = _criar_labirinto()
    ala_leste = _criar_ala_leste()
    return {
        lobby.ident: lobby,
        salao.ident: salao,
        galeria.ident: galeria,
        torre.ident: torre,
        labirinto.ident: labirinto,
        ala_leste.ident: ala_leste,
    }


def _grade(bloco):
    # gera uma matriz 17x17 totalmente preenchida com um mesmo tipo de bloco.
    return [[bloco for _ in range(TAMANHO_MAPA)] for _ in range(TAMANHO_MAPA)]


def _borda(grade, bloco):
    # preenche as 4 bordas externas da matriz com paredes ou muros.
    ultima = TAMANHO_MAPA - 1
    for i in range(TAMANHO_MAPA):
        grade[0][i] = bloco
        grade[ultima][i] = bloco
        grade[i][0] = bloco
        grade[i][ultima] = bloco


def _preencher(grade, x0, y0, x1, y1, bloco):
    # preenche um retângulo de blocos na matriz, de (x0, y0) até (x1, y1).
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grade[y][x] = bloco


def _celulas_portao(lado):
    # retorna as 3 coordenadas centrais da parede norte ou sul
    centro = TAMANHO_MAPA // 2 - 1
    ultima = TAMANHO_MAPA - 1
    if lado == "norte":
        return [(centro + deslocamento, 0) for deslocamento in range(3)]
    elif lado == "sul":
        return [(centro + deslocamento, ultima) for deslocamento in range(3)]
    elif lado == "leste":
        return [(ultima, centro + deslocamento) for deslocamento in range(3)]
    elif lado == "oeste":
        return [(0, centro + deslocamento) for deslocamento in range(3)]
    return []


def _escada(lado, destino, x, y, sobe, trancada=None):
    # As três células da passagem compartilham o mesmo estado da fechadura.
    passagem = {
        "destino": destino, "x": x, "y": y, "sobe": sobe,
        "trancada": trancada, "destrancada": False,
    }
    resultado = {}
    for celula in _celulas_portao(lado):
        resultado[celula] = passagem
    return resultado


def _criar_lobby():
    # entrada fechada com abismo central atravessado por tres plataformas moveis.
    grade = _grade(GALERIA_BURACO)
    _borda(grade, GALERIA_PAREDE)
    _preencher(grade, 7, 12, 9, 15, GALERIA_CHAO)
    _preencher(grade, 6, 1, 12, 3, GALERIA_CHAO)
    grade[2][11] = BAU_FECHADO
    baus = {(11, 2): ["Espada","Arco"]}
    escadas = _escada("norte", "salao", 8, 15, True)
    plataformas = [
        Plataforma(2, 10, 3, 2, 2, 12, 1, 0.55),
        Plataforma(12, 7, 3, 3, 2, 12, -1, 0.35),
        Plataforma(2, 4, 3, 3, 2, 12, 1, 0.20),
    ]
    return Mundo("lobby", "Entrada da Masmorra", grade, escadas, baus, plataformas=plataformas)


def _criar_salao():
    # andar 1 (salão): sala interna com 4 blocos de entulho e escadas ao sul e ao norte.
    grade = _grade(SALAO_CHAO)
    _borda(grade, SALAO_PAREDE)
    
    # Entulho decorativo no salão
    _preencher(grade, 2, 4, 5, 8, SALAO_ENTULHO)
    _preencher(grade, 11, 3, 14, 7, SALAO_ENTULHO)
    
    escadas = {}
    # Porta Sul: Volta para a Sala 1 (Lobby)
    escadas.update(_escada("sul", "lobby", 8, 1, False))

    # Porta Norte: Trancada por fechadura dourada
    escadas.update(_escada("norte", "torre", 8, 15, True, trancada="dourada"))
    
    # Porta Leste: Trancada por fechadura de prata
    escadas.update(_escada("leste", "ala_leste", 1, 8, True, trancada="prata"))
    
    # Porta Oeste (Ala Oeste): Leva para o Labirinto
    for x, y in _celulas_portao("oeste"):
        grade[y][x] = SALAO_CHAO
    escadas.update(_escada("oeste", "labirinto", 15, 8, True, trancada = "espinhos"))

    lista_inimigos = [inimigos(6, 6), inimigos(10, 6), inimigos(6, 10), inimigos(10, 10)]
    return Mundo("salao", "Andar 1 - Salão Central", grade, escadas, inimigos=lista_inimigos)


def _criar_galeria():
    # andar 2 (galeria): sala cheia de buracos com um caminho estreito em 's' até o norte.
    grade = _grade(GALERIA_BURACO)
    _preencher(grade, 7, 10, 9, 15, GALERIA_CHAO)
    _preencher(grade, 3, 10, 9, 11, GALERIA_CHAO)
    _preencher(grade, 3, 4, 4, 11, GALERIA_CHAO)
    _preencher(grade, 3, 4, 9, 5, GALERIA_CHAO)
    _preencher(grade, 7, 1, 9, 5, GALERIA_CHAO)
    _borda(grade, GALERIA_PAREDE)
    escadas = {}
    escadas.update(_escada("sul", "salao", 8, 1, False))
    escadas.update(_escada("norte", "torre", 8, 15, True))
    lista_inimigos = [inimigos(4, 10), inimigos(6, 4)]
    return Mundo("galeria", "Andar 2 - Galeria", grade, escadas, inimigos=lista_inimigos)


def _criar_ala_leste():
    # Arena livre; a entrada a oeste fica distante do lagarto no centro.
    grade = _grade(SALAO_CHAO)
    _borda(grade, SALAO_PAREDE)
    escadas = _escada("oeste", "salao", 15, 8, False)
    mundo = Mundo("ala_leste", "Sala 5 - Covil do Lagarto", grade, escadas)
    mundo.chefe = criar_lagarto(8, 8)
    return mundo
    



def _criar_torre():
    # andar 3 (torre): topo do castelo com 6 pilares, altar ao norte e escada de volta.
    grade = _grade(TORRE_CHAO)
    _borda(grade, TORRE_PAREDE)
    _preencher(grade, 7, 2, 9, 3, TORRE_ALTAR)
    for x, y in ((3, 4), (13, 4), (3, 9), (13, 9), (4, 13), (12, 13)):
        grade[y][x] = TORRE_PILAR
    escadas = _escada("sul", "salao", 8, 1, False)
    return Mundo("torre", "Andar 3 - Torre", grade, escadas)

def _criar_labirinto():
    # Inicia a grade toda como chão transitável e fecha as bordas externas (vermelhas na imagem)
    grade = _grade(GRAMA)
    _borda(grade, GALERIA_PAREDE)

    # --- PAREDES INTERNAS (blocos verdes da imagem) ---
    # Canto superior esquerdo (L invertido)
    _preencher(grade, 2, 2, 2, 9, MURO_LABIRINTO)
    _preencher(grade, 3, 2, 6, 2, MURO_LABIRINTO)

    # Coluna centro-esquerda superior e barra horizontal central
    _preencher(grade, 6, 2, 6, 6, MURO_LABIRINTO)
    _preencher(grade, 5, 6, 10, 6, MURO_LABIRINTO)

    # Coluna centro-direita superior e inferior (parede vertical contínua)
    _preencher(grade, 10, 2, 10, 11, MURO_LABIRINTO)

    # Canto superior direito (L invertido)
    _preencher(grade, 13, 2, 14, 2, MURO_LABIRINTO)
    _preencher(grade, 13, 3, 13, 7, MURO_LABIRINTO)

    # Pilar central-esquerdo (ao lado do objetivo vermelho)
    _preencher(grade, 5, 7, 5, 11, MURO_LABIRINTO)

    # Bloco inferior esquerdo (formato de garfo/E)
    _preencher(grade, 2, 11, 7, 11, MURO_LABIRINTO)
    _preencher(grade, 4, 12, 4, 14, MURO_LABIRINTO)
    _preencher(grade, 2, 14, 3, 14, MURO_LABIRINTO)
    _preencher(grade, 7, 12, 7, 14, MURO_LABIRINTO)

    # Bloco inferior direito (conectado até a borda sul)
    _preencher(grade, 13, 9, 13, 15, MURO_LABIRINTO)
    _preencher(grade, 10, 11, 12, 11, MURO_LABIRINTO)
    _preencher(grade, 9, 14, 12, 14, MURO_LABIRINTO)

    # --- OBJETIVO CENTRAL (bloco vermelho no centro da imagem) ---
    # Colocado em (8, 8) como um baú fechado (pode trocar por TORRE_ALTAR ou outro bloco)
    grade[8][8] = BAU_FECHADO
    baus = {(8, 8): ["Chave de Prata"]}

    # --- PORTÃO DE ENTRADA / SAÍDA (Lado Leste) ---
    # Mantém a abertura no leste (x=16, y=7..9) para o jogador entrar em (15, 8) e voltar ao salão
    escadas = {}
    escadas.update(_escada("leste", "salao", 1, 8, False))

    lista_inimigos = [inimigos(4, 8), inimigos(4, 9)]

    return Mundo("labirinto", "Labirinto", grade, escadas, baus=baus, inimigos=lista_inimigos)

