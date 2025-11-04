"""
Pacote de Conciliação Bancária

Este pacote contém o motor de conciliação e todas as estratégias de matching
para correlacionar lançamentos bancários com comprovantes de pagamento.

Componentes Principais:
    - MotorConciliacao: Orquestrador principal (a implementar)
    - Estratégias: Algoritmos de matching em src.conciliacao.estrategias

Arquitetura:
    1. MotorConciliacao recebe lançamentos e comprovantes
    2. Aplica estratégias em ordem de prioridade
    3. Retorna lista de Matches com confiança
    4. Evita matches duplicados

Uso Típico:
    >>> from src.conciliacao import MotorConciliacao
    >>> from src.conciliacao.estrategias import EstrategiaExato
    >>> 
    >>> motor = MotorConciliacao()
    >>> motor.adicionar_estrategia(EstrategiaExato())
    >>> matches = motor.conciliar(lancamentos, comprovantes)

Autor: Pedro Luis (pedroluisdias@br-nsa.com)
Data: 03/11/2025
Sprint: 3 - Motor de Conciliação
"""

# Importar subpacote de estratégias
from . import estrategias

# Importar classes principais do subpacote estrategias
from .estrategias import (
    EstrategiaBase,
    criar_match_com_confianca,
    validar_confianca,
    EstrategiaError,
    MatchInvalidoError,
    ConfiancaInvalidaError,
)

# Quando o MotorConciliacao for criado, descomentar:
# from .motor import MotorConciliacao, ConfiguracaoConciliacao

# Versão do pacote de conciliação
__version__ = "1.0.0"

# Exportar para uso externo
__all__ = [
    # Subpacotes
    "estrategias",
    
    # Classes base
    "EstrategiaBase",
    
    # Motor (a implementar)
    # "MotorConciliacao",
    # "ConfiguracaoConciliacao",
    
    # Funções auxiliares
    "criar_match_com_confianca",
    "validar_confianca",
    
    # Exceções
    "EstrategiaError",
    "MatchInvalidoError",
    "ConfiancaInvalidaError",
]


# Metadados do pacote
PACKAGE_INFO = {
    "nome": "Conciliação Bancária",
    "versao": __version__,
    "sprint": 3,
    "status": "Em desenvolvimento",
    "autor": "Pedro Luis",
    "email": "pedroluisdias@br-nsa.com",
}


def info():
    """
    Exibe informações sobre o pacote de conciliação.
    
    Examples:
        >>> from src.conciliacao import info
        >>> info()
    """
    print("=" * 60)
    print(f"📦 {PACKAGE_INFO['nome']} v{PACKAGE_INFO['versao']}")
    print("=" * 60)
    print(f"Sprint: {PACKAGE_INFO['sprint']}")
    print(f"Status: {PACKAGE_INFO['status']}")
    print(f"Autor: {PACKAGE_INFO['autor']} ({PACKAGE_INFO['email']})")
    print()
    print("Componentes:")
    print("  ✅ EstrategiaBase (interface abstrata)")
    print("  ⏳ EstrategiaExato (a implementar)")
    print("  ⏳ MotorConciliacao (a implementar)")
    print("=" * 60)


# Configurações padrão do sistema de conciliação
CONFIG_PADRAO = {
    "tolerancia_dias": 3,  # ±3 dias para matching de datas
    "tolerancia_valor": 0.50,  # R$ 0.50 de tolerância para valores
    "confianca_minima": 0.60,  # Confiança mínima para sugerir match
    "confianca_auto_aprovar": 0.90,  # Confiança para auto-aprovar
    "max_matches_por_lancamento": 5,  # Máximo de sugestões por lançamento
    "usar_cache": True,  # Usar cache de matches
    "log_level": "INFO",  # Nível de log
}


def obter_config_padrao():
    """
    Retorna configuração padrão do sistema.
    
    Returns:
        dict: Configurações padrão
        
    Examples:
        >>> config = obter_config_padrao()
        >>> print(config['tolerancia_dias'])
        3
    """
    return CONFIG_PADRAO.copy()


# Log de inicialização
import logging
logger = logging.getLogger(__name__)
logger.info(f"Pacote conciliacao v{__version__} carregado")
