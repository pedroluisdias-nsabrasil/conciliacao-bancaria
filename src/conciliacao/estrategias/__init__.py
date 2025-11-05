"""
Pacote de Estratégias de Matching

Este pacote contém todas as estratégias de conciliação disponíveis no sistema.
Cada estratégia implementa um algoritmo diferente para encontrar matches entre
lançamentos bancários e comprovantes de pagamento.

Estratégias Disponíveis:
    - EstrategiaBase: Interface abstrata (não usar diretamente)
    - EstrategiaExato: Matching por valor e data exatos (a implementar)
    - EstrategiaFuzzy: Matching com similaridade de texto (futuro)
    - EstrategiaAgregado: Matching de múltiplos lançamentos (futuro)

Autor: Pedro Luis (pedroluisdias@br-nsa.com)
Data: 03/11/2025
Sprint: 3 - Motor de Conciliação
"""

from .base import (
    EstrategiaBase,
    criar_match_com_confianca,
    validar_confianca,
    EstrategiaError,
    MatchInvalidoError,
    ConfiancaInvalidaError,
)

from .exato import EstrategiaExato

# Versão do pacote de estratégias
__version__ = "1.0.0"

# Exportar classes principais
__all__ = [
    # Classe base
    "EstrategiaBase",
    "EstrategiaExato",
    # Funções auxiliares
    "criar_match_com_confianca",
    "validar_confianca",
    # Exceções
    "EstrategiaError",
    "MatchInvalidoError",
    "ConfiancaInvalidaError",
]


def listar_estrategias():
    """
    Lista todas as estratégias disponíveis.

    Returns:
        dict: Dicionário com nome e classe de cada estratégia

    Examples:
        >>> estrategias = listar_estrategias()
        >>> for nome, classe in estrategias.items():
        ...     print(f"{nome}: {classe}")
    """
    estrategias = {
        "base": EstrategiaBase,
        "exato": EstrategiaExato,
        # "fuzzy": EstrategiaFuzzy,  # Futuro
        # "agregado": EstrategiaAgregado,  # Futuro
    }
    return estrategias


# Informações do pacote
print(f"Pacote estrategias v{__version__} carregado")
print(f"Estratégias disponíveis: {len(listar_estrategias())}")
