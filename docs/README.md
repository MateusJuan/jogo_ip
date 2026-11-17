# Lost Ruins: Hords of Doom

Jogo de exploração de masmorra (*dungeon crawler*) desenvolvido para a disciplina de **Introdução à Programação**. O personagem nasce no **Lobby** (pátio das ruínas) e sobe os andares do castelo através de escadas até alcançar o topo.

## Andares do Castelo

1. **Lobby:** Pátio inicial aberto com escada ao norte.
2. **Andar 1 – Salão:** Sala interna com obstáculos de entulho e acesso para o andar superior e inferior.
3. **Andar 2 – Galeria:** Sala com abismos no piso e caminho estreito até a próxima escada.
4. **Andar 3 – Torre:** Topo do castelo com pilares e altar central.

## Controles e Mecânicas Implementadas

* **Movimentação (`W A S D` ou `Setas`):** Deslize suave alinhado à grade de `17x17` células.
* **Animações do personagem:** Corrida lateral com os 10 quadros de `corrida_direita.png` e respiração com os 16 quadros de `respiracao_direita.png`, enviados por SrFaisca. As sequências são espelhadas para a esquerda. Ao parar, o personagem respira virado para o último lado escolhido, inclusive após descer ou virar junto a uma parede. A subida usa `caminhada_costas.png`, e a parada nessa direção mantém a pose de costas.
* **Transição de Andares:** Pisar nas escadas ao norte (sobe) ou ao sul (desce) transporta o personagem para o próximo mapa.
* **Sistema de Vida (HUD):** Barra superior esquerda com **3 corações** (suportando dano de `0.5` coração).
* **Invulnerabilidade e Hitstun:** Ao sofrer dano, o personagem pisca enquanto está invulnerável e fica momentaneamente paralisado pelo impacto.
* **Queda em Buracos:** Na Galeria, pisar em um buraco desconta `0.5` coração, paralisa o jogador por `1.0s` e o devolve para uma célula segura antes da beirada.

## Padrão de Código (Restrições da Disciplina)

Todo o código segue estritamente as permissões das listas de Introdução à Programação:
* **Sem classes, `sets`, `None`, `break` ou `continue`.**
* Entidades como o jogador, os mapas e a aplicação são representadas por **dicionários** manipulados por funções puras.

## Estrutura do Projeto

| Arquivo / Pasta | Função |
| :--- | :--- |
| `main.py` | Ponto de entrada que inicia o loop principal do jogo. |
| `COMO_RODAR.md` | Passo a passo de instalação e solução de problemas de versão do Python. |
| `GUIA_GIT.md` | Comandos essenciais de Git para a equipe trabalhar em branches separadas. |
| `requirements.txt` | Dependência externa do projeto (`pygame`). |
| `assets/` | Texturas `.png` dos pisos, paredes, obstáculos e personagem. |
| `assets/movimento_jogador/` | Animações `corrida_direita.png`, `respiracao_direita.png` e `caminhada_costas.png`; poses estáticas `parado_direita.png` e `parado_costas.png`. As versões para a esquerda são geradas pelo jogo. |
| `jogo/aplicacao.py` | Janela, relógio (`FPS`), loop principal, troca de andares e desenho do HUD. |
| `jogo/configuracoes.py` | Dimensões da tela e da matriz (`17x17`), velocidade, FPS e caminho dos assets. |
| `jogo/blocos.py` | Códigos numéricos dos terrenos, listas de obstáculos/buracos e mapa de imagens. |
| `jogo/recursos.py` | Carregamento e redimensionamento das imagens da pasta `assets/`. |
| `jogo/mapa.py` | Verificação de colisão, detecção de buracos e renderização da grade e escadas. |
| `jogo/mundos.py` | Construção das matrizes e ligações de escadas dos 4 andares. |
| `jogo/jogador.py` | Estado do personagem, movimentação na grade, dano, piscar e histórico de passos seguros. |

## Como Começar

* Para instalar e abrir o jogo na sua máquina, siga o **[COMO_RODAR.md](COMO_RODAR.md)**.
* Para enviar suas alterações para o GitHub sem conflitos, siga o **[GUIA_GIT.md](GUIA_GIT.md)**.
