# Guia de Git para a Equipe

Este guia reúne o fluxo de trabalho padrão do nosso repositório para que todos possam desenvolver novas funcionalidades e correções sem sobrescrever o código dos colegas.

---

## 1. Como Trabalhamos no Repositório

* **Nunca faça alterações diretamente na branch `main`:** A `main` guarda apenas a versão estável e testada do jogo.
* **Cada tarefa tem sua própria branch:** Antes de escrever código, você cria uma ramificação (`branch`) separada a partir da `main`.
* **Padrão de nomes para branches:** Não use espaços nem acentos. Utilize prefixos seguidos de hífen (`-`):
  * `feat/nome-da-funcao` para novas mecânicas (ex: `feat/bau-e-inventario`).
  * `fix/nome-do-ajuste` para correções de bugs ou ajustes (ex: `fix/colisao-buraco`).

---

## 2. Atualizando a `main` Antes de Começar

Sempre que for iniciar uma tarefa nova, garanta que a sua cópia local da `main` está sincronizada com o GitHub:

```bash
git checkout main
git pull origin main
```

* `git checkout main`: muda você para a branch principal.
* `git pull origin main`: baixa todas as atualizações recentes que a equipe enviou para o GitHub.

---

## 3. Criando e Trocando de Branch

Com a `main` atualizada, crie a sua branch de trabalho:

```bash
git checkout -b feat/nome-da-sua-tarefa
```

O comando `-b` cria a branch e já troca automaticamente para ela. Durante o dia a dia, você também pode usar:

* **Ver em qual branch você está** (a ativa aparece marcada com um `*`):
  ```bash
  git branch
  ```

* **Trocar para uma branch que já existe na sua máquina:**
  ```bash
  git checkout nome-da-branch
  ```

---

## 4. Salvando e Enviando Alterações (`commit` e `push`)

Depois de programar e testar o jogo com `python main.py`, siga os quatro passos abaixo para registrar e enviar seu trabalho:

1. **Conferir os arquivos alterados:**
   ```bash
   git status
   ```
   Verifique se apenas os arquivos que você realmente editou aparecem na lista (pastas como `.venv` e `__pycache__` são ignoradas automaticamente pelo `.gitignore`).

2. **Preparar os arquivos para o registro:**
   ```bash
   git add .
   ```
   *(Para adicionar apenas um arquivo específico em vez de todos, use `git add caminho/do/arquivo.py`.)*

3. **Salvar o ponto de histórico (`commit`):**
   ```bash
   git commit -m "feat: descreva de forma curta o que voce fez"
   ```

4. **Enviar a branch para o GitHub (`push`):**
   ```bash
   git push -u origin feat/nome-da-sua-tarefa
   ```
   *(A opção `-u` vincula sua branch local ao GitHub na primeira vez. Nos próximos commits dentro da mesma branch, basta rodar `git push`.)*

---

## 5. Atualizando sua Branch com Novidades da `main`

Se algum colega concluir uma tarefa e atualizar a `main` enquanto você ainda está trabalhando na sua branch, você pode puxar essas novidades para o seu código sem perder o que já fez:

```bash
git pull origin main
```

Caso o Git abra um editor de texto no terminal pedindo uma mensagem de confirmação (*merge*), basta digitar `:wq` e pressionar `Enter` (no editor Vim) ou fechar a aba do arquivo de mensagem caso ela abra no VS Code.

---

## 6. Finalizando a Tarefa (Pull Request)

Quando sua funcionalidade estiver pronta e enviada com `git push`:

1. Acesse a página do repositório no GitHub (`https://github.com/MateusJuan/jogo_ip`).
2. Clique no aviso **"Compare & pull request"** que aparece no topo da página.
3. Escreva um resumo do que foi alterado e clique em **"Create pull request"** para que a equipe revise e integre seu código na `main`.