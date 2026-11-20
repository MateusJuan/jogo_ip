"""Reprodução das trilhas dos mapas que já têm música definida."""

import logging
from pathlib import Path

import pygame


PASTA_MUSICAS = Path(__file__).resolve().parent.parent / "assets" / "musicas"
TRILHAS_MAPAS = {
    "lobby": "01_entrada.mp3",
    "salao": "02_salao.mp3",
}
VOLUME_MUSICA = 0.5
TEMPO_TRANSICAO = 0.35

logger = logging.getLogger(__name__)


class TrilhaSonora:
    def __init__(self):
        self.disponivel = pygame.mixer.get_init() is not None
        self.faixa_atual = None
        self._pedida = None
        self._volume = 0.0
        self._volume_saida = 0.0
        self._tempo_saida = 0.0
        self._saindo = False

    def tocar_mapa(self, identificador, reiniciar=False):
        self._solicitar(identificador if identificador in TRILHAS_MAPAS else None, reiniciar)

    def parar(self):
        self._solicitar(None)

    def _solicitar(self, faixa, reiniciar=False):
        if not self.disponivel or (faixa == self._pedida and not reiniciar):
            return
        self._pedida = faixa
        if self.faixa_atual is None or reiniciar:
            self._iniciar(faixa)
        elif faixa == self.faixa_atual:
            # Voltar à mesma sala durante a transição mantém a música em andamento.
            self._saindo = False
        else:
            self._volume_saida = self._volume
            self._tempo_saida = 0.0
            self._saindo = True

    def _iniciar(self, faixa):
        self._saindo = False
        self.faixa_atual = None
        self._volume = 0.0
        try:
            pygame.mixer.music.stop()
            if faixa is None:
                return
            arquivo = TRILHAS_MAPAS[faixa]
            pygame.mixer.music.load(str(PASTA_MUSICAS / arquivo))
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(loops=-1)
            self.faixa_atual = faixa
        except (pygame.error, OSError) as erro:
            pygame.mixer.music.stop()
            self.faixa_atual = None
            logger.warning("Não foi possível reproduzir a trilha %s: %s", faixa, erro)

    def atualizar(self, dt):
        if not self.disponivel:
            return
        if not pygame.mixer.get_init():
            self.disponivel = False
            return
        if self._saindo:
            self._tempo_saida += max(0.0, dt)
            progresso = min(1.0, self._tempo_saida / TEMPO_TRANSICAO)
            self._volume = self._volume_saida * (1.0 - progresso)
            pygame.mixer.music.set_volume(self._volume)
            if progresso == 1.0:
                self._iniciar(self._pedida)
        elif self.faixa_atual is not None and self._volume < VOLUME_MUSICA:
            self._volume = min(
                VOLUME_MUSICA, self._volume + VOLUME_MUSICA * max(0.0, dt) / TEMPO_TRANSICAO
            )
            pygame.mixer.music.set_volume(self._volume)

    def encerrar(self):
        if self.disponivel and pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        self.disponivel = False
        self.faixa_atual = None

