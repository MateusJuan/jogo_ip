# Como Configurar e Rodar o Jogo

Este guia explica como preparar o ambiente, resolver conflitos de versão do Python e executar o **Lost Ruins: Hords of Doom** na sua máquina.

---

## 1. Pré-requisitos e Compatibilidade do Python

Antes de começar, você precisa ter instalados no computador:
* **Git** (para baixar e enviar atualizações do código).
* **Python 3.12 ou Python 3.13** (recomendado).

### Por que a versão do Python importa?
Este projeto utiliza a biblioteca `pygame` (definida em `requirements.txt`).
* **Python 3.12 e 3.13:** São as versões recomendadas. O `pygame==2.6.1` já possui instaladores prontos (pré-compilados) para elas, então a instalação leva apenas alguns segundos.
* **Python 3.14 ou superior:** Versões muito recentes costumam não ter instalador pronto para o `pygame` padrão. Quando você tenta instalar nesses casos, o Python tenta compilar a biblioteca do zero em linguagem C e falha com erro no terminal.

> **Dica de instalação no Windows:** Ao instalar o Python pelo instalador oficial, sempre marque a caixa **"Add python.exe to PATH"** na primeira tela.

Para verificar quais versões do Python estão instaladas no seu Windows, abra o terminal e digite:

```bash
py --list
```

---

## 2. Baixando o Repositório

Abra o terminal (PowerShell, Prompt de Comando ou Git Bash) na pasta onde você costuma salvar seus projetos e clone o repositório:

```bash
git clone [https://github.com/MateusJuan/jogo_ip.git](https://github.com/MateusJuan/jogo_ip.git)
cd jogo_ip
```

---

## 3. Criando e Ativando o Ambiente Virtual (`.venv`)

O ambiente virtual (`.venv`) cria uma pasta isolada dentro do projeto para guardar as bibliotecas necessárias sem interferir em outros programas do seu computador.

Dentro da pasta `jogo_ip`, crie o ambiente virtual escolhendo a versão compatível instalada na sua máquina:

```powershell
# Se você tem Python 3.13 instalado:
py -3.13 -m venv .venv

# Ou, se você tem Python 3.12 instalado:
py -3.12 -m venv .venv
```

Após criar a pasta `.venv`, você precisa **ativá-la** toda vez que abrir um novo terminal para trabalhar no jogo:

* **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(Caso o PowerShell exiba um erro de permissão de execução de scripts, rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` uma única vez, confirme com `S` e tente ativar novamente.)*

* **Windows (Prompt de Comando / CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

* **Linux ou macOS:**
  ```bash
  source .venv/bin/activate
  ```

Quando a ativação funcionar, o prefixo `(.venv)` aparecerá no início da linha do seu terminal.

---

## 4. Instalando as Dependências

Com o `(.venv)` ativo, instale as bibliotecas listadas no `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

### Solução alternativa (caso você só tenha Python 3.14 ou superior)
Se o comando acima falhar por incompatibilidade de versão e você não puder instalar o Python 3.13 no momento, instale o `pygame-ce` (edição comunitária mantida com suporte antecipado às novas versões do Python e que funciona com o mesmo código `import pygame`):

```bash
python -m pip install pygame-ce
```

*(Importante: nunca instale `pygame` e `pygame-ce` juntos no mesmo `.venv`. Se precisar trocar de um para o outro, remova o anterior antes com `python -m pip uninstall pygame`.)*

---

## 5. Executando o Jogo

Com o ambiente virtual ativo e dentro da pasta `jogo_ip`, inicie o jogo pelo arquivo principal:

```bash
python main.py
```

* **Controles:** Use `W`, `A`, `S`, `D` ou as **setas direcionais** para andar pelo castelo.
* **Navegação:** Pise nas escadas ao norte para subir de andar e ao sul para retornar ao andar anterior.
* **Encerrar:** Feche a janela no botão `X` para encerrar o programa com segurança.

---

## 6. Configurando o VS Code ou Cursor

O repositório já inclui o arquivo `.vscode/settings.json` configurado para reconhecer o ambiente virtual. Caso o editor sublinhe `import pygame` como não encontrado:

1. Pressione `Ctrl + Shift + P` para abrir a paleta de comandos.
2. Digite e selecione **`Python: Select Interpreter`**.
3. Escolha o interpretador que aponta para **`.venv\Scripts\python.exe`**.