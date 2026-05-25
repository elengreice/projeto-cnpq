import logging
import os
from datetime import datetime

# Cria a pasta logs se nao existir
os.makedirs("logs", exist_ok=True)

# Configura o logger
logging.basicConfig(
    filename="logs/operacoes.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def log_info(operacao, detalhes=""):
    mensagem = f"{operacao}"
    if detalhes:
        mensagem += f" | {detalhes}"
    logging.info(mensagem)
    print(f"[LOG] {mensagem}")

def log_erro(operacao, erro=""):
    mensagem = f"{operacao}"
    if erro:
        mensagem += f" | ERRO: {erro}"
    logging.error(mensagem)
    print(f"[ERRO] {mensagem}")

def log_aviso(operacao, detalhe=""):
    mensagem = f"{operacao}"
    if detalhe:
        mensagem += f" | {detalhe}"
    logging.warning(mensagem)
    print(f"[AVISO] {mensagem}")