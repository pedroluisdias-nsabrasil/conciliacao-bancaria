"""
Estratégia Base para Conciliação Bancária

Este módulo define a interface abstrata que todas as estratégias de matching
devem implementar. Usa o padrão Strategy para permitir diferentes algoritmos
de conciliação de forma intercambiável.

Autor: Pedro Luis (pedroluisdias@br-nsa.com)
Data: 03/11/2025
Sprint: 3 - Motor de Conciliação
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Set
from decimal import Decimal
import logging

# Imports dos modelos (assumindo estrutura do projeto)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modelos import Lancamento, Comprovante, Match

logger = logging.getLogger(__name__)


class EstrategiaBase(ABC):
    """
    Classe abstrata base para estratégias de matching.

    Esta classe define a interface que todas as estratégias de conciliação
    devem implementar. Cada estratégia representa um algoritmo diferente
    para encontrar matches entre lançamentos bancários e comprovantes.

    Exemplos de estratégias:
        - EstrategiaExato: Match por valor e data exatos
        - EstrategiaFuzzy: Match com similaridade de texto
        - EstrategiaAgregado: Match de múltiplos lançamentos
        - EstrategiaML: Match usando Machine Learning

    Attributes:
        nome: Nome descritivo da estratégia
        prioridade: Ordem de execução (menor = executa primeiro)

    Examples:
        >>> class MinhaEstrategia(EstrategiaBase):
        ...     def encontrar_match(self, lancamento, comprovantes, usados):
        ...         # Implementação específica
        ...         pass
    """

    def __init__(self, nome: str, prioridade: int = 100):
        """
        Inicializa a estratégia base.

        Args:
            nome: Nome descritivo da estratégia (ex: "Matching Exato")
            prioridade: Ordem de execução. Menor valor = maior prioridade.
                       Por convenção:
                       - 10: Estratégias de alta confiança (exato)
                       - 50: Estratégias de média confiança (fuzzy)
                       - 100: Estratégias de baixa confiança (heurísticas)
        """
        self.nome = nome
        self.prioridade = prioridade
        logger.debug(
            f"Estratégia '{self.nome}' inicializada (prioridade: {self.prioridade})"
        )

    @abstractmethod
    def encontrar_match(
        self, lancamento: Lancamento, comprovantes: List[Comprovante], usados: Set[int]
    ) -> Optional[Match]:
        """
        Encontra o melhor match para um lançamento.

        Este é o método principal que cada estratégia deve implementar.
        Deve procurar entre os comprovantes disponíveis e retornar o melhor
        match possível, ou None se não encontrar nenhum candidato adequado.

        Args:
            lancamento: Lançamento bancário a ser conciliado
            comprovantes: Lista de comprovantes disponíveis
            usados: Set com IDs dos comprovantes já usados em outros matches
                   (para evitar matches duplicados)

        Returns:
            Match object com o melhor candidato e confiança calculada,
            ou None se não encontrar match adequado.

        Raises:
            NotImplementedError: Se a estratégia não implementar este método

        Examples:
            >>> estrategia = EstrategiaExato()
            >>> match = estrategia.encontrar_match(lancamento, comprovantes, set())
            >>> if match and match.confianca >= 0.90:
            ...     print("Match de alta confiança encontrado!")

        Notes:
            - Estratégias devem respeitar o set 'usados' para evitar duplicatas
            - Retornar None é válido e esperado quando não há match adequado
            - A confiança deve estar entre 0.0 e 1.0
            - Estratégias não devem modificar os objetos recebidos
        """
        pass

    def calcular_confianca(
        self, lancamento: Lancamento, comprovante: Comprovante, **kwargs
    ) -> float:
        """
        Calcula a confiança de um match entre lançamento e comprovante.

        Este método pode ser sobrescrito por estratégias específicas para
        implementar lógicas customizadas de cálculo de confiança. A implementação
        base retorna 0.5 (confiança neutra).

        Args:
            lancamento: Lançamento bancário
            comprovante: Comprovante de pagamento
            **kwargs: Argumentos adicionais específicos da estratégia

        Returns:
            float: Confiança entre 0.0 (sem confiança) e 1.0 (certeza absoluta)

        Examples:
            >>> confianca = estrategia.calcular_confianca(lancamento, comprovante)
            >>> assert 0.0 <= confianca <= 1.0

        Notes:
            - 0.0 a 0.59: Baixa confiança (não conciliar)
            - 0.60 a 0.89: Média confiança (revisar)
            - 0.90 a 1.0: Alta confiança (auto-aprovar)
        """
        return 0.5

    def validar_match(self, lancamento: Lancamento, comprovante: Comprovante) -> bool:
        """
        Valida se um match é minimamente viável.

        Verifica condições básicas que todo match deve satisfazer,
        independente da estratégia. Por exemplo, valores negativos
        não devem matchear com valores positivos.

        Args:
            lancamento: Lançamento bancário
            comprovante: Comprovante de pagamento

        Returns:
            bool: True se o match é viável, False caso contrário

        Examples:
            >>> if not estrategia.validar_match(lancamento, comprovante):
            ...     return None  # Match inviável

        Notes:
            - Esta é uma validação básica, não substitui o cálculo de confiança
            - Estratégias podem adicionar validações específicas
        """
        # Valores devem ter o mesmo sinal (ambos positivos ou ambos negativos)
        if (lancamento.valor > 0) != (comprovante.valor > 0):
            logger.debug(
                f"Match inviável: sinais diferentes "
                f"(lançamento: {lancamento.valor}, comprovante: {comprovante.valor})"
            )
            return False

        # Valores devem ser diferentes de zero
        if lancamento.valor == 0 or comprovante.valor == 0:
            logger.debug("Match inviável: valor zero detectado")
            return False

        return True

    def __str__(self) -> str:
        """Representação em string da estratégia."""
        return f"{self.nome} (prioridade: {self.prioridade})"

    def __repr__(self) -> str:
        """Representação técnica da estratégia."""
        return f"<{self.__class__.__name__}(nome='{self.nome}', prioridade={self.prioridade})>"

    def __lt__(self, other: "EstrategiaBase") -> bool:
        """
        Comparação para ordenação por prioridade.

        Permite ordenar estratégias automaticamente usando sort().
        Menor prioridade = executa primeiro.
        """
        return self.prioridade < other.prioridade


# Funções auxiliares para uso geral


def criar_match_com_confianca(
    lancamento: Lancamento,
    comprovante: Comprovante,
    confianca: float,
    metodo: str = "Manual",  # ← ADICIONAR
    observacoes: str = "",
) -> Match:
    """
    Função helper para criar um objeto Match com confiança.

    Args:
        lancamento: Lançamento bancário
        comprovante: Comprovante de pagamento
        confianca: Confiança do match (0.0 a 1.0)
        observacoes: Notas adicionais sobre o match

    Returns:
        Match: Objeto Match configurado

    Raises:
        ValueError: Se confiança fora do intervalo [0.0, 1.0]

    Examples:
        >>> match = criar_match_com_confianca(lanc, comp, 0.95, "Match exato")
    """
    if not 0.0 <= confianca <= 1.0:
        raise ValueError(f"Confiança deve estar entre 0.0 e 1.0, recebido: {confianca}")

    match = Match(
        lancamento=lancamento,
        comprovante=comprovante,
        confianca=confianca,
        metodo=metodo,  # ← ADICIONAR
    )

    if observacoes:
        # Assumindo que Match tem campo observacoes (ajustar se necessário)
        match.observacoes = observacoes

    return match


def validar_confianca(confianca: float) -> bool:
    """
    Valida se um valor de confiança é válido.

    Args:
        confianca: Valor de confiança a validar

    Returns:
        bool: True se válido, False caso contrário

    Examples:
        >>> validar_confianca(0.95)
        True
        >>> validar_confianca(1.5)
        False
    """
    return isinstance(confianca, (int, float)) and 0.0 <= confianca <= 1.0


# Exceções customizadas


class EstrategiaError(Exception):
    """Erro base para estratégias de matching."""

    pass


class MatchInvalidoError(EstrategiaError):
    """Erro quando um match inválido é criado."""

    pass


class ConfiancaInvalidaError(EstrategiaError):
    """Erro quando a confiança está fora do intervalo válido."""

    pass


if __name__ == "__main__":
    # Exemplo de uso (para testes rápidos)
    print("=" * 60)
    print("EstrategiaBase - Interface Abstrata")
    print("=" * 60)
    print()
    print("Esta é uma classe abstrata que define o contrato para")
    print("todas as estratégias de matching do sistema.")
    print()
    print("Para usar, crie uma subclasse e implemente o método")
    print("'encontrar_match()'.")
    print()
    print("Exemplo:")
    print("  class MinhaEstrategia(EstrategiaBase):")
    print("      def encontrar_match(self, lancamento, comprovantes, usados):")
    print("          # Sua lógica aqui")
    print("          pass")
    print()
    print("=" * 60)
