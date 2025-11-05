"""
Engine de Regras.

Processa regras YAML e aplica condições aos lançamentos bancários.
"""

import re
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date
import logging

from src.modelos.lancamento import Lancamento
from src.modelos.match import Match

logger = logging.getLogger(__name__)


class EngineRegras:
    """
    Engine para processar regras de auto-conciliação.

    Aplica regras em cascata (por prioridade) e retorna Match
    quando todas as condições de uma regra são satisfeitas.
    """

    def __init__(self, regras: List[Dict[str, Any]]):
        """
        Inicializa engine com lista de regras.

        Args:
            regras: Lista de regras validadas (do ParserRegras)

        Examples:
            >>> regras = [{'id': 'teste', 'prioridade': 10, ...}]
            >>> engine = EngineRegras(regras)
        """
        self.regras = regras
        self._ordenar_por_prioridade()
        logger.info(f"Engine inicializada com {len(self.regras)} regras")

    def _ordenar_por_prioridade(self) -> None:
        """Ordena regras por prioridade (maior primeiro)."""
        self.regras.sort(key=lambda r: r.get("prioridade", 0), reverse=True)

    def processar(self, lancamento: Lancamento) -> Optional[Match]:
        """
        Processa lançamento contra todas as regras.

        Testa regras em ordem de prioridade. Para na primeira
        regra que satisfazer todas as condições.

        Args:
            lancamento: Lançamento a processar

        Returns:
            Match se alguma regra foi aplicada, None caso contrário

        Examples:
            >>> lancamento = Lancamento(...)
            >>> match = engine.processar(lancamento)
            >>> if match:
            ...     print(f"Match encontrado: {match.observacoes}")
        """
        for regra in self.regras:
            if self._avaliar_regra(lancamento, regra):
                logger.info(
                    f"Regra '{regra['id']}' aplicada ao lançamento "
                    f"{lancamento.descricao}"
                )
                return self._criar_match(lancamento, regra)

        return None

    def _avaliar_regra(self, lancamento: Lancamento, regra: Dict[str, Any]) -> bool:
        """
        Avalia se todas as condições de uma regra são satisfeitas.

        Args:
            lancamento: Lançamento a avaliar
            regra: Regra com condições

        Returns:
            True se TODAS as condições são satisfeitas (AND lógico)
        """
        condicoes = regra.get("condicoes", [])

        for condicao in condicoes:
            if not self._avaliar_condicao(lancamento, condicao):
                return False

        # Todas condições satisfeitas
        return True

    def _avaliar_condicao(
        self, lancamento: Lancamento, condicao: Dict[str, Any]
    ) -> bool:
        """
        Avalia uma única condição.

        Args:
            lancamento: Lançamento a avaliar
            condicao: Dicionário com campo, operador e valor

        Returns:
            True se condição é satisfeita
        """
        campo = condicao["campo"]
        operador = condicao["operador"]
        valor_esperado = condicao["valor"]

        # Obter valor do campo do lançamento
        valor_lancamento = self._obter_valor_campo(lancamento, campo)

        if valor_lancamento is None:
            return False

        # Aplicar operador
        return self._aplicar_operador(valor_lancamento, operador, valor_esperado)

    def _obter_valor_campo(self, lancamento: Lancamento, campo: str) -> Any:
        """
        Obtém valor de um campo do lançamento.

        Args:
            lancamento: Lançamento
            campo: Nome do campo (ex: 'descricao', 'valor', 'tipo')

        Returns:
            Valor do campo ou None se campo não existe
        """
        # Mapeamento de campos
        mapeamento = {
            "descricao": lancamento.descricao,
            "valor": lancamento.valor,
            "data": lancamento.data,
            "tipo": lancamento.tipo,
        }

        return mapeamento.get(campo)

    def _aplicar_operador(
        self, valor_lancamento: Any, operador: str, valor_esperado: Any
    ) -> bool:
        """
        Aplica operador de comparação.

        Args:
            valor_lancamento: Valor extraído do lançamento
            operador: Tipo de operador
            valor_esperado: Valor esperado da regra

        Returns:
            True se operador retorna verdadeiro
        """
        # Mapear operadores para métodos
        operadores = {
            "equals": self._op_equals,
            "not_equals": self._op_not_equals,
            "contains": self._op_contains,
            "not_contains": self._op_not_contains,
            "regex": self._op_regex,
            "greater_than": self._op_greater_than,
            "less_than": self._op_less_than,
            "between": self._op_between,
            "in": self._op_in,
            "not_in": self._op_not_in,
        }

        metodo = operadores.get(operador)

        if metodo is None:
            logger.warning(f"Operador desconhecido: {operador}")
            return False

        try:
            return metodo(valor_lancamento, valor_esperado)
        except Exception as e:
            logger.error(f"Erro ao aplicar operador '{operador}': {e}")
            return False

    # ========================================
    # OPERADORES DE COMPARAÇÃO
    # ========================================

    def _op_equals(self, valor: Any, esperado: Any) -> bool:
        """Igualdade exata."""
        return valor == esperado

    def _op_not_equals(self, valor: Any, esperado: Any) -> bool:
        """Diferente."""
        return valor != esperado

    def _op_contains(self, valor: Any, esperado: Any) -> bool:
        """
        Contém substring (case-insensitive).

        Se esperado é lista, verifica se valor contém qualquer item.
        """
        if not isinstance(valor, str):
            valor = str(valor)

        valor = valor.upper()

        # Se esperado é lista, verificar qualquer item
        if isinstance(esperado, list):
            return any(str(item).upper() in valor for item in esperado)

        # Esperado é string única
        return str(esperado).upper() in valor

    def _op_not_contains(self, valor: Any, esperado: Any) -> bool:
        """Não contém substring."""
        return not self._op_contains(valor, esperado)

    def _op_regex(self, valor: Any, esperado: str) -> bool:
        """
        Match com expressão regular.

        Usa flags re.IGNORECASE por padrão.
        """
        if not isinstance(valor, str):
            valor = str(valor)

        try:
            return bool(re.search(esperado, valor, re.IGNORECASE))
        except re.error as e:
            logger.error(f"Regex inválido '{esperado}': {e}")
            return False

    def _op_greater_than(self, valor: Any, esperado: Any) -> bool:
        """Maior que (>)."""
        # Converter para Decimal se for valor monetário
        if isinstance(valor, Decimal):
            esperado = Decimal(str(esperado))
        elif isinstance(valor, (int, float)):
            if isinstance(esperado, str):
                esperado = float(esperado)

        return valor > esperado

    def _op_less_than(self, valor: Any, esperado: Any) -> bool:
        """Menor que (<)."""
        # Converter para Decimal se for valor monetário
        if isinstance(valor, Decimal):
            esperado = Decimal(str(esperado))
        elif isinstance(valor, (int, float)):
            if isinstance(esperado, str):
                esperado = float(esperado)

        return valor < esperado

    def _op_between(self, valor: Any, esperado: List) -> bool:
        """
        Entre dois valores (inclusivo).

        esperado deve ser [min, max]
        """
        if not isinstance(esperado, list) or len(esperado) != 2:
            logger.error(f"Operador 'between' requer lista [min, max]: {esperado}")
            return False

        min_val, max_val = esperado

        # Converter para Decimal se for valor monetário
        if isinstance(valor, Decimal):
            min_val = Decimal(str(min_val))
            max_val = Decimal(str(max_val))
        elif isinstance(valor, (int, float)):
            if isinstance(min_val, str):
                min_val = float(min_val)
            if isinstance(max_val, str):
                max_val = float(max_val)

        return min_val <= valor <= max_val

    def _op_in(self, valor: Any, esperado: List) -> bool:
        """Valor está na lista."""
        if not isinstance(esperado, list):
            logger.error(f"Operador 'in' requer lista: {esperado}")
            return False

        return valor in esperado

    def _op_not_in(self, valor: Any, esperado: List) -> bool:
        """Valor não está na lista."""
        return not self._op_in(valor, esperado)

    # ========================================
    # CRIAÇÃO DE MATCH
    # ========================================

    def _criar_match(self, lancamento: Lancamento, regra: Dict[str, Any]) -> Match:
        """
        Cria Match a partir da regra aplicada.

        Args:
            lancamento: Lançamento que satisfez a regra
            regra: Regra aplicada

        Returns:
            Match configurado conforme ação da regra
        """
        acao = regra["acao"]

        # Montar observações
        observacao_base = acao.get(
            "observacao", f"Auto-conciliado por regra: {regra['nome']}"
        )

        observacao_completa = f"{observacao_base}\n" f"Regra: {regra['id']}"

        # Categoria (se definida)
        if "categoria" in acao:
            observacao_completa += f"\nCategoria: {acao['categoria']}"

        # Criar Match
        return Match(
            lancamento=lancamento,
            comprovante=None,  # Regras não usam comprovante
            confianca=acao.get("confianca", 0.85),
            metodo="regra",
            observacoes=observacao_completa,
        )

    def estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas das regras carregadas.

        Returns:
            Dicionário com estatísticas
        """
        return {
            "total_regras": len(self.regras),
            "por_prioridade": {
                regra["id"]: regra.get("prioridade", 0) for regra in self.regras
            },
            "tipos_acao": {regra["id"]: regra["acao"]["tipo"] for regra in self.regras},
        }
