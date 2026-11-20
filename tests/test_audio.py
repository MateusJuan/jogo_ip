import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from jogo.audio import PASTA_MUSICAS, TEMPO_TRANSICAO, TrilhaSonora, VOLUME_MUSICA


class ControleDeTrilhasTest(unittest.TestCase):
    def setUp(self):
        mixer = patch("jogo.audio.pygame.mixer.get_init", return_value=(44100, -16, 2))
        backend = patch("jogo.audio.pygame.mixer.music")
        mixer.start()
        self.musica = backend.start()
        self.addCleanup(mixer.stop)
        self.addCleanup(backend.stop)
        self.trilha = TrilhaSonora()

    def test_repetir_pedido_do_mapa_nao_reinicia_a_musica(self):
        self.trilha.tocar_mapa("lobby")
        for _ in range(90):
            self.trilha.tocar_mapa("lobby")
            self.trilha.atualizar(1 / 60)
        self.musica.load.assert_called_once_with(str(PASTA_MUSICAS / "01_entrada.mp3"))
        self.musica.play.assert_called_once_with(loops=-1)
        self.assertEqual(self.trilha._volume, VOLUME_MUSICA)

    def test_troca_de_sala_reduz_volume_antes_de_carregar_sem_bloquear(self):
        self.trilha.tocar_mapa("lobby")
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertEqual(self.trilha.faixa_atual, "lobby")
        self.assertAlmostEqual(self.musica.set_volume.call_args.args[0], VOLUME_MUSICA / 2)
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertEqual(self.trilha.faixa_atual, "salao")
        self.musica.load.assert_called_with(str(PASTA_MUSICAS / "02_salao.mp3"))
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.trilha._volume, VOLUME_MUSICA)
        self.musica.fadeout.assert_not_called()

    def test_voltar_antes_da_transicao_terminar_cancela_o_destino(self):
        self.trilha.tocar_mapa("lobby")
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.trilha.tocar_mapa("lobby")
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.trilha.faixa_atual, "lobby")
        self.musica.load.assert_called_once()
        self.assertEqual(self.trilha._volume, VOLUME_MUSICA)

    def test_mapas_em_desenvolvimento_nao_recebem_trilhas(self):
        for mapa in ("galeria", "torre", "ala_leste", "ala_oeste"):
            with self.subTest(mapa=mapa):
                self.trilha.tocar_mapa("lobby", reiniciar=True)
                self.trilha.atualizar(TEMPO_TRANSICAO)
                carregamentos = self.musica.load.call_count
                self.trilha.tocar_mapa(mapa)
                self.trilha.atualizar(TEMPO_TRANSICAO)
                self.assertIsNone(self.trilha.faixa_atual)
                self.assertEqual(self.musica.load.call_count, carregamentos)

    def test_reiniciar_repete_a_entrada_desde_o_comeco(self):
        self.trilha.tocar_mapa("lobby")
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.trilha.tocar_mapa("lobby", reiniciar=True)
        self.assertEqual(self.musica.play.call_count, 2)
        self.assertEqual(self.trilha._volume, 0.0)

    def test_sem_dispositivo_de_audio_nao_tenta_reproduzir(self):
        with patch("jogo.audio.pygame.mixer.get_init", return_value=None):
            trilha = TrilhaSonora()
            trilha.tocar_mapa("lobby")
            trilha.atualizar(1)
            trilha.parar()
            trilha.encerrar()
        self.assertFalse(trilha.disponivel)
        self.musica.load.assert_not_called()
        self.musica.play.assert_not_called()

    def test_arquivo_ausente_nao_interrompe_o_jogo_nem_repete_o_aviso(self):
        self.musica.load.side_effect = FileNotFoundError("arquivo ausente")
        with self.assertLogs("jogo.audio", level="WARNING") as avisos:
            for _ in range(10):
                self.trilha.tocar_mapa("lobby")
                self.trilha.atualizar(1 / 60)
        self.assertEqual(len(avisos.output), 1)
        self.musica.load.assert_called_once()
        self.musica.play.assert_not_called()


class AudioNoJogoTest(unittest.TestCase):
    def setUp(self):
        from jogo.aplicacao import Aplicacao
        self.app = Aplicacao()

    def tearDown(self):
        self.app.trilha.encerrar()
        pygame.quit()

    def test_mp3_reais_e_troca_de_mapa_pelas_escadas(self):
        self.app.trilha.tocar_mapa(self.app.mundo.ident)
        self.app.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertTrue(pygame.mixer.music.get_busy())
        self.assertEqual(self.app.trilha.faixa_atual, "lobby")
        self.app.jogador.definir_posicao(8, 0)
        self.app._verificar_escada()
        self.app.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.app.mundo.ident, "salao")
        self.assertEqual(self.app.trilha.faixa_atual, "salao")
        self.assertTrue(pygame.mixer.music.get_busy())
        self.app.jogador.definir_posicao(8, 16)
        self.app._verificar_escada()
        self.app.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.app.mundo.ident, "lobby")
        self.assertEqual(self.app.trilha.faixa_atual, "lobby")

    def test_vitoria_para_a_trilha_e_enter_reinicia_a_entrada(self):
        self.app.trilha.tocar_mapa("lobby")
        self.app.trilha.atualizar(TEMPO_TRANSICAO)
        self.app.mundo = self.app.mundos["torre"]
        self.app.jogador.definir_posicao(8, 4)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f))
        self.app._eventos()
        self.app.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertTrue(self.app.vitoria)
        self.assertFalse(pygame.mixer.music.get_busy())
        self.app._desenhar()
        self.assertLessEqual(
            self.app.fonte.size("Trilha sonora escrita por matewx_j")[0], 616
        )
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.app._eventos()
        self.assertFalse(self.app.vitoria)
        self.assertEqual(self.app.mundo.ident, "lobby")
        self.assertTrue(pygame.mixer.music.get_busy())

    def test_loop_principal_inicia_e_encerra_com_audio(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.app.executar()
        self.assertFalse(pygame.get_init())


if __name__ == "__main__":
    unittest.main()
