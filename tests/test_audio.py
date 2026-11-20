import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from jogo.audio import PASTA_MUSICAS, TEMPO_TRANSICAO, TrilhaSonora, VOLUME_MUSICA


class CanalSimulado:
    def __init__(self):
        self.volume = 0.0
        self.ativo = False
        self.inicios = []

    def set_volume(self, volume):
        self.volume = volume

    def get_busy(self):
        return self.ativo

    def play(self, som, loops):
        self.ativo = True
        self.inicios.append((som, loops))

    def stop(self):
        self.ativo = False


class ControleDeTrilhasTest(unittest.TestCase):
    def setUp(self):
        self.canais = [CanalSimulado(), CanalSimulado()]
        patches = [
            patch("jogo.audio.pygame.mixer.get_init", return_value=(44100, -16, 2)),
            patch("jogo.audio.pygame.mixer.get_num_channels", return_value=8),
            patch("jogo.audio.pygame.mixer.set_reserved"),
            patch("jogo.audio.pygame.mixer.Channel", side_effect=self.canais.__getitem__),
            patch("jogo.audio.pygame.mixer.Sound", side_effect=lambda caminho: caminho),
            patch("jogo.audio.pygame.mixer.music"),
        ]
        mocks = []
        for patcher in patches:
            mocks.append(patcher.start())
            self.addCleanup(patcher.stop)
        self.carregar_som = mocks[4]
        self.musica_stream = mocks[5]
        self.trilha = TrilhaSonora()

    def iniciar_entrada(self):
        self.trilha.tocar_mapa("lobby")
        self.trilha.atualizar(TEMPO_TRANSICAO)

    def test_repetir_pedido_do_mapa_nao_reinicia_a_musica(self):
        self.iniciar_entrada()
        for _ in range(90):
            self.trilha.tocar_mapa("lobby")
            self.trilha.atualizar(1 / 60)
        self.assertEqual(len(self.canais[0].inicios), 1)
        self.assertEqual(self.canais[0].inicios[0], (str(PASTA_MUSICAS / "01_entrada.mp3"), -1))
        self.assertEqual(self.canais[0].volume, VOLUME_MUSICA)
        # A troca de mapa não depende de decodificação ou leitura do disco.
        self.assertEqual(self.carregar_som.call_count, 2)

    def test_as_duas_faixas_se_sobrepoem_durante_a_transicao(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.assertTrue(all(canal.ativo for canal in self.canais))
        self.assertEqual(self.canais[1].volume, 0.0)
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertTrue(all(canal.ativo for canal in self.canais))
        for canal in self.canais:
            self.assertAlmostEqual(canal.volume, VOLUME_MUSICA / 2 ** 0.5)
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertFalse(self.canais[0].ativo)
        self.assertTrue(self.canais[1].ativo)
        self.assertEqual(self.canais[1].volume, VOLUME_MUSICA)
        self.assertEqual(self.trilha.faixa_atual, "salao")
        self.musica_stream.fadeout.assert_not_called()
        self.assertEqual(self.carregar_som.call_count, 2)

    def test_mistura_nao_cria_buraco_de_volume_nem_pico_de_potencia(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        for _ in range(180):
            self.trilha.atualizar(TEMPO_TRANSICAO / 180)
            potencia = sum(canal.volume ** 2 for canal in self.canais)
            self.assertAlmostEqual(potencia, VOLUME_MUSICA ** 2, places=12)
            self.assertTrue(all(0 <= canal.volume <= VOLUME_MUSICA for canal in self.canais))

    def test_curva_comeca_gradualmente_e_dura_tres_segundos(self):
        self.assertEqual(TEMPO_TRANSICAO, 3.0)
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(1 / 60)
        self.assertLess(self.canais[1].volume, 0.001)
        self.assertGreater(self.canais[0].volume, VOLUME_MUSICA - 0.001)
        self.trilha.atualizar(0.5)
        self.assertTrue(all(canal.ativo for canal in self.canais))

    def test_voltar_durante_a_transicao_preserva_posicao_e_volumes(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 3)
        antes = [canal.volume for canal in self.canais]
        self.trilha.tocar_mapa("lobby")
        self.assertEqual([canal.volume for canal in self.canais], antes)
        self.trilha.atualizar(0)
        for canal, volume in zip(self.canais, antes):
            self.assertAlmostEqual(canal.volume, volume)
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.trilha.faixa_atual, "lobby")
        self.assertEqual(len(self.canais[0].inicios), 1)
        self.assertEqual(self.canais[0].volume, VOLUME_MUSICA)
        self.assertFalse(self.canais[1].ativo)

    def test_parar_no_meio_da_transicao_diminui_as_duas_faixas(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        antes = [canal.volume for canal in self.canais]
        self.trilha.parar()
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        for canal, volume in zip(self.canais, antes):
            self.assertAlmostEqual(canal.volume, volume / 2)
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertFalse(any(canal.ativo for canal in self.canais))
        self.assertIsNone(self.trilha.faixa_atual)

    def test_mapas_em_desenvolvimento_nao_recebem_trilhas(self):
        for mapa in ("galeria", "torre", "ala_leste", "ala_oeste"):
            with self.subTest(mapa=mapa):
                self.trilha.tocar_mapa("lobby", reiniciar=True)
                self.trilha.atualizar(TEMPO_TRANSICAO)
                self.trilha.tocar_mapa(mapa)
                self.trilha.atualizar(TEMPO_TRANSICAO)
                self.assertIsNone(self.trilha.faixa_atual)
                self.assertFalse(any(canal.ativo for canal in self.canais))
        self.assertEqual(self.carregar_som.call_count, 2)

    def test_reiniciar_repete_a_entrada_desde_o_comeco(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.trilha.tocar_mapa("lobby", reiniciar=True)
        self.assertEqual(len(self.canais[0].inicios), 2)
        self.assertFalse(self.canais[1].ativo)
        self.assertTrue(all(canal.volume == 0.0 for canal in self.canais))
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.trilha.faixa_atual, "lobby")
        self.assertEqual(self.canais[0].volume, VOLUME_MUSICA)

    def test_sem_dispositivo_de_audio_nao_tenta_reproduzir(self):
        carregamentos = self.carregar_som.call_count
        with patch("jogo.audio.pygame.mixer.get_init", return_value=None):
            trilha = TrilhaSonora()
            trilha.tocar_mapa("lobby")
            trilha.atualizar(1)
            trilha.parar()
            trilha.encerrar()
        self.assertFalse(trilha.disponivel)
        self.assertEqual(self.carregar_som.call_count, carregamentos)
        self.assertFalse(any(canal.ativo for canal in self.canais))

    def test_arquivo_ausente_nao_interrompe_o_jogo_nem_repete_o_aviso(self):
        def carregar(caminho):
            if caminho.endswith("01_entrada.mp3"):
                raise FileNotFoundError("arquivo ausente")
            return caminho
        self.carregar_som.side_effect = carregar
        with self.assertLogs("jogo.audio", level="WARNING") as avisos:
            trilha = TrilhaSonora()
            for _ in range(10):
                trilha.tocar_mapa("lobby")
                trilha.atualizar(1 / 60)
        self.assertEqual(len(avisos.output), 1)
        self.assertFalse(any(canal.ativo for canal in self.canais))


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
        self.assertTrue(pygame.mixer.get_busy())
        self.assertEqual(self.app.trilha.faixa_atual, "lobby")
        self.app.jogador.definir_posicao(8, 0)
        self.app._verificar_escada()
        self.app.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertTrue(pygame.mixer.Channel(0).get_busy())
        self.assertTrue(pygame.mixer.Channel(1).get_busy())
        self.assertAlmostEqual(
            pygame.mixer.Channel(0).get_volume(), VOLUME_MUSICA / 2 ** 0.5, delta=0.01
        )
        self.assertAlmostEqual(
            pygame.mixer.Channel(1).get_volume(), VOLUME_MUSICA / 2 ** 0.5, delta=0.01
        )
        self.app.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertFalse(pygame.mixer.Channel(0).get_busy())
        self.assertEqual(self.app.mundo.ident, "salao")
        self.assertEqual(self.app.trilha.faixa_atual, "salao")
        self.assertTrue(pygame.mixer.get_busy())
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
        self.assertFalse(pygame.mixer.get_busy())
        self.app._desenhar()
        self.assertLessEqual(
            self.app.fonte.size("Trilha sonora escrita por matewx_j")[0], 616
        )
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.app._eventos()
        self.assertFalse(self.app.vitoria)
        self.assertEqual(self.app.mundo.ident, "lobby")
        self.assertTrue(pygame.mixer.get_busy())

    def test_loop_principal_inicia_e_encerra_com_audio(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.app.executar()
        self.assertFalse(pygame.get_init())


if __name__ == "__main__":
    unittest.main()
