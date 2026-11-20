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
        self.som_atual = None
        self.inicios = []
        self.volumes_ao_iniciar = []
        self.paradas = []

    def set_volume(self, volume):
        self.volume = volume

    def get_busy(self):
        return self.ativo

    def play(self, som, loops):
        self.ativo = True
        self.som_atual = som
        self.inicios.append((som, loops))
        self.volumes_ao_iniciar.append(self.volume)

    def stop(self):
        self.paradas.append((self.som_atual, self.volume))
        self.ativo = False
        self.som_atual = None


class ControleDeTrilhasTest(unittest.TestCase):
    def setUp(self):
        self.canais = [CanalSimulado(), CanalSimulado()]
        self.canal = self.canais[0]
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
        self.trilha.tocar_mapa("lobby", reiniciar=True)
        self.trilha.atualizar(TEMPO_TRANSICAO)

    def test_repetir_pedido_do_mapa_nao_reinicia_a_musica(self):
        self.iniciar_entrada()
        for _ in range(90):
            self.trilha.tocar_mapa("lobby")
            self.trilha.atualizar(1 / 60)
        self.assertEqual(self.canal.inicios, [(str(PASTA_MUSICAS / "01_entrada.mp3"), -1)])
        self.assertEqual(self.canal.volume, VOLUME_MUSICA)
        self.assertEqual(self.carregar_som.call_count, 2)

    def test_proxima_faixa_so_comeca_apos_zerar_e_parar_a_atual(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.assertEqual(len(self.canal.inicios), 1)
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertEqual(len(self.canal.inicios), 1)
        self.assertEqual(self.trilha.faixa_atual, "lobby")
        self.assertAlmostEqual(self.canal.volume, VOLUME_MUSICA / 2)
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertEqual(self.canal.paradas[-1], (str(PASTA_MUSICAS / "01_entrada.mp3"), 0.0))
        self.assertEqual(self.canal.inicios[-1], (str(PASTA_MUSICAS / "02_salao.mp3"), -1))
        self.assertEqual(self.canal.volumes_ao_iniciar[-1], 0.0)
        self.assertEqual(self.canal.volume, 0.0)
        self.assertEqual(self.trilha.faixa_atual, "salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertAlmostEqual(self.canal.volume, VOLUME_MUSICA / 2)
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertEqual(self.canal.volume, VOLUME_MUSICA)
        self.musica_stream.fadeout.assert_not_called()
        self.assertEqual(self.carregar_som.call_count, 2)

    def test_volume_gradual_limitado_e_sem_sobreposicao(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        for _ in range(180):
            antes = self.canal.volume
            self.trilha.atualizar(TEMPO_TRANSICAO / 180)
            self.assertLessEqual(abs(self.canal.volume - antes), 0.01)
            self.assertTrue(all(0 <= c.volume <= VOLUME_MUSICA for c in self.canais))
            self.assertLessEqual(sum(c.ativo for c in self.canais), 1)
        self.assertEqual(self.trilha.faixa_atual, "salao")
        self.assertAlmostEqual(self.canal.volume, VOLUME_MUSICA)

    def test_curva_comeca_gradualmente_e_troca_no_meio_dos_tres_segundos(self):
        self.assertEqual(TEMPO_TRANSICAO, 3.0)
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(1 / 60)
        self.assertGreater(self.canal.volume, VOLUME_MUSICA - 0.001)
        self.assertEqual(len(self.canal.inicios), 1)
        self.trilha.atualizar(TEMPO_TRANSICAO / 2 - 1 / 60)
        self.assertEqual(self.canal.volume, 0.0)
        self.assertEqual(len(self.canal.inicios), 2)
        self.trilha.atualizar(1 / 60)
        self.assertLess(self.canal.volume, 0.001)

    def test_voltar_antes_do_silencio_cancela_a_troca_sem_reiniciar(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        antes = self.canal.volume
        self.trilha.tocar_mapa("lobby")
        self.assertEqual(self.canal.volume, antes)
        self.trilha.atualizar(0)
        self.assertEqual(self.canal.volume, antes)
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.trilha.faixa_atual, "lobby")
        self.assertEqual(len(self.canal.inicios), 1)
        self.assertEqual(self.canal.volume, VOLUME_MUSICA)

    def test_parar_durante_a_saida_cancela_a_faixa_pendente(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.trilha.parar()
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertFalse(self.canal.ativo)
        self.assertEqual(self.canal.volume, 0.0)
        self.assertIsNone(self.trilha.faixa_atual)
        self.assertEqual(len(self.canal.inicios), 1)

    def test_parar_durante_a_entrada_diminui_a_faixa_ativa(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(3 * TEMPO_TRANSICAO / 4)
        self.assertEqual(self.trilha.faixa_atual, "salao")
        antes = self.canal.volume
        self.trilha.parar()
        self.assertEqual(self.canal.volume, antes)
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertAlmostEqual(self.canal.volume, antes / 2)
        self.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertFalse(self.canal.ativo)
        self.assertEqual(len(self.canal.inicios), 2)

    def test_resultado_independe_do_tamanho_dos_quadros(self):
        for intervalos in ([TEMPO_TRANSICAO], [0.1] * 30, [1 / 60] * 180):
            with self.subTest(intervalos=len(intervalos)):
                self.iniciar_entrada()
                self.trilha.tocar_mapa("salao")
                for dt in intervalos:
                    self.trilha.atualizar(dt)
                self.assertEqual(self.trilha.faixa_atual, "salao")
                self.assertAlmostEqual(self.canal.volume, VOLUME_MUSICA)

    def test_mapas_em_desenvolvimento_nao_recebem_trilhas(self):
        for mapa in ("galeria", "torre", "ala_leste", "ala_oeste"):
            with self.subTest(mapa=mapa):
                self.iniciar_entrada()
                quantidade_inicios = len(self.canal.inicios)
                self.trilha.tocar_mapa(mapa)
                self.trilha.atualizar(TEMPO_TRANSICAO)
                self.assertIsNone(self.trilha.faixa_atual)
                self.assertFalse(any(c.ativo for c in self.canais))
                self.assertEqual(len(self.canal.inicios), quantidade_inicios)
        self.assertEqual(self.carregar_som.call_count, 2)

    def test_reiniciar_repete_a_entrada_desde_o_comeco_em_volume_zero(self):
        self.iniciar_entrada()
        self.trilha.tocar_mapa("salao")
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.trilha.tocar_mapa("lobby", reiniciar=True)
        self.assertEqual(self.canal.volumes_ao_iniciar, [0.0, 0.0, 0.0])
        self.assertEqual(self.canal.volume, 0.0)
        self.trilha.atualizar(TEMPO_TRANSICAO)
        self.assertEqual(self.trilha.faixa_atual, "lobby")
        self.assertEqual(self.canal.volume, VOLUME_MUSICA)

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
        self.assertFalse(any(c.ativo for c in self.canais))

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
        self.assertFalse(any(c.ativo for c in self.canais))


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
        self.app.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertTrue(pygame.mixer.Channel(0).get_busy())
        self.assertFalse(pygame.mixer.Channel(1).get_busy())
        self.assertEqual(self.app.trilha.faixa_atual, "lobby")
        self.assertAlmostEqual(pygame.mixer.Channel(0).get_volume(), VOLUME_MUSICA / 2, delta=0.01)
        self.app.trilha.atualizar(TEMPO_TRANSICAO / 4)
        self.assertEqual(self.app.mundo.ident, "salao")
        self.assertEqual(self.app.trilha.faixa_atual, "salao")
        self.assertEqual(pygame.mixer.Channel(0).get_volume(), 0.0)
        self.assertEqual(pygame.mixer.Channel(0).get_sound(), self.app.trilha._sons["salao"])
        self.assertFalse(pygame.mixer.Channel(1).get_busy())
        self.app.trilha.atualizar(TEMPO_TRANSICAO / 2)
        self.assertAlmostEqual(pygame.mixer.Channel(0).get_volume(), VOLUME_MUSICA, delta=0.01)
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
