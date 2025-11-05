"""
Estratégia de conciliação baseada em regras YAML.

Auto-concilia lançamentos sem comprovante usando regras de negócio
configuradas em arquivos YAML.
"""

from pathlib import Path
from typing import Optional, List
import logging

from src.conciliacao.estrategias.base import EstrategiaBase
from src.modelos.lancamento import Lancamento
from src.modelos.comprovante import Comprovante
from src.modelos.match import Match
from src.regras.parser import ParserRegras
from src.regras.engine import EngineRegras

logger = logging.getLogger(__name__)


class EstrategiaRegras(EstrategiaBase):
    """
    Estratégia baseada em regras YAML.

    Permite auto-conciliação de lançamentos comuns (tarifas bancárias,
    IOF, juros, rendimentos) sem necessidade de comprovante físico.

    As regras são definidas em arquivo YAML e processadas pela Engine.
    Esta estratégia deve ser executada ANTES das outras, pois é mais
    específica e tem maior confiança.

    Attributes:
        arquivo_regras: Caminho para arquivo YAML com regras
        engine: Engine de regras configurada
        nome: Nome da estratégia
        prioridade: Prioridade de execução (20 = alta, antes do exato)

    Examples:
        >>> estrategia = EstrategiaRegras()
        >>> match = estrategia.encontrar_match(lancamento, [], set())
        >>> if match:
        ...     print(f"Auto-conciliado: {match.observacoes}")
    """

    def __init__(
        self,
        arquivo_regras: Optional[Path] = None,
        nome: str = "Regras YAML",
        prioridade: int = 20,
    ):
        """
        Inicializa estratégia de regras.

        Args:
            arquivo_regras: Caminho para YAML de regras.
                          Se None, usa default: config/regras/tarifas.yaml
            nome: Nome descritivo da estratégia
            prioridade: Prioridade de execução (maior = primeira)

        Examples:
            >>> # Usar arquivo padrão
            >>> estrategia = EstrategiaRegras()

            >>> # Usar arquivo customizado
            >>> estrategia = EstrategiaRegras(
            ...     arquivo_regras=Path('minhas_regras.yaml')
            ... )
        """
        super().__init__(nome=nome, prioridade=prioridade)

        if arquivo_regras is None:
            arquivo_regras = Path("config/regras/tarifas.yaml")

        self.arquivo_regras = Path(arquivo_regras)
        self.engine: Optional[EngineRegras] = None
        self._carregar_regras()

    def _carregar_regras(self) -> None:
        """
        Carrega regras do arquivo YAML.

        Usa ParserRegras para ler e validar o YAML, depois
        inicializa EngineRegras com as regras carregadas.

        Em caso de erro, cria engine vazia (sem regras).
        """
        try:
            parser = ParserRegras(self.arquivo_regras)
            regras = parser.carregar()
            self.engine = EngineRegras(regras)

            logger.info(
                f"Estratégia '{self.nome}' inicializada: "
                f"{len(regras)} regras carregadas de {self.arquivo_regras}"
            )

        except FileNotFoundError:
            logger.warning(
                f"Arquivo de regras não encontrado: {self.arquivo_regras}. "
                f"Estratégia '{self.nome}' desabilitada."
            )
            self.engine = EngineRegras([])

        except Exception as e:
            logger.error(
                f"Erro ao carregar regras de {self.arquivo_regras}: {e}. "
                f"Estratégia '{self.nome}' desabilitada."
            )
            self.engine = EngineRegras([])

    def encontrar_match(
        self,
        lancamento: Lancamento,
        comprovantes: List[Comprovante],
        comprovantes_usados: set,
    ) -> Optional[Match]:
        """
        Busca match baseado em regras YAML.

        Esta estratégia NÃO usa comprovantes - ela auto-concilia
        lançamentos baseando-se apenas nas características do
        próprio lançamento (descrição, valor, tipo, etc).

        Args:
            lancamento: Lançamento a conciliar
            comprovantes: Lista de comprovantes disponíveis (não usado)
            comprovantes_usados: Set de comprovantes já usados (não usado)

        Returns:
            Match se alguma regra se aplicar, None caso contrário.
            O Match terá comprovante=None pois é auto-conciliação.

        Examples:
            >>> lancamento = Lancamento(
            ...     data=date(2025, 11, 5),
            ...     valor=Decimal('15.00'),
            ...     descricao='TARIFA DOC TRANSF',
            ...     tipo='D'
            ... )
            >>> match = estrategia.encontrar_match(lancamento, [], set())
            >>> if match:
            ...     print(match.metodo)  # 'regra'
            ...     print(match.confianca)  # 0.95 (alta confiança)
        """
        # Se engine não carregou, não há como processar
        if self.engine is None or len(self.engine.regras) == 0:
            return None

        # Processar lançamento contra regras
        match = self.engine.processar(lancamento)

        if match:
            logger.debug(
                f"Estratégia '{self.nome}' encontrou match para "
                f"lançamento: {lancamento.descricao} "
                f"(Confiança: {match.confianca:.0%})"
            )

        return match

    def recarregar_regras(self) -> int:
        """
        Recarrega regras do arquivo YAML.

        Útil para aplicar mudanças nas regras sem reiniciar
        a aplicação.

        Returns:
            Número de regras carregadas

        Examples:
            >>> estrategia = EstrategiaRegras()
            >>> # Editar config/regras/tarifas.yaml
            >>> num_regras = estrategia.recarregar_regras()
            >>> print(f"{num_regras} regras recarregadas")
        """
        self._carregar_regras()

        if self.engine:
            num_regras = len(self.engine.regras)
            logger.info(f"Regras recarregadas: {num_regras} regras ativas")
            return num_regras

        return 0

    def obter_estatisticas(self) -> dict:
        """
        Obtém estatísticas das regras carregadas.

        Returns:
            Dicionário com estatísticas:
            - total_regras: Número total de regras
            - arquivo: Caminho do arquivo de regras
            - por_prioridade: Regras agrupadas por prioridade
            - tipos_acao: Regras agrupadas por tipo de ação

        Examples:
            >>> stats = estrategia.obter_estatisticas()
            >>> print(f"Total de regras: {stats['total_regras']}")
            >>> print(f"Arquivo: {stats['arquivo']}")
        """
        if not self.engine or len(self.engine.regras) == 0:
            return {
                "total_regras": 0,
                "arquivo": str(self.arquivo_regras),
                "status": "não carregada",
                "estrategia": self.nome,
                "prioridade": self.prioridade,
            }

        stats = self.engine.estatisticas()
        stats["arquivo"] = str(self.arquivo_regras)
        stats["estrategia"] = self.nome
        stats["prioridade"] = self.prioridade

        return stats

    def __repr__(self) -> str:
        """Representação string da estratégia."""
        num_regras = len(self.engine.regras) if self.engine else 0
        return (
            f"EstrategiaRegras("
            f"nome='{self.nome}', "
            f"prioridade={self.prioridade}, "
            f"regras={num_regras}, "
            f"arquivo='{self.arquivo_regras}'"
            f")"
        )
