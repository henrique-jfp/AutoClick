<div align="center">
  <img src="app_icon.png" alt="Auto Clicker Pro Logo" width="128"/>
  <h1>Auto Clicker Pro & Key Presser ⚡</h1>
  <p><strong>A automação de mouses e teclados mais avançada, bonita e segura do mercado. Totalmente gratuita.</strong></p>
  
  [![Release](https://img.shields.io/github/v/release/henrique-jfp/AutoClick?color=3ECF8E&style=for-the-badge)](https://github.com/henrique-jfp/AutoClick/releases)
  [![Python](https://img.shields.io/badge/Python-3.12-5B8CFF?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
</div>

<br/>

Esqueça os "Auto Clickers" antigos, com visual de Windows 95, menus confusos e vírus. O **Auto Clicker Pro** foi refeito do zero para te oferecer uma experiência premium, interface moderna (Dark Mode nativo) e ferramentas de automação profissionais que realmente funcionam nos jogos modernos!

---

## 🚀 O que o Auto Clicker Pro pode fazer por você?

### 🎮 Para Jogos (Roblox, Minecraft, Genshin Impact e MMOs)
- **Modo Spam (Metralhadora):** Ideal para *Simulators* no Roblox ou jogos idle. Faça 1.000 cliques por segundo no botão esquerdo, direito ou na barra de espaço. Seu dedo agradece.
- **Modo Segurar (AFK Farming):** Vai sair para jantar mas precisa que o seu boneco continue minerando no Minecraft ou andando num servidor? O Modo Segurar prende a tecla para você.
- **Posição de Clique Teleportada:** O recurso mais cobiçado em jogos. Você diz a coordenada X e Y de um botão (ex: "Aceitar Missão"). Não importa onde o seu mouse esteja na tela, ao ligar o clicker, ele se teletransporta para o local exato e clica por você.
- **Sistema Anti-Ban (Jitter Humano):** A maioria dos AutoClickers são detectados por Anti-Cheats (como o Vanguard ou XignCode) porque clicam como "robôs" em velocidades cravadas de 50ms. O nosso sistema injeta **micro-atrasos aleatórios** (Modo Humano), enganando os detectores e protegendo a sua conta.

### 💼 Para Trabalho e Produtividade (Macros)
- **Criador de Presets e Sequências:** Quer automatizar o preenchimento de uma planilha ou sistema do seu trabalho? Crie uma Macro Visual arrastando comandos: `Clica` ➜ `Espera 1 seg` ➜ `Aperta Enter` ➜ `Repete infinitamente`.
- **Modo Flutuante (Mini Bar):** Não quer aquele janelão no meio da tela enquanto joga ou trabalha? Um único clique encolhe o aplicativo para uma barra minimalista e flutuante no topo do monitor.
- **Anti-AFK (Teams / Discord):** Crie uma macro rápida para mexer o mouse a cada 5 minutos. Nunca mais apareça como "Ausente" na sua empresa.

---

## ✨ Novidades da Versão 2.0 (Premium UI)

1. **Design Inteligente & Adaptativo:** A interface inteira foi desenhada em uma "Dark UI" com feedback visual responsivo. Além disso, ela se adapta perfeitamente ao seu monitor sem criar barras de rolagem.
2. **Sistema de Captura Interativa 🎯:** Não sabe a coordenada X/Y de um botão na tela? Basta clicar no ícone de "Alvo" no programa, mover o mouse para onde você quer, esperar 3 segundos, e o programa lê as coordenadas da sua tela automaticamente.
3. **Abas Organizacionais (Presets):** Salve dezenas de macros e organize por categorias! Uma aba para "Minecraft", outra para "Trabalho", outra para "Genshin". Exporte e mande seu arquivo `.json` para os seus amigos importarem o mesmo farm!
4. **Sistema de Doação Nativo 💛:** Modal de doação super elegante gerado 100% via código, com QR Code de PIX flutuante na tela!

---

## 📥 Como Baixar e Usar (Versão Pronta)

Você não precisa ser programador nem instalar nada complicado no PC. O programa já vem compilado em um único arquivo de inicialização direta:

1. Acesse a aba [**Releases**](https://github.com/henrique-jfp/AutoClick/releases) aqui no Github.
2. Baixe o arquivo `AutoClicker.exe` da versão mais recente.
3. **Pronto!** Dê dois cliques no `.exe` e ele abre direto. (Caso o Windows SmartScreen alerte por ser um programa novo, clique em "Mais Informações" ➜ "Executar assim mesmo").

> **Nota para Jogos em Tela Cheia:** A maioria dos jogos mais novos bloqueia cliques simulados se o jogo não estiver rodando como Administrador. Para funcionar 100% no seu jogo, certifique-se de iniciar o `AutoClicker.exe` **como Administrador**.

---

## 💻 Quer editar o código-fonte? (Para Desenvolvedores)

Se você é programador e quer contribuir ou criar a sua própria versão customizada, o projeto é construído em **Python puro + Tkinter + Pynput**.

1. Instale o Python (3.10 ou superior).
2. Clone o repositório no seu PC:
   ```bash
   git clone https://github.com/henrique-jfp/AutoClick.git
   cd AutoClick
   ```
3. Instale as dependências:
   ```bash
   pip install pynput pillow qrcode
   ```
4. Execute e teste:
   ```bash
   python autoclicker.py
   ```

### 🔨 Compilando o seu próprio `.exe`
Fizemos um script que empacota o app (e imagens embutidas como o QR Code) num arquivo só, usando o PyInstaller:
```bash
pip install pyinstaller
python build_exe.py
```
O seu novo `.exe` mágico e independente aparecerá dentro da pasta `dist/`!

---

## 🤝 Gostou?
Esqueça mensalidades e adwares. Este software é livre e construído pela comunidade!
Sinta-se à vontade para dar uma **Estrela (Star ⭐)** no topo deste repositório, relatar bugs nas *Issues*, e enviar novas melhorias de funcionalidade.
⚡
