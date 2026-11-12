# Lost Ruins: Hords of Doom

O personagem nasce no lobby, o pátio das ruínas, e sobe o castelo por uma escada. Cada andar é um mapa com chão e obstáculos próprios. A ordem é Lobby, Salão, Galeria e Torre. A Torre é o último andar.

Para instalar e abrir o jogo, siga o `comoRodar.txt`.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `main.py` | Ponto de entrada. Só cria a aplicação e inicia o jogo. |
| `comoRodar.txt` | Passo a passo para a equipe configurar a máquina e rodar o jogo. |
| `requirements.txt` | Dependência do projeto. Hoje é o pygame 2.6.1. |
| `README.md` | Este arquivo. Explica o que cada parte do repositório faz. |
| `.vscode/settings.json` | Aponta o editor para o interpretador do ambiente `.venv`. |

## Pacote `jogo`

| Arquivo | Função |
| --- | --- |
| `jogo/__init__.py` | Marca a pasta `jogo` como um pacote Python. Não tem código. |
| `jogo/aplicacao.py` | Janela, relógio e loop principal. Troca de andar quando o personagem pisa numa escada e desenha o nome do piso. |
| `jogo/configuracoes.py` | Tamanho do mapa, da célula e da janela, FPS, velocidade do personagem, título e caminho da pasta `assets`. |
| `jogo/jogador.py` | Movimento suave de célula em célula, teclas e posição do personagem. |
| `jogo/mapa.py` | Decide se uma célula pode ser pisada e desenha o andar, inclusive as escadas. |
| `jogo/mundos.py` | Monta os quatro mapas e liga a escada de cada um ao andar de cima ou de baixo. |
| `jogo/blocos.py` | Números de cada tipo de bloco, quais bloqueiam o passo e qual imagem cada um usa. |
| `jogo/recursos.py` | Carrega e redimensiona as imagens da pasta `assets`. |

## Pasta `assets`

Imagens usadas pelo jogo. O piso e os muros de cada andar têm arquivos próprios. O personagem está em `personagem.png`. A grama do lobby está em `grama.png` e o muro do lobby em `muro.png`.
