"""
Módulo de ingestão de dados.

Este módulo é responsável por ler arquivos de entrada (extratos bancários,
comprovantes) e convertê-los em objetos do domínio.
"""

from .leitor_csv import LeitorCSV
from .leitor_pdf import LeitorPDF
from .normalizadores import (
    normalizar_data,
    normalizar_valor,
    limpar_descricao,
    identificar_tipo_lancamento,
)

__all__ = [
    "LeitorCSV",
    "LeitorPDF",
    "normalizar_data",
    "normalizar_valor", 
    "limpar_descricao",
    "identificar_tipo_lancamento",
]
