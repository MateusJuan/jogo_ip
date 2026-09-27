from jogo.blocos import (
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
    def __init__(self, ident, nome, grade, escadas):
        self.ident = ident
        self.nome = nome
        self.grade = grade
        self.escadas = escadas


def criar_mundos():
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
    return [[bloco for _ in range(TAMANHO_MAPA)] for _ in range(TAMANHO_MAPA)]


def _borda(grade, bloco):
    ultima = TAMANHO_MAPA - 1
    for i in range(TAMANHO_MAPA):
        grade[0][i] = bloco
        grade[ultima][i] = bloco
        grade[i][0] = bloco
        grade[i][ultima] = bloco


def _preencher(grade, x0, y0, x1, y1, bloco):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grade[y][x] = bloco


def _celulas_portao(lado):
    centro = TAMANHO_MAPA // 2 - 1
    ultima = TAMANHO_MAPA - 1
    if lado == "norte":
        return [(centro + deslocamento, 0) for deslocamento in range(3)]
    return [(centro + deslocamento, ultima) for deslocamento in range(3)]


def _escada(lado, destino, x, y, sobe):
    return {
        celula: {"destino": destino, "x": x, "y": y, "sobe": sobe}
        for celula in _celulas_portao(lado)
    }


def _criar_lobby():
    grade = _grade(GRAMA)
    _borda(grade, MURO)
    escadas = _escada("norte", "salao", 8, 15, True)
    return Mundo("lobby", "Lobby", grade, escadas)


def _criar_salao():
    grade = _grade(SALAO_CHAO)
    _borda(grade, SALAO_PAREDE)
    _preencher(grade, 2, 4, 5, 8, SALAO_ENTULHO)
    _preencher(grade, 11, 3, 14, 7, SALAO_ENTULHO)
    _preencher(grade, 3, 11, 6, 13, SALAO_ENTULHO)
    _preencher(grade, 10, 10, 13, 13, SALAO_ENTULHO)
    escadas = {}
    escadas.update(_escada("sul", "lobby", 8, 1, False))
    escadas.update(_escada("norte", "galeria", 8, 15, True))
    return Mundo("salao", "Andar 1 · Salão", grade, escadas)


def _criar_galeria():
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
    return Mundo("galeria", "Andar 2 · Galeria", grade, escadas)


def _criar_torre():
    grade = _grade(TORRE_CHAO)
    _borda(grade, TORRE_PAREDE)
    _preencher(grade, 7, 2, 9, 3, TORRE_ALTAR)
    for x, y in ((3, 4), (13, 4), (3, 9), (13, 9), (4, 13), (12, 13)):
        grade[y][x] = TORRE_PILAR
    escadas = _escada("sul", "galeria", 8, 1, False)
    return Mundo("torre", "Andar 3 · Torre", grade, escadas)
