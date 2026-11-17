# códigos numéricos que representam cada tipo de terreno nas matrizes dos mapas.
GRAMA = 0
MURO = 1
SALAO_CHAO = 2
SALAO_ENTULHO = 3
SALAO_PAREDE = 4
GALERIA_CHAO = 5
GALERIA_BURACO = 6
GALERIA_PAREDE = 7
TORRE_CHAO = 8
TORRE_PILAR = 9
TORRE_PAREDE = 10
TORRE_ALTAR = 11
BAU_FECHADO = 12

# lista de blocos que fazem o personagem cair e perder vida (usamos lista no lugar de set).
BURACOS = [
    GALERIA_BURACO,
]

# lista de blocos que bloqueiam a passagem do personagem (paredes e obstáculos).
SOLIDOS = [
    BAU_FECHADO,
    MURO,
    SALAO_ENTULHO,
    SALAO_PAREDE,
    GALERIA_PAREDE,
    TORRE_PILAR,
    TORRE_PAREDE,
    TORRE_ALTAR,
]

# dicionário que liga o número do bloco na matriz ao nome da imagem carregada em recursos.py.
IMAGENS = {
    BAU_FECHADO: "galeria_chao",
    GRAMA: "grama",
    MURO: "muro",
    SALAO_CHAO: "salao_chao",
    SALAO_ENTULHO: "salao_entulho",
    SALAO_PAREDE: "salao_parede",
    GALERIA_CHAO: "galeria_chao",
    GALERIA_BURACO: "galeria_buraco",
    GALERIA_PAREDE: "galeria_parede",
    TORRE_CHAO: "torre_chao",
    TORRE_PILAR: "torre_pilar",
    TORRE_PAREDE: "torre_parede",
    TORRE_ALTAR: "torre_altar",
}