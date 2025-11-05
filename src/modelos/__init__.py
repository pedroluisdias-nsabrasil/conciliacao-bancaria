"""
Pacote de Modelos de Dados - Sistema de Conciliação Bancária.

Este pacote contém os modelos de dados principais do sistema:
- Lancamento: Representa um lançamento do extrato bancário
- Comprovante: Representa um comprovante de pagamento
- Match: Representa a conciliação entre lançamento e comprovante

Author: Pedro Luis
Date: 02/11/2025
"""

from .lancamento import Lancamento, LancamentoError, LancamentoInvalidoError
from .comprovante import (
    Comprovante,
    ComprovanteError,
    ComprovanteInvalidoError,
    OCRError,
)
from .match import Match, MatchError, MatchInvalidoError, MatchConflitanteError

__version__ = "1.0.0"

__all__ = [
    # Modelos principais
    "Lancamento",
    "Comprovante",
    "Match",
    # Exceções de Lancamento
    "LancamentoError",
    "LancamentoInvalidoError",
    # Exceções de Comprovante
    "ComprovanteError",
    "ComprovanteInvalidoError",
    "OCRError",
    # Exceções de Match
    "MatchError",
    "MatchInvalidoError",
    "MatchConflitanteError",
]
