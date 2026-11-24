import os
import unittest
from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from jogo.aplicacao import Aplicacao
from jogo.arco import Flecha, Projetil
from jogo.blocos import BAU_ABERTO, BAU_FECHADO, SALAO_PAREDE
from jogo.lagarto import atualizar_lagarto, criar_lagarto, ferir_lagarto, retangulo_lagarto
from jogo.mapa import pode_andar


class CicloDoLagartoTest(unittest.TestCase):
    def test_mira_anunciada_permanece_fixa_ate_o_fim_da_rajada(self):
        chefe = criar_lagarto(8, 8)
        jogador = SimpleNamespace(x=160, y=320)
        self.assertEqual(atualizar_lagarto(chefe, 0.6, jogador), [])
        direcao = chefe["direcao"]
        jogador.y = 160
        atualizar_lagarto(chefe, 0.6, jogador)
        tiros = atualizar_lagarto(chefe, 0.8, jogador)
        self.assertEqual(len(tiros), 4)
        self.assertTrue(all(tiro[2] == direcao for tiro in tiros))
        self.assertEqual(chefe["estado"], "cooldown")
        self.assertEqual(atualizar_lagarto(chefe, 2.4, jogador), [])
        self.assertEqual(chefe["estado"], "preparacao")
        self.assertNotEqual(chefe["direcao"], direcao)

    def test_ciclo_e_quantidade_de_fogo_independem_da_taxa_de_quadros(self):
        for intervalos in ([4.4], [0.05] * 88, [1 / 60] * 264):
            with self.subTest(quadros=len(intervalos)):
                chefe = criar_lagarto(8, 8)
                jogador = SimpleNamespace(x=160, y=320)
                tiros = []
                for dt in intervalos:
                    tiros.extend(atualizar_lagarto(chefe, dt, jogador))
                self.assertEqual(len(tiros), 4)
                self.assertEqual(chefe["estado"], "preparacao")
                self.assertAlmostEqual(chefe["tempo_estado"], 0)

    def test_so_espada_no_cooldown_fere_e_golpes_seguidos_respeitam_protecao(self):
        chefe = criar_lagarto(8, 8)
        jogador = SimpleNamespace(x=160, y=320)
        for estado in ("preparacao", "ataque", "cooldown"):
            chefe["estado"] = estado
            self.assertFalse(ferir_lagarto(chefe, 1, "flecha"))
            self.assertEqual(chefe["vida"], 6)
            if estado != "cooldown":
                self.assertFalse(ferir_lagarto(chefe, 1, "espada"))
                self.assertEqual(chefe["vida"], 6)
        self.assertTrue(ferir_lagarto(chefe, 1, "espada"))
        self.assertFalse(ferir_lagarto(chefe, 1, "espada"))
        atualizar_lagarto(chefe, 0.5, jogador)
        self.assertTrue(ferir_lagarto(chefe, 1, "espada"))
        self.assertEqual(chefe["vida"], 4)

    def test_morto_nao_dispara_nem_recebe_dano(self):
        chefe = criar_lagarto(8, 8)
        chefe["estado"] = "cooldown"
        self.assertTrue(ferir_lagarto(chefe, 6, "espada"))
        self.assertFalse(ferir_lagarto(chefe, 1, "espada"))
        self.assertEqual(atualizar_lagarto(chefe, 30, SimpleNamespace(x=0, y=0)), [])
        self.assertEqual(chefe["estado"], "morto")
        self.assertEqual(chefe["vida"], 0)


class Sala5NoJogoTest(unittest.TestCase):
    def setUp(self):
        self.app = Aplicacao()
        self.arena = self.app.mundos["ala_leste"]
        self.app.mundo = self.arena
        self.app.jogador.definir_posicao(4, 8)
        self.teclas = defaultdict(bool)

    def tearDown(self):
        self.app.trilha.encerrar()
        pygame.quit()

    def pressionar(self, tecla):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))
        self.app._eventos()

    def entrar_no_covil(self):
        self.app.mundo = self.app.mundos["salao"]
        self.app.jogador.definir_posicao(15, 8)
        self.pressionar(pygame.K_f)
        self.app.jogador.definir_posicao(16, 8)
        self.app._verificar_escada()
        self.assertIs(self.app.mundo, self.arena)

    def derrotar(self):
        self.app.jogador.receber_itens(["Espada", "Chave de Prata"])
        self.entrar_no_covil()
        self.app.jogador.definir_posicao(7, 8)
        self.app.jogador.direcao_olhar = (1, 0)
        self.arena.chefe["estado"] = "cooldown"
        self.arena.chefe["vida"] = 1
        self.pressionar(pygame.K_SPACE)
        self.assertTrue(self.arena.chefe["morto"])

    def revisitar(self):
        self.app.jogador.definir_posicao(0, 8)
        self.app._verificar_escada()
        self.assertEqual(self.app.mundo.ident, "salao")
        self.assertEqual((self.app.jogador.grade_x, self.app.jogador.grade_y), (15, 8))
        self.app.jogador.definir_posicao(16, 8)
        self.app._verificar_escada()
        self.assertIs(self.app.mundo, self.arena)

    def fogo(self, x=320, y=320, direcao=(-1, 0)):
        return Projetil(x, y, direcao, dano=0.5, velocidade=240,
                        dono="lagarto", tipo_dano="fogo", tempo_vida=3)

    def test_prata_so_abre_a_porta_leste_ao_usar_f_ao_lado(self):
        salao = self.app.mundos["salao"]
        self.app.mundo = salao
        self.app.jogador.definir_posicao(15, 8)
        self.pressionar(pygame.K_f)
        self.assertFalse(self.app.jogador._comecar_passo(1, 0, self.app.mundo))
        self.app.jogador.definir_posicao(16, 8)
        self.app._verificar_escada()
        self.assertEqual(self.app.mundo.ident, "salao")
        self.app.mundo = self.app.mundos["labirinto"]
        self.app.jogador.definir_posicao(9, 8)
        self.pressionar(pygame.K_f)
        self.assertTrue(self.app.jogador.tem_chave_prata)
        self.app.mundo = salao
        self.app.jogador.definir_posicao(14, 8)
        self.pressionar(pygame.K_f)
        for y in (7, 8, 9):
            self.assertFalse(pode_andar(salao, 16, y, self.app.jogador))
        self.app.jogador.definir_posicao(15, 8)
        self.assertFalse(self.app.jogador._comecar_passo(1, 0, salao))
        self.pressionar(pygame.K_f)
        self.assertIs(self.app.mundo, salao)
        for y in (7, 8, 9):
            self.assertTrue(pode_andar(salao, 16, y, self.app.jogador))
        self.assertFalse(pode_andar(salao, 8, 0, self.app.jogador))
        self.assertTrue(self.app.jogador._comecar_passo(1, 0, self.app.mundo))
        self.app.jogador.atualizar(0.2, self.teclas, self.app.mundo)
        self.app._verificar_escada()
        self.assertIs(self.app.mundo, self.arena)
        self.assertEqual((self.app.jogador.grade_x, self.app.jogador.grade_y), (1, 8))
        jogador_area = pygame.Rect(self.app.jogador.x, self.app.jogador.y, 40, 40)
        self.assertFalse(jogador_area.colliderect(retangulo_lagarto(self.arena.chefe)))
        self.revisitar()

    def test_evento_de_espada_respeita_a_brecha_e_exibe_bloqueio(self):
        self.app.jogador.receber_itens(["Espada"])
        self.app.jogador.definir_posicao(7, 8)
        self.app.jogador.direcao_olhar = (1, 0)
        self.pressionar(pygame.K_SPACE)
        self.assertEqual(self.arena.chefe["vida"], 6)
        self.assertGreater(self.arena.chefe["tempo_bloqueio"], 0)
        self.app.jogador.atualizar(0.3, self.teclas, self.arena)
        atualizar_lagarto(self.arena.chefe, 2.0, self.app.jogador)
        self.pressionar(pygame.K_SPACE)
        self.assertEqual(self.arena.chefe["vida"], 5)

    def test_flecha_real_e_removida_ao_acertar_sem_ferir_o_chefe_na_brecha(self):
        self.app.jogador.receber_itens(["Arco"])
        self.app.jogador.definir_posicao(6, 8)
        self.arena.chefe["estado"] = "cooldown"
        self.pressionar(pygame.K_SPACE)
        flecha = self.app.flechas[0]
        self.app._atualizar_combate(0.25)
        self.assertFalse(flecha.ativa)
        self.assertEqual(self.app.flechas, [])
        self.assertEqual(self.arena.chefe["vida"], 6)
        self.assertGreater(self.arena.chefe["tempo_bloqueio"], 0)

    def test_fogo_causa_meio_coracao_e_invulnerabilidade_impede_dano_repetido(self):
        primeiro = self.fogo()
        self.app.flechas.append(primeiro)
        self.app._atualizar_combate(0.7)
        self.assertFalse(primeiro.ativa)
        self.assertEqual(self.app.jogador.vida, 2.5)
        self.assertGreater(self.app.jogador.tempo_invulneravel, 0)
        segundo = self.fogo(self.app.jogador.x, self.app.jogador.y)
        self.app.flechas.append(segundo)
        self.app._atualizar_combate(0)
        self.assertFalse(segundo.ativa)
        self.assertEqual(self.app.jogador.vida, 2.5)
        self.assertEqual(self.arena.chefe["vida"], 6)

    def test_sair_da_linha_anunciada_desvia_da_rajada_inteira(self):
        atualizar_lagarto(self.arena.chefe, 1.2, self.app.jogador)
        self.app.jogador.definir_posicao(4, 6)
        viu_fogo = False
        for _ in range(50):
            self.app._atualizar_combate(0.05)
            viu_fogo = viu_fogo or bool(self.app.flechas)
        self.assertTrue(viu_fogo)
        self.assertEqual(self.app.jogador.vida, 3)
        self.assertEqual(self.app.flechas, [])

    def test_projeteis_param_na_parede_e_no_limite_sem_atravessar_alvos(self):
        self.arena.grade[8][6] = SALAO_PAREDE
        flecha = Flecha(160, 320, (1, 0))
        flecha.atualizar(0.6, self.arena, [], self.app.jogador, self.arena.chefe)
        self.assertFalse(flecha.ativa)
        self.assertLess(flecha.x, 280)
        self.assertEqual(self.arena.chefe["vida"], 6)
        fora = self.fogo(600, 320, (1, 0))
        fora.atualizar(0.8)
        self.assertFalse(fora.ativa)

    def test_flecha_continua_ferindo_inimigos_comuns_sem_acertar_o_jogador(self):
        salao = self.app.mundos["salao"]
        inimigo = salao.inimigos[0]
        flecha = Flecha(240, 160, (0, 1))
        flecha.atualizar(0.3, salao, [inimigo], self.app.jogador)
        self.assertFalse(flecha.ativa)
        self.assertEqual(inimigo.vida, 2)
        self.assertEqual(self.app.jogador.vida, 3)

    def test_morte_limpa_fogo_desativa_contato_e_cria_um_bau_alcancavel(self):
        fogo = self.fogo()
        self.app.flechas.append(fogo)
        self.derrotar()
        self.assertFalse(fogo.ativa)
        self.assertEqual(self.app.flechas, [])
        self.assertEqual(self.arena.baus, {(12, 8): ["Chave Dourada"]})
        self.assertEqual(self.arena.grade[8][12], BAU_FECHADO)
        self.assertTrue(pode_andar(self.arena, 11, 8, self.app.jogador))
        self.app.jogador.definir_posicao(8, 8)
        self.app._atualizar_combate(20)
        self.assertEqual(self.app.jogador.vida, 3)
        self.assertEqual(len(self.arena.baus), 1)
        self.assertEqual(self.app.flechas, [])

    def test_revisita_preserva_derrota_e_chave_unica_que_deve_ser_usada_no_norte(self):
        self.derrotar()
        self.revisitar()
        self.assertTrue(self.arena.chefe["morto"])
        self.assertEqual(self.arena.grade[8][12], BAU_FECHADO)
        self.app.jogador.definir_posicao(11, 8)
        self.pressionar(pygame.K_f)
        self.pressionar(pygame.K_f)
        self.assertTrue(self.app.jogador.tem_chave_dourada)
        self.revisitar()
        self.assertEqual(self.arena.grade[8][12], BAU_ABERTO)
        self.app.jogador.definir_posicao(11, 8)
        self.pressionar(pygame.K_f)
        self.assertEqual(self.app.jogador.inventario.count("Chave Dourada"), 1)
        self.app.jogador.definir_posicao(0, 8)
        self.app._verificar_escada()
        salao = self.app.mundo
        self.app.jogador.definir_posicao(8, 0)
        self.app._verificar_escada()
        self.assertIs(self.app.mundo, salao)
        self.app.jogador.definir_posicao(9, 1)
        # Deixa passar a animação do último golpe antes de tentar andar.
        self.app.jogador.atualizar(0.3, self.teclas, salao)
        self.assertFalse(self.app.jogador._comecar_passo(0, -1, salao))
        self.pressionar(pygame.K_f)
        self.assertIs(self.app.mundo, salao)
        for x in (7, 8, 9):
            self.assertTrue(pode_andar(salao, x, 0, self.app.jogador))
        self.assertTrue(self.app.jogador._comecar_passo(0, -1, salao))
        self.app.jogador.atualizar(0.2, self.teclas, salao)
        self.app._verificar_escada()
        self.assertEqual(self.app.mundo.ident, "torre")
        self.assertEqual((self.app.jogador.grade_x, self.app.jogador.grade_y), (8, 15))
        torre = self.app.mundo
        self.assertTrue(self.app.jogador._comecar_passo(0, 1, torre))
        self.app.jogador.atualizar(0.2, self.teclas, torre)
        self.app._verificar_escada()
        self.assertIs(self.app.mundo, salao)
        self.assertEqual((self.app.jogador.grade_x, self.app.jogador.grade_y), (8, 1))

    def test_chave_de_prata_nao_abre_a_porta_norte(self):
        self.app.mundo = self.app.mundos["salao"]
        self.app.jogador.receber_itens(["Chave de Prata"])
        self.app.jogador.definir_posicao(8, 1)
        self.pressionar(pygame.K_f)
        self.assertFalse(pode_andar(self.app.mundo, 8, 0, self.app.jogador))
        self.app.jogador.definir_posicao(8, 0)
        self.app._verificar_escada()
        self.assertEqual(self.app.mundo.ident, "salao")

    def test_inventario_cheio_nao_perde_a_recompensa(self):
        self.derrotar()
        self.app.jogador.receber_itens(["Arco", "Cajado Mágico", "Outro item"])
        self.app.jogador.definir_posicao(11, 8)
        self.pressionar(pygame.K_f)
        self.assertEqual(self.arena.grade[8][12], BAU_FECHADO)
        self.assertFalse(self.app.jogador.tem_chave_dourada)
        self.app.jogador.inventario.pop()
        self.pressionar(pygame.K_f)
        self.assertTrue(self.app.jogador.tem_chave_dourada)

    def test_troca_de_sala_remove_projeteis_sem_reiniciar_o_ciclo(self):
        self.app.jogador.receber_itens(["Chave de Prata"])
        self.entrar_no_covil()
        atualizar_lagarto(self.arena.chefe, 1.5, self.app.jogador)
        fogo = self.fogo()
        self.app.flechas.append(fogo)
        self.revisitar()
        self.assertFalse(fogo.ativa)
        self.assertEqual(self.app.flechas, [])
        self.assertEqual(self.arena.chefe["estado"], "ataque")
        self.assertAlmostEqual(self.arena.chefe["tempo_estado"], 0.3)

    def test_restart_restaura_arena_recompensa_itens_e_todos_os_cronometros(self):
        self.derrotar()
        self.app.jogador.definir_posicao(11, 8)
        self.pressionar(pygame.K_f)
        self.app.jogador.definir_posicao(0, 8)
        self.app._verificar_escada()
        self.app.jogador.definir_posicao(8, 1)
        self.pressionar(pygame.K_f)
        self.assertTrue(pode_andar(self.app.mundo, 8, 0, self.app.jogador))
        fogo = self.fogo()
        self.app.flechas.append(fogo)
        self.app._reiniciar()
        nova_arena = self.app.mundos["ala_leste"]
        self.assertIsNot(nova_arena, self.arena)
        self.assertEqual(nova_arena.chefe, criar_lagarto(8, 8))
        self.assertEqual(nova_arena.baus, {})
        self.assertNotEqual(nova_arena.grade[8][12], BAU_FECHADO)
        self.assertFalse(fogo.ativa)
        self.assertEqual(self.app.flechas, [])
        self.assertEqual(self.app.jogador.inventario, [])
        self.assertFalse(self.app.jogador.tem_chave_prata)
        self.assertFalse(self.app.jogador.tem_chave_dourada)
        salao = self.app.mundos["salao"]
        self.assertFalse(pode_andar(salao, 16, 8, self.app.jogador))
        self.assertFalse(pode_andar(salao, 8, 0, self.app.jogador))

    def test_game_over_remove_todos_os_projeteis(self):
        self.app.jogador.vida = 0.5
        fogo = self.fogo(self.app.jogador.x, self.app.jogador.y)
        outro = self.fogo()
        self.app.flechas.extend([fogo, outro])
        self.app._atualizar_combate(0)
        self.assertTrue(self.app.jogador.game_over)
        self.assertFalse(outro.ativa)
        self.assertEqual(self.app.flechas, [])

    def test_loop_principal_atualiza_projeteis_e_inventario_pausa_o_combate(self):
        self.app.jogador.receber_itens(["Arco"])
        self.app.jogador.definir_posicao(6, 8)
        self.arena.chefe["estado"] = "cooldown"
        self.pressionar(pygame.K_SPACE)
        flecha = self.app.flechas[0]
        quadros = 0

        def observar():
            nonlocal quadros
            quadros += 1
            if quadros == 5:
                self.assertFalse(flecha.ativa)
                self.app.inventario_aberto = True
            elif quadros == 10:
                self.assertAlmostEqual(self.arena.chefe["tempo_estado"], 0.25)
                self.app.rodando = False

        with patch.object(self.app, "clock") as clock, patch.object(self.app, "_desenhar", side_effect=observar):
            clock.tick.return_value = 50
            self.app.executar()
        self.assertEqual(quadros, 10)


if __name__ == "__main__":
    unittest.main()
