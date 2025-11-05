"""
Módulo de regras YAML para auto-conciliação.

Este módulo implementa um sistema de regras configurável via YAML
para auto-conciliar lançamentos bancários comuns (tarifas, IOF, juros)
sem necessidade de comprovante físico.
"""

from src.regras.parser import ParserRegras
from src.regras.engine import EngineRegras

__all__ = ["ParserRegras", "EngineRegras"]
