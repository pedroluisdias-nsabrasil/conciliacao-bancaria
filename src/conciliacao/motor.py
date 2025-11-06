"""
Motor de Conciliação Bancária.

Este módulo implementa o MotorConciliacao, responsável por orquestrar
o processo de conciliação entre lançamentos bancários e comprovantes,
gerenciando múltiplas estratégias de matching.

Classes:
    MotorConciliacao: Orquestrador principal de conciliação
    
Exceções:
    MotorConciliacaoError: Erro base do motor
    EstrategiaInvalidaError: Estratégia inválida
    ConciliacaoError: Erro durante conciliação

Exemplo:
    >>> from src.conciliacao import MotorConciliacao
    >>> from src.conciliacao.estrategias import EstrategiaExato
    >>> 
    >>> motor = MotorConciliacao()
    >>> motor.adicionar_estrategia(EstrategiaExato())
    >>> matches = motor.conciliar(lancamentos, comprovantes)
    >>> stats = motor.gerar_estatisticas(matches, lancamentos)

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Created: 04/11/2025
Version: 1.0.0
"""

import logging
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
from decimal import Decimal
from src.modelos import Lancamento, Comprovante, Match
from src.conciliacao.estrategias.base import EstrategiaBase
from src.conciliacao.estrategias.regras import EstrategiaRegras
from src.conciliacao.estrategias.exato import EstrategiaExato


# Configuração de logging
logger = logging.getLogger(__name__)


# ============================================================================
# EXCEÇÕES CUSTOMIZADAS
# ============================================================================


class MotorConciliacaoError(Exception):
    """Erro base do motor de conciliação."""

    pass


class EstrategiaInvalidaError(MotorConciliacaoError):
    """Erro quando estratégia é inválida."""

    pass


class ConciliacaoError(MotorConciliacaoError):
    """Erro durante processo de conciliação."""

    pass


# ============================================================================
# MOTOR DE CONCILIAÇÃO
# ============================================================================


class MotorConciliacao:
    """
    Motor de conciliação bancária.

    Responsável por orquestrar o processo de conciliação entre lançamentos
    bancários e comprovantes de pagamento, gerenciando múltiplas estratégias
    de matching e garantindo que cada comprovante seja usado apenas uma vez.

    O motor aplica as estratégias em ordem de prioridade (menor valor primeiro)
    e para no primeiro match encontrado para cada lançamento.

    Attributes:
        estrategias: Lista de estratégias de matching
        config: Configurações do motor

    Example:
        >>> motor = MotorConciliacao()
        >>> motor.adicionar_estrategia(EstrategiaExato())
        >>> matches = motor.conciliar(lancamentos, comprovantes)
        >>> print(f"Taxa: {motor.calcular_taxa_conciliacao(matches, lancamentos):.1%}")
    """

    def __init__(self):
        """
        Inicializa motor de conciliação com estratégias padrão.

        Estratégias são aplicadas em ordem de prioridade (maior primeiro):
        - EstrategiaRegras (prioridade 20): Auto-conciliação de tarifas
        - EstrategiaExato (prioridade 10): Matching exato com comprovantes
        """
        # Inicializar estratégias em ordem de prioridade
        self.estrategias = [
            EstrategiaRegras(),  # Prioridade 20 (executa primeiro)
            EstrategiaExato(),  # Prioridade 10 (executa depois)
        ]

        # Ordenar por prioridade decrescente
        self.estrategias.sort(key=lambda e: e.prioridade, reverse=True)

        # Configuração padrão
        self.config = {
            "tolerancia_dias": 3,
            "tolerancia_valor": 0.50,
            "confianca_minima": 0.60,
            "confianca_auto_aprovar": 0.90,  # ✅ ADICIONAR ESTA LINHA!
        }
        # Variáveis de estatísticas
        self._tempo_total = Decimal('0')
        self._total_conciliacoes = 0

        # Log de inicialização
        logger.info(
            f"Motor inicializado com {len(self.estrategias)} estratégias: "
            f"{[e.nome for e in self.estrategias]}"
        )

    def conciliar(
        self,
        lancamentos: List[Lancamento],
        comprovantes: List[Comprovante],
    ) -> List[Match]:
        """
        Concilia lançamentos com comprovantes.

        Este é o método principal do motor. Para cada lançamento:
        1. Itera pelas estratégias em ordem de prioridade
        2. Busca um match usando a estratégia
        3. Se encontrar, adiciona à lista e marca comprovante como usado
        4. Para no primeiro match (não tenta outras estratégias)

        Comprovantes já usados não são considerados nas próximas iterações,
        garantindo que cada comprovante seja usado apenas uma vez.

        Args:
            lancamentos: Lista de lançamentos bancários
            comprovantes: Lista de comprovantes de pagamento

        Returns:
            Lista de matches encontrados (pode estar vazia)

        Raises:
            ConciliacaoError: Se erro durante conciliação
            ValueError: Se listas vazias ou None

        Example:
            >>> matches = motor.conciliar(lancamentos, comprovantes)
            >>> print(f"Encontrados {len(matches)} matches")
            >>> auto_aprovados = [m for m in matches if m.pode_auto_aprovar()]
        """
        # Validações
        if not lancamentos:
            raise ValueError("Lista de lançamentos não pode ser vazia")

        # TEMPORÁRIO: Permitir comprovantes vazios para MVP (EstrategiaRegras funciona sem eles)
        # if not comprovantes:
        #     raise ValueError("Lista de comprovantes não pode ser vazia")
        if not comprovantes:
            logger.warning("Lista de comprovantes vazia - apenas estratégias baseadas em regras funcionarão")

        if not self.estrategias:
            raise ConciliacaoError(
                "Nenhuma estratégia cadastrada. "
                "Use adicionar_estrategia() antes de conciliar."
            )

        logger.info(
            f"Iniciando conciliação: "
            f"{len(lancamentos)} lançamentos × "
            f"{len(comprovantes)} comprovantes"
        )
        logger.debug(f"Estratégias ativas: " f"{[e.nome for e in self.estrategias]}")

        # Registro de tempo
        inicio = datetime.now()

        # Estruturas de controle
        matches: List[Match] = []
        usados: Set[int] = set()  # IDs de comprovantes já usados

        # Estatísticas por estratégia
        stats_estrategias: Dict[str, int] = {e.nome: 0 for e in self.estrategias}

        try:
            # Para cada lançamento
            for idx_lanc, lancamento in enumerate(lancamentos, 1):
                logger.debug(
                    f"Processando lançamento {idx_lanc}/{len(lancamentos)}: "
                    f"{lancamento.descricao} - R$ {lancamento.valor}"
                )

                # Tentar cada estratégia em ordem de prioridade
                match_encontrado = False

                for estrategia in self.estrategias:
                    logger.debug(
                        f"  Aplicando estratégia: {estrategia.nome} "
                        f"(prioridade {estrategia.prioridade})"
                    )

                    try:
                        # Buscar match com esta estratégia
                        match = estrategia.encontrar_match(
                            lancamento, comprovantes, usados
                        )

                        # Se encontrou match
                        if match:
                            # Verificar confiança mínima
                            if match.confianca >= self.config["confianca_minima"]:
                                matches.append(match)
                                usados.add(id(match.comprovante))
                                stats_estrategias[estrategia.nome] += 1
                                match_encontrado = True

                                logger.info(
                                    f"  ✓ Match encontrado! "
                                    f"Estratégia: {estrategia.nome}, "
                                    f"Confiança: {match.confianca:.1%}, "
                                    f"Comprovante: {match.comprovante.arquivo if match.comprovante else 'AUTO (Regra)'}"
                                )
                                break  # Para no primeiro match
                            else:
                                logger.debug(
                                    f"  ⚠ Match com confiança baixa "
                                    f"({match.confianca:.1%} < "
                                    f"{self.config['confianca_minima']:.1%}), "
                                    f"ignorando"
                                )

                    except Exception as e:
                        logger.error(f"  ✗ Erro na estratégia {estrategia.nome}: {e}")
                        # Continua com próxima estratégia
                        continue

                if not match_encontrado:
                    logger.debug(f"  ✗ Nenhum match encontrado para este lançamento")

            # Calcular tempo total
            fim = datetime.now()
            tempo_decorrido = (fim - inicio).total_seconds()
            self._tempo_total += Decimal(str(tempo_decorrido))
            self._total_conciliacoes += 1

            # Log de resumo
            logger.info(
                f"Conciliação concluída: "
                f"{len(matches)} matches em {tempo_decorrido:.2f}s"
            )
            logger.info(
                f"Taxa de conciliação: "
                f"{len(matches)}/{len(lancamentos)} "
                f"({len(matches)/len(lancamentos):.1%})"
            )

            # Log de estatísticas por estratégia
            for nome, count in stats_estrategias.items():
                if count > 0:
                    logger.info(
                        f"  {nome}: {count} matches "
                        f"({count/len(matches):.1%} do total)"
                    )

            return matches

        except Exception as e:
            logger.error(f"Erro durante conciliação: {e}", exc_info=True)
            raise ConciliacaoError(f"Falha na conciliação: {e}")

    def conciliar_com_filtros(
        self,
        lancamentos: List[Lancamento],
        comprovantes: List[Comprovante],
        filtro_lancamento: Optional[callable] = None,
        filtro_comprovante: Optional[callable] = None,
    ) -> List[Match]:
        """
        Concilia aplicando filtros personalizados.

        Args:
            lancamentos: Lista de lançamentos bancários
            comprovantes: Lista de comprovantes
            filtro_lancamento: Função que retorna True para incluir lançamento
            filtro_comprovante: Função que retorna True para incluir comprovante

        Returns:
            Lista de matches encontrados

        Example:
            >>> # Apenas lançamentos > R$ 1000
            >>> filtro = lambda l: l.valor > Decimal('1000')
            >>> matches = motor.conciliar_com_filtros(
            ...     lancamentos, comprovantes,
            ...     filtro_lancamento=filtro
            ... )
        """
        # Aplicar filtros
        lanc_filtrados = lancamentos
        comp_filtrados = comprovantes

        if filtro_lancamento:
            lanc_filtrados = [l for l in lancamentos if filtro_lancamento(l)]
            logger.info(
                f"Filtro de lançamentos: " f"{len(lanc_filtrados)}/{len(lancamentos)}"
            )

        if filtro_comprovante:
            comp_filtrados = [c for c in comprovantes if filtro_comprovante(c)]
            logger.info(
                f"Filtro de comprovantes: " f"{len(comp_filtrados)}/{len(comprovantes)}"
            )

        # Conciliar normalmente
        return self.conciliar(lanc_filtrados, comp_filtrados)

    def gerar_estatisticas(
        self,
        matches: List[Match],
        lancamentos: List[Lancamento],
    ) -> Dict[str, any]:
        """
        Gera estatísticas detalhadas da conciliação.

        Args:
            matches: Lista de matches encontrados
            lancamentos: Lista de lançamentos originais

        Returns:
            Dicionário com estatísticas:
            - total_lancamentos: Total de lançamentos processados
            - total_matches: Total de matches encontrados
            - taxa_conciliacao: Percentual de conciliação (0.0 a 1.0)
            - confianca_media: Confiança média dos matches
            - confianca_min: Confiança mínima
            - confianca_max: Confiança máxima
            - auto_aprovados: Quantidade de matches auto-aprovados
            - requer_revisao: Quantidade que requer revisão manual
            - valor_total_conciliado: Valor total dos matches (Decimal)
            - por_metodo: Estatísticas por método de conciliação
            - por_confianca: Distribuição por faixa de confiança

        Example:
            >>> stats = motor.gerar_estatisticas(matches, lancamentos)
            >>> print(f"Taxa: {stats['taxa_conciliacao']:.1%}")
            >>> print(f"Auto-aprovados: {stats['auto_aprovados']}")
        """
        if not matches:
            return {
                "total_lancamentos": len(lancamentos),
                "total_matches": 0,
                "taxa_conciliacao": 0.0,
                "confianca_media": 0.0,
                "confianca_min": 0.0,
                "confianca_max": 0.0,
                "auto_aprovados": 0,
                "requer_revisao": 0,
                "valor_total_conciliado": Decimal("0"),
                "por_metodo": {},
                "por_confianca": {
                    "alta": 0,  # >= 0.90
                    "media": 0,  # >= 0.70
                    "baixa": 0,  # >= 0.60
                },
            }

        # Estatísticas básicas
        total_lancamentos = len(lancamentos)
        total_matches = len(matches)
        taxa_conciliacao = total_matches / total_lancamentos

        # Confiança
        confiancas = [m.confianca for m in matches]
        confianca_media = sum(confiancas) / len(confiancas)
        confianca_min = min(confiancas)
        confianca_max = max(confiancas)

        # Auto-aprovação
        threshold_auto = self.config["confianca_auto_aprovar"]
        auto_aprovados = sum(1 for m in matches if m.confianca >= threshold_auto)
        requer_revisao = total_matches - auto_aprovados

        # Valor total
        valor_total = sum(m.lancamento.valor for m in matches)

        # Por método
        por_metodo: Dict[str, int] = {}
        for match in matches:
            metodo = match.metodo
            por_metodo[metodo] = por_metodo.get(metodo, 0) + 1

        # Por faixa de confiança
        por_confianca = {
            "alta": sum(1 for m in matches if m.confianca >= 0.90),
            "media": sum(1 for m in matches if 0.70 <= m.confianca < 0.90),
            "baixa": sum(1 for m in matches if 0.60 <= m.confianca < 0.70),
        }

        return {
            "total_lancamentos": total_lancamentos,
            "total_matches": total_matches,
            "taxa_conciliacao": taxa_conciliacao,
            "confianca_media": confianca_media,
            "confianca_min": confianca_min,
            "confianca_max": confianca_max,
            "auto_aprovados": auto_aprovados,
            "requer_revisao": requer_revisao,
            "valor_total_conciliado": valor_total,
            "por_metodo": por_metodo,
            "por_confianca": por_confianca,
        }

    def gerar_relatorio(
        self,
        matches: List[Match],
        lancamentos: List[Lancamento],
        formato: str = "texto",
    ) -> str:
        """
        Gera relatório formatado da conciliação.

        Args:
            matches: Lista de matches encontrados
            lancamentos: Lista de lançamentos originais
            formato: Formato do relatório ("texto" ou "markdown")

        Returns:
            String com relatório formatado

        Example:
            >>> relatorio = motor.gerar_relatorio(matches, lancamentos)
            >>> print(relatorio)
        """
        stats = self.gerar_estatisticas(matches, lancamentos)

        if formato == "markdown":
            return self._gerar_relatorio_markdown(stats)
        else:
            return self._gerar_relatorio_texto(stats)

    def _gerar_relatorio_texto(self, stats: Dict) -> str:
        """Gera relatório em formato texto."""
        linhas = [
            "=" * 60,
            "RELATÓRIO DE CONCILIAÇÃO BANCÁRIA",
            "=" * 60,
            "",
            "RESUMO GERAL:",
            f"  Total de lançamentos:     {stats['total_lancamentos']}",
            f"  Matches encontrados:      {stats['total_matches']}",
            f"  Taxa de conciliação:      {stats['taxa_conciliacao']:.1%}",
            "",
            "CONFIANÇA:",
            f"  Média:                    {stats['confianca_media']:.1%}",
            f"  Mínima:                   {stats['confianca_min']:.1%}",
            f"  Máxima:                   {stats['confianca_max']:.1%}",
            "",
            "STATUS:",
            f"  Auto-aprovados:           {stats['auto_aprovados']}",
            f"  Requerem revisão:         {stats['requer_revisao']}",
            "",
            "VALOR TOTAL CONCILIADO:",
            f"  R$ {stats['valor_total_conciliado']:,.2f}",
            "",
        ]

        if stats["por_metodo"]:
            linhas.extend(
                [
                    "POR MÉTODO:",
                    *[f"  {k}: {v}" for k, v in stats["por_metodo"].items()],
                    "",
                ]
            )

        linhas.extend(
            [
                "POR FAIXA DE CONFIANÇA:",
                f"  Alta (≥90%):              {stats['por_confianca']['alta']}",
                f"  Média (70-90%):           {stats['por_confianca']['media']}",
                f"  Baixa (60-70%):           {stats['por_confianca']['baixa']}",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(linhas)

    def _gerar_relatorio_markdown(self, stats: Dict) -> str:
        """Gera relatório em formato markdown."""
        linhas = [
            "# Relatório de Conciliação Bancária",
            "",
            "## Resumo Geral",
            "",
            f"- **Total de lançamentos:** {stats['total_lancamentos']}",
            f"- **Matches encontrados:** {stats['total_matches']}",
            f"- **Taxa de conciliação:** {stats['taxa_conciliacao']:.1%}",
            "",
            "## Confiança",
            "",
            f"- **Média:** {stats['confianca_media']:.1%}",
            f"- **Mínima:** {stats['confianca_min']:.1%}",
            f"- **Máxima:** {stats['confianca_max']:.1%}",
            "",
            "## Status",
            "",
            f"- **Auto-aprovados:** {stats['auto_aprovados']}",
            f"- **Requerem revisão:** {stats['requer_revisao']}",
            "",
            "## Valor Total Conciliado",
            "",
            f"**R$ {stats['valor_total_conciliado']:,.2f}**",
            "",
        ]

        if stats["por_metodo"]:
            linhas.extend(
                [
                    "## Por Método",
                    "",
                    *[f"- **{k}:** {v}" for k, v in stats["por_metodo"].items()],
                    "",
                ]
            )

        linhas.extend(
            [
                "## Por Faixa de Confiança",
                "",
                f"- **Alta (≥90%):** {stats['por_confianca']['alta']}",
                f"- **Média (70-90%):** {stats['por_confianca']['media']}",
                f"- **Baixa (60-70%):** {stats['por_confianca']['baixa']}",
            ]
        )

        return "\n".join(linhas)

    def calcular_taxa_conciliacao(
        self, matches: List[Match], lancamentos: List[Lancamento]
    ) -> float:
        """
        Calcula taxa de conciliação.

        Args:
            matches: Lista de matches encontrados
            lancamentos: Lista de lançamentos originais

        Returns:
            Taxa de conciliação (0.0 a 1.0)

        Example:
            >>> taxa = motor.calcular_taxa_conciliacao(matches, lancamentos)
            >>> print(f"Taxa: {taxa:.1%}")
        """
        if not lancamentos:
            return 0.0
        return len(matches) / len(lancamentos)

    def obter_performance(self) -> Dict[str, any]:
        """
        Obtém métricas de performance do motor.

        Returns:
            Dicionário com métricas de performance

        Example:
            >>> perf = motor.obter_performance()
            >>> print(f"Tempo médio: {perf['tempo_medio']:.2f}s")
        """
        if self._total_conciliacoes == 0:
            return {
                "total_conciliacoes": 0,
                "tempo_total": Decimal("0"),
                "tempo_medio": Decimal("0"),
            }

        tempo_medio = self._tempo_total / self._total_conciliacoes

        return {
            "total_conciliacoes": self._total_conciliacoes,
            "tempo_total": float(self._tempo_total),
            "tempo_medio": float(tempo_medio),
        }

    def __repr__(self) -> str:
        """Representação string do motor."""
        return (
            f"MotorConciliacao("
            f"estrategias={len(self.estrategias)}, "
            f"conciliacoes={self._total_conciliacoes})"
        )


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================


def criar_motor_padrao() -> MotorConciliacao:
    """
    Cria motor com configuração padrão.

    Returns:
        MotorConciliacao configurado com estratégia exato

    Example:
        >>> motor = criar_motor_padrao()
        >>> matches = motor.conciliar(lancamentos, comprovantes)
    """
    from src.conciliacao.estrategias import EstrategiaExato

    motor = MotorConciliacao()
    motor.adicionar_estrategia(EstrategiaExato())

    logger.info("Motor padrão criado com EstrategiaExato")
    return motor


def info() -> None:
    """
    Exibe informações sobre o motor de conciliação.

    Example:
        >>> from src.conciliacao.motor import info
        >>> info()
    """
    print("=" * 60)
    print("MOTOR DE CONCILIAÇÃO BANCÁRIA")
    print("=" * 60)
    print(f"Versão: 1.0.0")
    print(f"Autor: Pedro Luis")
    print(f"Estratégias disponíveis:")
    print("  - EstrategiaExato (prioridade: 10)")
    print("  - [Outras virão nas próximas sprints]")
    print("=" * 60)
