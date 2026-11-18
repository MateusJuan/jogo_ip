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
)
from jogo.configuracoes import TAMANHO_MAPA


class Mundo:
    # representa um andar do castelo com identificador, nome, matriz de blocos e escadas.
    def __init__(self, ident, nome, grade, escadas, baus=None):
        self.ident = ident
        self.nome = nome
        self.grade = grade
        self.escadas = escadas
        self.baus = baus or {} #depois colcoar a espada dentro do bau da entrada da masmorra
        self.abertura_porta = 0.0
        self.porta_ativada = False


def criar_mundos():
    # instancia todos os 4 andares e retorna um dicionário indexado pelo identificador.
    lobby = _criar_lobby()
    salao = _criar_salao()
    galeria = _criar_galeria()
    torre = _criar_torre()
    return {
        lobby.ident: lobby,
        salao.ident: salao,
        galeria.ident: galeria,
        torre.ident: torre,
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
    return []


def _escada(lado, destino, x, y, sobe):
    # mapeia as 3 células da escada para o andar de destino e a posição onde o jogador nasce.
    resultado = {}
    for celula in _celulas_portao(lado):
        resultado[celula] = {"destino": destino, "x": x, "y": y, "sobe": sobe}
    return resultado


def _criar_lobby():
    # Entrada fechada com percurso em S entre dois abismos.
    grade = _grade(GALERIA_BURACO)
    _borda(grade, GALERIA_PAREDE)
    _preencher(grade, 7, 12, 9, 15, GALERIA_CHAO)
    _preencher(grade, 4, 10, 9, 12, GALERIA_CHAO)
    _preencher(grade, 4, 6, 6, 12, GALERIA_CHAO)
    _preencher(grade, 4, 5, 10, 7, GALERIA_CHAO)
    _preencher(grade, 8, 1, 10, 6, GALERIA_CHAO)
    _preencher(grade, 6, 1, 12, 3, GALERIA_CHAO)
    grade[2][11] = BAU_FECHADO
    baus = {(11, 2): ["Espada"]}
    escadas = _escada("norte", "salao", 8, 15, True)
    return Mundo("lobby", "Entrada da Masmorra", grade, escadas, baus)


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

    return Mundo("salao", "Andar 1 - Salão Central", grade, escadas)


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
    return Mundo("galeria", "Andar 2 - Galeria", grade, escadas)


def _criar_torre():
    # andar 3 (torre): topo do castelo com 6 pilares, altar ao norte e escada de volta.
    grade = _grade(TORRE_CHAO)
    _borda(grade, TORRE_PAREDE)
    _preencher(grade, 7, 2, 9, 3, TORRE_ALTAR)
    for x, y in ((3, 4), (13, 4), (3, 9), (13, 9), (4, 13), (12, 13)):
        grade[y][x] = TORRE_PILAR
    escadas = _escada("sul", "galeria", 8, 1, False)
    return Mundo("torre", "Andar 3 - Torre", grade, escadas)