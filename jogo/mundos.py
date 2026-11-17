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


def criar_mundo(ident, nome, grade, escadas):
    # cria o dicionário que representa um andar do castelo (substitui a classe Mundo).
    return {
        "ident": ident,
        "nome": nome,
        "grade": grade,
        "escadas": escadas,
    }


def criar_mundos():
    # monta todos os 4 andares e retorna um dicionário indexado pelo identificador.
    lobby = _criar_lobby()
    salao = _criar_salao()
    galeria = _criar_galeria()
    torre = _criar_torre()
    return {
        lobby["ident"]: lobby,
        salao["ident"]: salao,
        galeria["ident"]: galeria,
        torre["ident"]: torre,
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
    # retorna as 3 coordenadas centrais da parede norte (y=0) ou sul (y=16) para a escada.
    centro = TAMANHO_MAPA // 2 - 1
    ultima = TAMANHO_MAPA - 1
    if lado == "norte":
        return [(centro + deslocamento, 0) for deslocamento in range(3)]
    return [(centro + deslocamento, ultima) for deslocamento in range(3)]


def _escada(lado, destino, x, y, sobe):
    # mapeia as 3 células da escada para o andar de destino e a posição onde o jogador nasce.
    resultado = {}
    for celula in _celulas_portao(lado):
        resultado[celula] = {"destino": destino, "x": x, "y": y, "sobe": sobe}
    return resultado


def _criar_lobby():
    # andar 0 (lobby): pátio aberto com escada ao norte levando para o salão.
    grade = _grade(GRAMA)
    _borda(grade, MURO)
    escadas = _escada("norte", "salao", 8, 15, True)
    return criar_mundo("lobby", "Lobby", grade, escadas)


def _criar_salao():
    # andar 1 (salão): sala interna com 4 blocos de entulho e escadas ao sul e ao norte.
    grade = _grade(SALAO_CHAO)
    _borda(grade, SALAO_PAREDE)
    _preencher(grade, 2, 4, 5, 8, SALAO_ENTULHO)
    _preencher(grade, 11, 3, 14, 7, SALAO_ENTULHO)
    _preencher(grade, 3, 11, 6, 13, SALAO_ENTULHO)
    _preencher(grade, 10, 10, 13, 13, SALAO_ENTULHO)
    escadas = {}
    escadas.update(_escada("sul", "lobby", 8, 1, False))
    escadas.update(_escada("norte", "galeria", 8, 15, True))
    return criar_mundo("salao", "Andar 1 - Salão", grade, escadas)


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
    return criar_mundo("galeria", "Andar 2 - Galeria", grade, escadas)


def _criar_torre():
    # andar 3 (torre): topo do castelo com 6 pilares, altar ao norte e escada de volta.
    grade = _grade(TORRE_CHAO)
    _borda(grade, TORRE_PAREDE)
    _preencher(grade, 7, 2, 9, 3, TORRE_ALTAR)
    for x, y in ((3, 4), (13, 4), (3, 9), (13, 9), (4, 13), (12, 13)):
        grade[y][x] = TORRE_PILAR
    escadas = _escada("sul", "galeria", 8, 1, False)
    return criar_mundo("torre", "Andar 3 - Torre", grade, escadas)