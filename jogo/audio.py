"""Reprodução das trilhas dos mapas que já têm música definida."""

import logging
from pathlib import Path

import pygame


PASTA_MUSICAS = Path(__file__).resolve().parent.parent / "assets" / "musicas"
TRILHAS_MAPAS = {
    "lobby": "01_entrada.mp3",
    "salao": "02_salao.mp3",
    "labirinto": "04_abismo.mp3",
}
VOLUME_MUSICA = 0.5
TEMPO_TRANSICAO = 3.0
TEMPO_ETAPA = TEMPO_TRANSICAO / 2

logger = logging.getLogger(__name__)


class TrilhaSonora:
    def __init__(self):
        self.disponivel = pygame.mixer.get_init() is not None
        self.faixa_atual = None
        self._pedida = None
        self._sons = {}
        self._canal = None
        self._volume = 0.0
        self._volume_inicial = self._volume_final = 0.0
        self._tempo = 0.0
        self._fase = None
        if not self.disponivel:
            return

        # Um único canal garante que as músicas nunca se sobreponham.
        if pygame.mixer.get_num_channels() < 1:
            pygame.mixer.set_num_channels(1)
        pygame.mixer.set_reserved(1)
        self._canal = pygame.mixer.Channel(0)
        self._canal.set_volume(0.0)
        for faixa, arquivo in TRILHAS_MAPAS.items():
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

        self._pedida = faixa
        if reiniciar:
            self._silenciar()
            self._iniciar_pedida()
        elif self.faixa_atual is None:
            self._iniciar_pedida()
        elif faixa == self.faixa_atual:
            # Voltar antes do silêncio cancela a troca sem reiniciar a faixa atual.
            self._preparar_etapa("entrando", VOLUME_MUSICA)
        elif self._volume == 0.0:
            self._silenciar()
            self._iniciar_pedida()
        elif self._fase != "saindo":
            self._preparar_etapa("saindo", 0.0)

    def _preparar_etapa(self, fase, volume_final):
        self._fase = fase
        self._volume_inicial = self._volume
        self._volume_final = volume_final
        self._tempo = 0.0

    def _silenciar(self):
        self._volume = 0.0
        self._canal.set_volume(0.0)
        self._canal.stop()
        self.faixa_atual = None
        self._fase = None

    def _iniciar_pedida(self):
        if self._pedida is None:
            self._fase = None
            return
        self._canal.set_volume(0.0)
        self._volume = 0.0
        self._canal.play(self._sons[self._pedida], loops=-1)
        self.faixa_atual = self._pedida
        self._preparar_etapa("entrando", VOLUME_MUSICA)

    def atualizar(self, dt):
        if not self.disponivel:
            return
        if not pygame.mixer.get_init():
            self.disponivel = False
            return

        restante = max(0.0, dt)
        while self._fase is not None:
            passo = min(restante, max(0.0, TEMPO_ETAPA - self._tempo))
            self._tempo += passo
            restante = max(0.0, restante - passo)
            if TEMPO_ETAPA - self._tempo < 1e-9:
                self._tempo = TEMPO_ETAPA
            progresso = min(1.0, self._tempo / TEMPO_ETAPA)
            suave = progresso * progresso * (3.0 - 2.0 * progresso)
            self._volume = self._volume_inicial + (self._volume_final - self._volume_inicial) * suave
            self._canal.set_volume(self._volume)
            if progresso < 1.0:
                break
            if self._fase == "saindo":
                # A nova faixa só pode começar depois de zerar e parar a anterior.
                self._silenciar()
                self._iniciar_pedida()
            else:
                self._fase = None
            if restante <= 0.0:
                break

    def encerrar(self):
        if self.disponivel and pygame.mixer.get_init():
            self._silenciar()
        self._sons.clear()
        self.disponivel = False
        self.faixa_atual = None
