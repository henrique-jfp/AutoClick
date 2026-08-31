# ⚡ Auto Clicker Pro & Key Presser

Um utilitário moderno, completo e de alta performance para automação de teclas do teclado e cliques do mouse no Windows, projetado para jogos e produtividade.

---

## ✨ Principais Funcionalidades

### 1. 🔤 Sequência de Teclas Exatas / Macros (NOVO!)
- **Combos e Sequências Ilimitadas:** Além de uma única tecla ou clique do mouse, agora você pode definir **sequências exatas de teclas** de qualquer tamanho!
- **Como configurar:** Clique no novo botão **`🔤 Sequência (Macro)`** na Seção 1 e digite as teclas separadas por vírgula ou espaço (ex: `F, F, ESPAÇO` ou `1, 2, 3, 4` ou `E, Q, F`).
- Ao ativar, o aplicativo dispara a sequência completa de teclas em ordem com o tempo/jitter configurado.
- Você pode salvar qualquer sequência como um **Botão Rápido** em qualquer jogo!

### 2. 🖥️ Modo Barrinha Flutuante (Mini Overlay sem Alt+Tab)
- **Troca de Presets em Tempo Real no Jogo:** Clique no botão **`🖥️ BARRINHA FLUTUANTE`** no topo da tela para transformar a interface em uma barra horizontal pequena e flutuante.
- **Sempre no Topo da Tela:** A barrinha fica fixada por cima do Genshin Impact ou de qualquer outro jogo em tela cheia / janela sem bordas.
- **Botões Rápidos do Jogo Atual:** Exibe apenas os botões de presets do jogo ativo (ex: `[ ⚔️ Diálogo ]`, `[ 🏹 Ataque ]`, `[ 📜 Combo F,F,Espaço ]`) + botão de ligar/desligar `[ 🔴 PARADO (F6) ]`.
- **Arrastável:** Clique e segure no ícone `⣿` para mover a barrinha para qualquer canto da sua tela!

### 3. 🎮 Perfis por Jogo & Botões Rápidos Dinâmicos
- **Abas de Jogos:** Alterne facilmente entre os perfis de cada jogo pelas abas principais (ex: `[ 🎮 Genshin Impact ]`, `[ ⛏️ Minecraft ]`, `[ 🧱 Roblox ]`).
- **Botões Rápidos Instantâneos:** Cada jogo exibe sua própria linha de botões rápidos. Clicar em qualquer botão carrega instantaneamente a configuração do preset!
- **➕ Criar Novo Jogo:** Adicione novos jogos/categorias com 1 clique (ex: `🎮 Valorant`, `🚀 GTA V`, `⚔️ Elden Ring`).
- **➕ Adicionar Preset no Jogo:** Ao configurar os parâmetros desejados (tecla, sequência, ms, jitter, posição fixa X/Y), clique em **`➕ Adicionar Preset`** para criar um novo botão rápido!

### 4. 🎯 Tecla Alvo & Atalho Global Personalizável
- **Captura Unificada**: Escolha qualquer tecla do teclado, botões do mouse (`Clique Esquerdo`, `Direito`, `Clique Duplo`, `Clique Meio`, `Mouse 4 / X1`, `Mouse 5 / X2`) ou uma **Sequência Macro**.
- **Atalho Global Customizável**: Altere a tecla de Ligar/Desligar instantaneamente (Padrão: **F6**).

### 5. 🔄 Modos de Funcionamento & Anti-Cheat
- **Modo Repetição (Spam)**: Repete a ação com intervalo customizável em milissegundos.
- **🎲 Modo Humano (Jitter)**: Adiciona variação aleatória de tempo (ex: 50ms $\pm$ 5ms) para evitar padrões fixos e bypassar detecções anti-bot em jogos.
- **✊ Modo Segurar (Hold)**: Mantém a tecla pressionada continuamente com pulsos de alta fidelidade.

### 6. 📍 Posição do Clique
- **Posição Atual do Cursor**: Clica exatamente onde o ponteiro do mouse estiver.
- **🎯 Posição Fixa `(X, Y)`**: Define coordenadas fixas na tela com botão de **Captura Automática (3s)**.

### 7. ⏱️ Condições de Parada Automática
- **Limite por Cliques**: Parar automaticamente após $N$ cliques.
- **Limite por Tempo**: Parar automaticamente após $X$ segundos de execução.

### 8. 📊 Painel de Estatísticas em Tempo Real
- Exibe o **Contador Total de Cliques**, o indicador **CPS** (*Clicks Per Second*) em tempo real e o tempo decorrido de execução.

### 9. 📌 Opções & Integração com o Windows
- **📌 Sempre no Topo**: Fixa a janela por cima de outros aplicativos ou jogos.
- **🔔 Feedback Sonoro**: Emite um aviso sonoro sutil (*beep*) ao ativar/desativar.
- **📥 Ocultar na Bandeja (System Tray)**: Minimiza para a área de notificação do Windows perto do relógio (`pystray`).
- **🛡️ Verificação de Administrador**: Botão automático para reiniciar como Administrador (necessário para jogos com anti-cheat elevado como Genshin Impact).
- **⚡ High-Precision Timer**: Utiliza a API do Windows (`winmm.dll`) com precisão de 1ms.

---

## 🚀 Como Usar

### Opção 1: Usando o Executável (.exe)
1. Abra o arquivo `dist/AutoClicker.exe`.
2. Para criar uma sequência de teclas, clique em **`🔤 Sequência (Macro)`** e digite as teclas (ex: `F, F, ESPAÇO`).
3. Para salvar como botão rápido no seu jogo, clique em **`➕ Adicionar Preset`**.
4. Use o botão **`🖥️ BARRINHA FLUTUANTE`** para jogar com uma mini barrinha sobreposta na tela sem precisar de Alt+Tab!

### Opção 2: Executando via Python
```bash
python autoclicker.py
```

---

## 🔨 Como Gerar o Executável (.exe)

Para gerar a versão compilada executando PyInstaller com ícone personalizado:

```bash
python build_exe.py
```

O executável final estará pronto em `dist/AutoClicker.exe`.
