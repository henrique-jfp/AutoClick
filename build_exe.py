import subprocess
import sys
import os

def build():
    print("[*] Iniciando a compilacao do Auto Clicker Pro em arquivo .exe...")
    
    # Ensure icon is generated
    if not os.path.exists("app_icon.ico"):
        print("[*] Gerando icon do aplicativo...")
        try:
            import generate_icon
            generate_icon.create_icon()
        except Exception as e:
            print(f"[!] Aviso ao gerar icon: {e}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=AutoClicker",
        "--icon=app_icon.ico" if os.path.exists("app_icon.ico") else "",
        "autoclicker.py"
    ]
    
    # Filter empty strings
    cmd = [c for c in cmd if c]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n[+] COMPILACAO CONCLUIDA COM SUCESSO!")
        print("O seu executavel 'AutoClicker.exe' foi criado na pasta 'dist':")
        print(f"Caminho: {os.path.abspath('dist/AutoClicker.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Erro durante a compilacao: {e}")

if __name__ == "__main__":
    build()
