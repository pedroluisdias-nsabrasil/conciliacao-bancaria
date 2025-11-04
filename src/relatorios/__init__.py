"""
Módulo de geração de relatórios para o Sistema de Conciliação Bancária.

Este módulo fornece classes para gerar relatórios profissionais em diferentes formatos:
- Excel (.xlsx): Relatórios com múltiplas abas, formatação condicional e gráficos
- PDF: Relatórios com layout profissional, gráficos matplotlib e tabelas formatadas

Exemplo de uso:
    >>> from src.relatorios import GeradorExcel, GeradorPDF
    >>> 
    >>> # Gerar relatório Excel
    >>> gerador_excel = GeradorExcel()
    >>> gerador_excel.gerar(matches, lancamentos_nao_conc, stats, "relatorio.xlsx")
    >>> 
    >>> # Gerar relatório PDF
    >>> gerador_pdf = GeradorPDF()
    >>> gerador_pdf.gerar(matches, lancamentos_nao_conc, stats, "relatorio.pdf")

Autores:
    Pedro Luis (pedroluisdias@br-nsa.com)

Versão:
    1.0.0 - Sprint 5 (Novembro 2025)
"""

from .gerador_excel import GeradorExcel

__all__ = ["GeradorExcel"]

__version__ = "1.0.0"
__author__ = "Pedro Luis"
