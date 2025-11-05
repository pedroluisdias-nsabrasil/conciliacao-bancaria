"""
src/relatorios/__init__.py

Módulo de geração de relatórios.
"""

from .gerador_excel import GeradorExcel
from .gerador_pdf import GeradorPDF

__all__ = ["GeradorExcel", "GeradorPDF"]
