<div align="center">
  <img src="app_icon.png" alt="Auto Clicker Pro Logo" width="128"/>
  <h1>Auto Clicker Pro & Key Presser ⚡</h1>
  <p><strong>A automação de mouses e teclados mais avançada e premium, construída em Python.</strong></p>
  
  [![Release](https://img.shields.io/github/v/release/henrique-jfp/AutoClick?color=3ECF8E&style=for-the-badge)](https://github.com/henrique-jfp/AutoClick/releases)
  [![Python](https://img.shields.io/badge/Python-3.12-5B8CFF?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
</div>

<br/>

O **Auto Clicker Pro** não é só mais um clicador genérico. Ele foi desenhado do zero para ter uma interface moderna (Dark Premium) e um poder de customização robusto. Funciona para automatizar farm em jogos (Genshin Impact, Minecraft, Roblox) e para realizar tarefas repetitivas de escritório (preencher formulários, lidar com planilhas, manter a tela ativa).

---

## 🎮 Para que serve?

### 1. Automação para Jogos (Gaming)
- **Modo Spam (Repetição):** Precisa atirar rápido ou pular freneticamente? O modo Spam clica milhares de vezes por segundo na posição que você escolher.
- **Modo Hold (Segurar):** Para jogos onde você precisa segurar uma tecla por minutos (como correr ou minerar).
- **Construtor de Macros:** Você pode criar um perfil complexo de *Stamina Loop* para jogos como Genshin Impact (ex: `Segura W` -> `Dá 7 Dashs` -> `Espera 6s` -> `Repete`).

### 2. Produtividade & Trabalho
- **Clique Dinâmico:** Automatize a navegação em sistemas lentos, clicando nas coordenadas X e Y exatas nos momentos corretos.
- **Anti-AFK (Away From Keyboard):** Precisa ir pegar um café e não quer que o Microsoft Teams ou o jogo desconecte? Crie um macro para mexer o mouse e apertar `Scroll` de vez em quando.
- **Modo Humano (Jitter):** Se o software que você usa tem detecção de bots, ative o "Modo Humano", que insere micro-atrasos aleatórios (em milissegundos) entre cada ação, imitando o comportamento humano real.

---

## ✨ Principais Funcionalidades

- **Design Premium & Responsivo:** Layout focado em "Cards" com indicadores LED (bolinha pulsante) de status e micro-interações de *hover*.
- **Construtor de Macros Modular 🧙‍♂️:** Uma interface gráfica para você arrastar e soltar blocos lógicos (`Segurar Tecla`, `Pausa`, `Clique Mouse`, `Arrastar Mouse`).
- **Sistema de Captura Interativa 🎯:** Não sabe qual a coordenada do mouse? Clique no botão de capturar (📍), você terá 3 segundos para colocar o cursor onde quer, e o sistema copia a posição automaticamente!
- **Painel Flutuante (Mini-Bar) ⠿:** Minimiza o aplicativo em uma barra super discreta no topo da tela, permitindo que você troque de presets enquanto trabalha ou joga.
- **Perfis (Presets) Salvos:** Crie abas separadas por categorias (Genshin, Roblox, Trabalho) e salve os macros em um arquivo `.json` exportável para mandar para amigos.

---

## 📥 Como Baixar e Usar (Versão Pronta)

Você não precisa instalar Python para usar o aplicativo! Basta baixar o executável pronto:

1. Acesse a aba [**Releases**](https://github.com/henrique-jfp/AutoClick/releases) aqui no Github.
2. Baixe o arquivo `AutoClicker.exe` da versão mais recente.
3. Dê dois cliques e pronto! (Se o Windows SmartScreen bloquear, clique em "Mais Informações" -> "Executar assim mesmo").

> **Nota:** Para alguns jogos executados em Tela Cheia ou com anti-cheat pesado, recomenda-se iniciar o `AutoClicker.exe` como Administrador.

---

## 🛠️ Como Rodar pelo Código-Fonte (Desenvolvedores)

Se você é desenvolvedor e quer mexer no código, os requisitos são simples:

1. Instale o Python (3.10 ou superior).
2. Clone o repositório:
   ```bash
   git clone https://github.com/henrique-jfp/AutoClick.git
   cd AutoClick
   ```
3. Instale as dependências:
   ```bash
   pip install pynput pillow
   ```
4. Execute a aplicação:
   ```bash
   python autoclicker.py
   ```

### Compilando seu próprio `.exe`
Para compilar uma versão standalone, execute o script de build incluso:
```bash
pip install pyinstaller
python build_exe.py
```
O executável final estará na pasta `dist/`.

---

## 🤝 Contribuindo
Sinta-se à vontade para abrir **Issues** relatando bugs ou enviar **Pull Requests** com novas ideias de funcionalidades!

**Feito com foco em UI/UX e automação de alta performance.** ⚡
