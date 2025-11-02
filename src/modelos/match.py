"""
Modelo de dados para Match (Conciliação).

Este módulo define a estrutura de um match entre lançamento e comprovante,
incluindo nível de confiança e método de matching utilizado.

Author: Pedro Luis
Date: 02/11/2025
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

# Imports dos outros modelos (serão resolvidos quando estiverem no mesmo pacote)
try:
    from .lancamento import Lancamento
    from .comprovante import Comprovante
except ImportError:
    # Para testes isolados
    from lancamento import Lancamento
    from comprovante import Comprovante


@dataclass
class Match:
    """
    Representa um match (conciliação) entre lançamento e comprovante.
    
    Um match é a correlação bem-sucedida entre um lançamento bancário
    e um comprovante de pagamento, com um nível de confiança associado.
    
    Attributes:
        lancamento: Lançamento do extrato bancário
        comprovante: Comprovante relacionado (pode ser None para regras automáticas)
        confianca: Nível de confiança do match (0.0 a 1.0)
        metodo: Método de matching usado ('exato', 'fuzzy', 'agregado', 'regra')
        observacoes: Observações sobre o match (opcional)
        timestamp: Data/hora do match (gerado automaticamente)
        confirmado: Indica se o match foi confirmado pelo usuário
        usuario: Usuário que confirmou o match (opcional)
        
    Examples:
        >>> from decimal import Decimal
        >>> from datetime import date
        >>> 
        >>> # Criar lançamento e comprovante
        >>> lanc = Lancamento(date(2025, 11, 2), Decimal('150.50'), 'Pagamento XYZ', 'D')
        >>> comp = Comprovante('nf_123.pdf', date(2025, 11, 2), Decimal('150.50'), confianca_ocr=0.95)
        >>> 
        >>> # Criar match com alta confiança
        >>> match = Match(
        ...     lancamento=lanc,
        ...     comprovante=comp,
        ...     confianca=0.98,
        ...     metodo='exato',
        ...     observacoes='Valor e data exatos'
        ... )
        >>> print(match)
        Match (exato, 98%): Pagamento XYZ ↔ nf_123.pdf [Alta confiança]
        
        >>> # Match com regra automática (sem comprovante)
        >>> match_tarifa = Match(
        ...     lancamento=lanc,
        ...     comprovante=None,
        ...     confianca=1.0,
        ...     metodo='regra',
        ...     observacoes='Tarifa bancária automática'
        ... )
    """
    
    lancamento: Lancamento
    comprovante: Optional[Comprovante]
    confianca: float
    metodo: str  # 'exato', 'fuzzy', 'agregado', 'regra'
    observacoes: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    confirmado: bool = False
    usuario: Optional[str] = None
    
    def __post_init__(self):
        """
        Validações executadas após a inicialização do objeto.
        
        Raises:
            ValueError: Se confiança estiver fora do intervalo [0, 1]
            ValueError: Se método não for válido
            ValueError: Se lançamento não for válido
        """
        # Validar confiança
        if not 0.0 <= self.confianca <= 1.0:
            raise ValueError(
                f"Confiança deve estar entre 0.0 e 1.0, "
                f"recebido: {self.confianca}"
            )
        
        # Validar método
        metodos_validos = ['exato', 'fuzzy', 'agregado', 'regra', 'manual']
        if self.metodo not in metodos_validos:
            raise ValueError(
                f"Método deve ser um dos seguintes: {metodos_validos}, "
                f"recebido: '{self.metodo}'"
            )
        
        # Validar lançamento
        if not isinstance(self.lancamento, Lancamento):
            raise ValueError(
                f"Lançamento deve ser uma instância de Lancamento, "
                f"recebido: {type(self.lancamento)}"
            )
        
        # Validar comprovante (se fornecido)
        if self.comprovante is not None and not isinstance(self.comprovante, Comprovante):
            raise ValueError(
                f"Comprovante deve ser uma instância de Comprovante, "
                f"recebido: {type(self.comprovante)}"
            )
        
        # Limpar observações
        if self.observacoes:
            self.observacoes = ' '.join(self.observacoes.split())
    
    @property
    def nivel_confianca(self) -> str:
        """
        Retorna nível de confiança como string descritiva.
        
        Returns:
            'Alta', 'Média' ou 'Baixa' baseado na confiança
            
        Examples:
            >>> from datetime import date
            >>> from decimal import Decimal
            >>> lanc = Lancamento(date.today(), Decimal('100'), 'Teste', 'D')
            >>> comp = Comprovante('teste.pdf', date.today(), Decimal('100'))
            >>> match = Match(lanc, comp, 0.95, 'exato')
            >>> match.nivel_confianca
            'Alta'
        """
        if self.confianca >= 0.9:
            return 'Alta'
        elif self.confianca >= 0.7:
            return 'Média'
        else:
            return 'Baixa'
    
    @property
    def cor_confianca(self) -> str:
        """
        Retorna cor para UI baseada na confiança.
        
        Returns:
            'green', 'yellow' ou 'red'
            
        Útil para interface Streamlit com indicadores coloridos.
        """
        if self.confianca >= 0.9:
            return 'green'
        elif self.confianca >= 0.7:
            return 'yellow'
        else:
            return 'red'
    
    @property
    def requer_revisao(self) -> bool:
        """
        Indica se o match requer revisão manual.
        
        Returns:
            True se confiança < 0.9 e não confirmado, False caso contrário
            
        Examples:
            >>> from datetime import date
            >>> from decimal import Decimal
            >>> lanc = Lancamento(date.today(), Decimal('100'), 'Teste', 'D')
            >>> comp = Comprovante('teste.pdf', date.today(), Decimal('100'))
            >>> 
            >>> # Match com alta confiança não requer revisão
            >>> match_alto = Match(lanc, comp, 0.95, 'exato')
            >>> match_alto.requer_revisao
            False
            >>> 
            >>> # Match com baixa confiança requer revisão
            >>> match_baixo = Match(lanc, comp, 0.75, 'fuzzy')
            >>> match_baixo.requer_revisao
            True
        """
        return self.confianca < 0.9 and not self.confirmado
    
    @property
    def pode_auto_aprovar(self) -> bool:
        """
        Indica se o match pode ser auto-aprovado.
        
        Returns:
            True se confiança >= 0.9, False caso contrário
            
        Matches com confiança >= 90% podem ser aprovados automaticamente
        sem intervenção humana.
        """
        return self.confianca >= 0.9
    
    def confirmar(self, usuario: Optional[str] = None) -> None:
        """
        Confirma o match manualmente.
        
        Args:
            usuario: Nome do usuário que confirmou (opcional)
            
        Examples:
            >>> from datetime import date
            >>> from decimal import Decimal
            >>> lanc = Lancamento(date.today(), Decimal('100'), 'Teste', 'D')
            >>> comp = Comprovante('teste.pdf', date.today(), Decimal('100'))
            >>> match = Match(lanc, comp, 0.75, 'fuzzy')
            >>> match.confirmar('Pedro Luis')
            >>> match.confirmado
            True
        """
        self.confirmado = True
        if usuario:
            self.usuario = usuario
        
        # Marcar lançamento e comprovante como conciliados
        self.lancamento.marcar_como_conciliado()
        if self.comprovante:
            self.comprovante.marcar_como_conciliado()
    
    def desfazer(self) -> None:
        """
        Desfaz a confirmação do match.
        
        Útil para corrigir matches incorretos.
        
        Examples:
            >>> from datetime import date
            >>> from decimal import Decimal
            >>> lanc = Lancamento(date.today(), Decimal('100'), 'Teste', 'D')
            >>> comp = Comprovante('teste.pdf', date.today(), Decimal('100'))
            >>> match = Match(lanc, comp, 0.95, 'exato')
            >>> match.confirmar()
            >>> match.desfazer()
            >>> match.confirmado
            False
        """
        self.confirmado = False
        self.usuario = None
        
        # Desmarcar lançamento e comprovante
        self.lancamento.desmarcar_conciliacao()
        if self.comprovante:
            self.comprovante.desmarcar_conciliacao()
    
    def __str__(self) -> str:
        """
        Representação amigável do match.
        
        Returns:
            String formatada com método, confiança, lançamento e comprovante
        """
        comp_info = self.comprovante.nome_arquivo if self.comprovante else 'Sem comprovante (regra)'
        confianca_pct = f'{self.confianca:.0%}'
        status = f' [CONFIRMADO]' if self.confirmado else ''
        nivel = f' [{self.nivel_confianca} confiança]'
        
        return (
            f"Match ({self.metodo}, {confianca_pct}): "
            f"{self.lancamento.descricao} ↔ {comp_info}{nivel}{status}"
        )
    
    def __repr__(self) -> str:
        """Representação técnica do objeto."""
        return (
            f"Match(lancamento={self.lancamento!r}, "
            f"comprovante={self.comprovante!r}, "
            f"confianca={self.confianca}, metodo={self.metodo!r}, "
            f"confirmado={self.confirmado})"
        )
    
    def to_dict(self) -> dict:
        """
        Converte o match para dicionário.
        
        Útil para serialização e exportação de dados.
        
        Returns:
            Dicionário com todos os atributos do match
            
        Examples:
            >>> from datetime import date
            >>> from decimal import Decimal
            >>> lanc = Lancamento(date.today(), Decimal('100'), 'Teste', 'D')
            >>> comp = Comprovante('teste.pdf', date.today(), Decimal('100'))
            >>> match = Match(lanc, comp, 0.95, 'exato')
            >>> dados = match.to_dict()
            >>> print(dados['metodo'])
            exato
        """
        return {
            'lancamento': self.lancamento.to_dict(),
            'comprovante': self.comprovante.to_dict() if self.comprovante else None,
            'confianca': self.confianca,
            'nivel_confianca': self.nivel_confianca,
            'metodo': self.metodo,
            'observacoes': self.observacoes,
            'timestamp': self.timestamp,
            'confirmado': self.confirmado,
            'usuario': self.usuario,
            'requer_revisao': self.requer_revisao,
            'pode_auto_aprovar': self.pode_auto_aprovar
        }


# Exceções customizadas para erros relacionados a matches
class MatchError(Exception):
    """Erro base para problemas relacionados a matches."""
    pass


class MatchInvalidoError(MatchError):
    """Erro quando um match possui dados inválidos."""
    pass


class MatchConflitanteError(MatchError):
    """Erro quando há conflito entre matches (ex: lançamento já conciliado)."""
    pass
