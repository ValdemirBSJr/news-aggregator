import os
import sys
import subprocess
import venv

VENV_DIRETORIO = "venv"
NOME_ENTRY_POINT = "news-aggregator"  # O nome do comando definido no setup.py


def obter_caminhos_venv():
    """Retorna os caminhos para o executável python e scripts dentro do venv."""
    if os.name == "nt":
        scripts_dir = os.path.join(VENV_DIRETORIO, "Scripts")
        python_exe = os.path.join(scripts_dir, "python.exe")
    else:
        scripts_dir = os.path.join(VENV_DIRETORIO, "bin")
        python_exe = os.path.join(scripts_dir, "python")

    return python_exe, scripts_dir


def criar_venv():
    """Cria o ambiente virtual."""
    print()
    print("🐍🐍🐍 Olá! Estamos configurando tudo para você... 🐍🐍🐍")
    print("Não se preocupe, isto só acontecerá na primeira vez.")
    print()
    print(f"✅ Criando ambiente virtual em '{VENV_DIRETORIO}'...")

    venv.create(VENV_DIRETORIO, with_pip=True)


def instalador_pacotes_via_setup():
    """Instala o pacote e suas dependências usando pyproject.toml."""
    print("📦 Instalando o pacote e suas dependências via pyproject.toml...")
    python_exe, _ = obter_caminhos_venv()

    # Este comando lê o pyproject.toml, instala as dependências
    # listadas em 'install_requires' e cria o 'entry_point'.
    # Usar '-e' (editável) é ótimo para desenvolvimento.
    comando = [python_exe, "-m", "pip", "install", "--quiet", "-e", "."]

    print(f"Executando: {' '.join(comando)}")
    subprocess.check_call(comando)
    print("✅ Pacote instalado com sucesso!")


def rodar_script_via_entrypoint():
    """Roda o script principal usando o comando de console."""
    print(f"🚀 Rodando o script principal (via entry point '{NOME_ENTRY_POINT}')...")
    print("-" * 30)

    python_exe, scripts_dir = obter_caminhos_venv()

    # O entry point estará no diretório de scripts do venv
    if os.name == "nt":
        # No Windows, pode ser .exe, .cmd ou um script sem extensão
        comando_app = os.path.join(scripts_dir, f"{NOME_ENTRY_POINT}.exe")
        if not os.path.exists(comando_app):
            comando_app = os.path.join(scripts_dir, f"{NOME_ENTRY_POINT}.cmd")
        if not os.path.exists(comando_app):
            comando_app = os.path.join(scripts_dir, NOME_ENTRY_POINT)
    else:
        # No Linux/macOS
        comando_app = os.path.join(scripts_dir, NOME_ENTRY_POINT)

    # Verificação final
    if not os.path.exists(comando_app):
        print(f"❌ Erro: Não foi possível encontrar o comando '{comando_app}'")
        print(f"Certifique-se de que '{NOME_ENTRY_POINT}' está definido em 'entry_points' no setup.py.")
        sys.exit(1)

    # Executa o comando
    subprocess.check_call([comando_app])
    print("-" * 30)
    print("🎉 Execução concluída!")


def checa_configura_env():
    """Verifica se o venv existe e o configura se necessário."""
    if not os.path.exists(VENV_DIRETORIO):
        try:
            criar_venv()
            instalador_pacotes_via_setup()
        except Exception as e:
            print(f"❌ Erro ao configurar ambiente: {e}")
            print("Tente remover a pasta 'venv' e rodar novamente.")
            sys.exit(1)
    else:
        print("✅ Ambiente virtual já existe.")
        # Você pode adicionar uma lógica aqui para reinstalar
        # ou atualizar dependências se desejar.
        # Por enquanto, vamos assumir que está tudo OK.


if __name__ == "__main__":
    checa_configura_env()
    rodar_script_via_entrypoint()
