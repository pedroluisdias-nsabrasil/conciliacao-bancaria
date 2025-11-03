"""
Módulo de ingestão de dados.

Leitores para diferentes formatos de arquivos:
- LeitorCSV: Extratos bancários em CSV
- LeitorPDF: Extratos bancários em PDF
- LeitorOCR: Comprovantes em PDF/imagem (com OCR)
- Preprocessador: Melhoria de qualidade de imagens

Author: Pedro Luis (pedroluisdias@br-nsa.com)
"""

from .leitor_csv import LeitorCSV
from .leitor_pdf import LeitorPDF
from .leitor_ocr import LeitorOCR
from .preprocessador import Preprocessador, preprocessar_para_ocr
from .normalizadores import (
    normalizar_data,
    normalizar_valor,
    limpar_descricao,
    identificar_tipo_lancamento,
    detectar_encoding
)

__all__ = [
    'LeitorCSV',
    'LeitorPDF',
    'LeitorOCR',
    'Preprocessador',
    'preprocessar_para_ocr',
    'normalizar_data',
    'normalizar_valor',
    'limpar_descricao',
    'identificar_tipo_lancamento',
    'detectar_encoding',
]
