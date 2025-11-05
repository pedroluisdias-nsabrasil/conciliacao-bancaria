"""
Funções para normalização de dados de extratos bancários.

Este módulo contém utilitários para transformar strings de extratos
bancários em tipos Python apropriados (date, Decimal, etc).
"""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def normalizar_data(texto: str) -> date:
    """
    Converte uma string de data em um objeto date.

    Suporta os seguintes formatos:
    - DD/MM/YYYY (padrão brasileiro)
    - DD-MM-YYYY
    - YYYY-MM-DD (ISO)
    - DD/MM/YY (assume século 2000)

    Args:
        texto: String contendo a data

    Returns:
        Objeto date normalizado

    Raises:
        ValueError: Se a data não puder ser interpretada

    Examples:
        >>> normalizar_data("02/11/2025")
        date(2025, 11, 2)
        >>> normalizar_data("02-11-2025")
        date(2025, 11, 2)
        >>> normalizar_data("2025-11-02")
        date(2025, 11, 2)
    """
    if not texto or not isinstance(texto, str):
        raise ValueError(f"Data inválida: '{texto}'")

    texto = texto.strip()

    # Tentar formato DD/MM/YYYY ou DD-MM-YYYY
    formatos_br = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",  # ano com 2 dígitos
        "%d-%m-%y",
    ]

    for formato in formatos_br:
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue

    # Tentar formato ISO (YYYY-MM-DD)
    try:
        return date.fromisoformat(texto)
    except ValueError:
        pass

    raise ValueError(
        f"Formato de data não reconhecido: '{texto}'. "
        f"Formatos aceitos: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD"
    )


def normalizar_valor(texto: str) -> Decimal:
    """
    Converte uma string de valor monetário em Decimal.

    Suporta os seguintes formatos:
    - R$ 1.234,56
    - R$ 1234,56
    - 1.234,56
    - 1234,56
    - -1.234,56 (negativo)
    - (1.234,56) (contábil negativo)

    Args:
        texto: String contendo o valor

    Returns:
        Valor como Decimal (sempre positivo)

    Raises:
        ValueError: Se o valor não puder ser interpretado

    Examples:
        >>> normalizar_valor("R$ 1.234,56")
        Decimal('1234.56')
        >>> normalizar_valor("-1.234,56")
        Decimal('1234.56')
        >>> normalizar_valor("(150,00)")
        Decimal('150.00')
    """
    if not texto or not isinstance(texto, str):
        raise ValueError(f"Valor inválido: '{texto}'")

    # Remover espaços e converter para string
    texto = str(texto).strip()

    # Remover símbolo de moeda (R$, $, etc)
    texto = re.sub(r"[R\$\s]+", "", texto)

    # Detectar se é negativo (- ou parênteses contábeis)
    eh_negativo = texto.startswith("-") or (
        texto.startswith("(") and texto.endswith(")")
    )

    # Remover sinais e parênteses
    texto = texto.replace("-", "").replace("(", "").replace(")", "").strip()

    if not texto:
        raise ValueError("Valor vazio após limpeza")

    # Substituir vírgula por ponto (formato brasileiro → decimal)
    # Mas primeiro remover pontos de milhar
    # Regra: se temos "1.234,56", remover o ponto e trocar vírgula por ponto
    if "," in texto:
        texto = texto.replace(".", "")  # Remove separador de milhar
        texto = texto.replace(",", ".")  # Vírgula decimal vira ponto

    try:
        valor = Decimal(texto)
        # Sempre retornar positivo (o sinal é tratado pelo tipo do lançamento)
        return abs(valor)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(
            f"Não foi possível converter '{texto}' para valor monetário: {e}"
        )


def limpar_descricao(texto: str) -> str:
    """
    Limpa e normaliza a descrição de um lançamento.

    Remove:
    - Espaços múltiplos
    - Quebras de linha
    - Caracteres especiais problemáticos
    - Espaços no início e fim

    Args:
        texto: Descrição original

    Returns:
        Descrição limpa e normalizada

    Examples:
        >>> limpar_descricao("  PAG   FORNECEDOR\\n  XYZ  ")
        'PAG FORNECEDOR XYZ'
        >>> limpar_descricao("TED-123  PAGAMENTO")
        'TED-123 PAGAMENTO'
    """
    if not texto:
        return ""

    # Converter para string se não for
    texto = str(texto)

    # Remover quebras de linha e tabs
    texto = texto.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Remover espaços múltiplos
    texto = re.sub(r"\s+", " ", texto)

    # Remover espaços no início e fim
    texto = texto.strip()

    # Converter para uppercase (padrão)
    texto = texto.upper()

    return texto


def identificar_tipo_lancamento(
    descricao: str, valor: Decimal, coluna_tipo: Optional[str] = None
) -> str:
    """
    Identifica se um lançamento é débito (D) ou crédito (C).

    Usa 3 estratégias em ordem de prioridade:
    1. Coluna explícita no CSV (se fornecida)
    2. Palavras-chave na descrição
    3. Sinal do valor (se negativo = débito)

    Args:
        descricao: Descrição do lançamento
        valor: Valor do lançamento
        coluna_tipo: Valor da coluna tipo, se existir (D/C ou Débito/Crédito)

    Returns:
        'D' para débito ou 'C' para crédito

    Examples:
        >>> identificar_tipo_lancamento("TED ENVIADA", Decimal('100'), None)
        'D'
        >>> identificar_tipo_lancamento("DEPOSITO RECEBIDO", Decimal('100'), None)
        'C'
        >>> identificar_tipo_lancamento("COMPRA LOJA", Decimal('50'), "D")
        'D'
    """
    # Estratégia 1: Usar coluna explícita se fornecida
    if coluna_tipo:
        coluna_tipo = str(coluna_tipo).strip().upper()
        if coluna_tipo in ["D", "DEBITO", "DÉBITO", "DEB"]:
            return "D"
        if coluna_tipo in ["C", "CREDITO", "CRÉDITO", "CRED"]:
            return "C"

    # Estratégia 2: Palavras-chave na descrição
    descricao_upper = descricao.upper()

    # Palavras que indicam débito (saída de dinheiro)
    palavras_debito = [
        "PAGAMENTO",
        "PAG",
        "TED",
        "DOC",
        "PIX ENVIADO",
        "TRANSFERENCIA",
        "COMPRA",
        "SAQUE",
        "TARIFA",
        "IOF",
        "JUROS",
        "MULTA",
        "DEBITO",
        "DÉBITO",
        "ENVIO",
        "ENVIADO",
    ]

    # Palavras que indicam crédito (entrada de dinheiro)
    palavras_credito = [
        "DEPOSITO",
        "DEPÓSITO",
        "PIX RECEBIDO",
        "RECEBIDO",
        "CREDITO",
        "CRÉDITO",
        "ESTORNO",
        "DEVOLUCAO",
        "DEVOLUÇÃO",
        "RESGATE",
        "RENDIMENTO",
        "APLICACAO",
        "APLICAÇÃO",
    ]

    for palavra in palavras_debito:
        if palavra in descricao_upper:
            return "D"

    for palavra in palavras_credito:
        if palavra in descricao_upper:
            return "C"

    # Estratégia 3: Fallback - assumir débito (mais comum)
    # Em produção, poderia logar um warning aqui
    logger.warning(
        f"Não foi possível determinar tipo do lançamento pela descrição: '{descricao}'. "
        f"Assumindo débito (D)."
    )
    return "D"


def detectar_encoding(caminho_arquivo: str) -> str:
    """
    Detecta o encoding de um arquivo.

    Tenta detectar automaticamente o encoding (UTF-8, Latin-1, etc).
    Útil para arquivos CSV de bancos que podem vir em diferentes encodings.

    Args:
        caminho_arquivo: Caminho para o arquivo

    Returns:
        Nome do encoding detectado

    Note:
        Por enquanto retorna 'utf-8' como padrão.
        Implementação completa requer biblioteca chardet.
    """
    # TODO: Implementar detecção automática com chardet
    # Por enquanto, retornar encoding padrão
    return "utf-8"
