"""Reprodução das trilhas dos mapas que já têm música definida."""

import logging
import math
from pathlib import Path

import pygame


PASTA_MUSICAS = Path(__file__).resolve().parent.parent / "assets" / "musicas"
TRILHAS_MAPAS = {
    "lobby": "01_entrada.mp3",
    "salao": "02_salao.mp3",
}
VOLUME_MUSICA = 0.5
TEMPO_TRANSICAO = 3.0

logger = logging.getLogger(__name__)


class TrilhaSonora:
    def __init__(self):
        self.disponivel = pygame.mixer.get_init() is not None
        self.faixa_atual = None
        self._pedida = None
        self._sons = {}
        self._canais = {}
        self._volumes = {faixa: 0.0 for faixa in TRILHAS_MAPAS}
        self._tempo = 0.0
        self._transicionando = False
        self._angulo_inicial = self._angulo_final = 0.0
        self._ganho_inicial = self._ganho_final = 0.0
        if not self.disponivel:
            return

        # Dois canais exclusivos permitem sobrepor as faixas durante a troca.
        quantidade = len(TRILHAS_MAPAS)
        if pygame.mixer.get_num_channels() < quantidade:
            pygame.mixer.set_num_channels(quantidade)
        pygame.mixer.set_reserved(quantidade)
        for indice, (faixa, arquivo) in enumerate(TRILHAS_MAPAS.items()):
            canal = pygame.mixer.Channel(indice)
            canal.set_volume(0.0)
            self._canais[faixa] = canal
            try:
                # Decodificar na abertura evita carregar MP3 ao atravessar a porta.
                self._sons[faixa] = pygame.mixer.Sound(str(PASTA_MUSICAS / arquivo))
            except (pygame.error, OSError) as erro:
                logger.warning("Não foi possível carregar a trilha %s: %s", faixa, erro)

    def tocar_mapa(self, identificador, reiniciar=False):
        self._solicitar(identificador if identificador in TRILHAS_MAPAS else None, reiniciar)

    def parar(self):
        self._solicitar(None)

    def _solicitar(self, faixa, reiniciar=False):
        if faixa not in self._sons:
            faixa = None
        if not self.disponivel or (faixa == self._pedida and not reiniciar):
            return
        if not pygame.mixer.get_init():
            self.disponivel = False
            return

        if reiniciar:
            for identificador, canal in self._canais.items():
                canal.stop()
                canal.set_volume(0.0)
                self._volumes[identificador] = 0.0
            self.faixa_atual = None

        self._pedida = faixa
        if faixa is not None:
            canal = self._canais[faixa]
            if not canal.get_busy():
                canal.set_volume(0.0)
                canal.play(self._sons[faixa], loops=-1)
                self._volumes[faixa] = 0.0
            if self.faixa_atual is None:
                self.faixa_atual = faixa

        entrada, salao = self._volumes.values()
        self._ganho_inicial = math.hypot(entrada, salao)
        self._ganho_final = VOLUME_MUSICA if faixa is not None else 0.0
        self._angulo_inicial = math.atan2(salao, entrada)
        self._angulo_final = (
            self._angulo_inicial if faixa is None else
            0.0 if faixa == "lobby" else math.pi / 2
        )
        if self._ganho_inicial == 0.0:
            self._angulo_inicial = self._angulo_final
        self._tempo = 0.0
        self._transicionando = True

    def atualizar(self, dt):
        if not self.disponivel:
            return
        if not pygame.mixer.get_init():
            self.disponivel = False
            return
        if not self._transicionando:
            return

        self._tempo += max(0.0, dt)
        progresso = min(1.0, self._tempo / TEMPO_TRANSICAO)
        suave = progresso * progresso * (3.0 - 2.0 * progresso)
        angulo = self._angulo_inicial + (self._angulo_final - self._angulo_inicial) * suave
        ganho = self._ganho_inicial + (self._ganho_final - self._ganho_inicial) * suave
        # Seno/cosseno mantêm a potência da mistura estável, sem um buraco de silêncio.
        volumes = (ganho * math.cos(angulo), ganho * math.sin(angulo))
        for (faixa, canal), volume in zip(self._canais.items(), volumes):
            if progresso == 1.0:
                volume = VOLUME_MUSICA if faixa == self._pedida else 0.0
            self._volumes[faixa] = volume
            canal.set_volume(volume)
            if progresso == 1.0 and volume == 0.0:
                canal.stop()
        if progresso == 1.0:
            self.faixa_atual = self._pedida
            self._transicionando = False

    def encerrar(self):
        if self.disponivel and pygame.mixer.get_init():
            for canal in self._canais.values():
                canal.stop()
        self._sons.clear()
        self.disponivel = False
        self.faixa_atual = None

