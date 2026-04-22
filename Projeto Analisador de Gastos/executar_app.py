import subprocess
import os

# Caminhos que você já validou
caminho_streamlit = r"C:\Users\dilma\AppData\Local\python\mu\mu_venv-38-20260417-121010\Scripts\streamlit.exe"
caminho_app = r"C:\Users\dilma\mu_code\Projeto Analisador de Gastos\app.py"

print("Iniciando o Analisador de Gastos... Aguarde o navegador abrir.")

# Esse comando abre o Streamlit sem você precisar ir no CMD
subprocess.run([caminho_streamlit, "run", caminho_app])# Escreva o seu código aqui :-)
