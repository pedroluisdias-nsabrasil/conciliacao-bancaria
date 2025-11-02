"""
Modelo de dados para Lançamento Bancário.

Este módulo define a estrutura de um lançamento do extrato bancário,
incluindo validações de dados e métodos auxiliares.

Author: Pedro Luis
Date: 02/11/2025
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Lancamento:
    """
    Representa um lançamento do extrato bancário.
    
    Um lançamento é uma movimentação financeira registrada no banco,
    podendo ser um débito (saída) ou crédito (entrada).
    
    Attributes:
        data: Data do lançamento
        valor: Valor da movimentação (sempre positivo, usar Decimal para precisão)
        descricao: Descrição/histórico do lançamento
        tipo: Tipo da movimentação - 'D' para débito, 'C' para crédito
        documento: Número do documento (opcional, ex: cheque, DOC, TED)
        categoria: Categoria do lançamento (opcional, ex: 'Alimentação', 'Transporte')
        saldo: Saldo após o lançamento (opcional)
        conciliado: Indica se o lançamento já foi conciliado (padrão: False)
        
    Examples:
        >>> from decimal import Decimal
        >>> from datetime import date
        >>> 
        >>> # Criar um débito (pagamento)
        >>> lancamento = Lancamento(
        ...     data=date(2025, 11, 2),
        ...     valor=Decimal('150.50'),
        ...     descricao='Pagamento fornecedor XYZ',
        ...     tipo='D'
        ... )
        >>> print(lancamento)
        Lancamento(02/11/2025, D, R$ 150.50): Pagamento fornecedor XYZ
        
        >>> # Criar um crédito (recebimento)
        >>> recebimento = Lancamento(
        ...     data=date(2025, 11, 1),
        ...     valor=Decimal('5000.00'),
        ...     descricao='Transferência recebida',
        ...     tipo='C',
        ...     documento='TED 12345'
        ... )
    """
    
    data: date
    valor: Decimal
    descricao: str
    tipo: str  # 'D' para débito, 'C' para crédito
    documento: Optional[str] = None
    categoria: Optional[str] = None
    saldo: Optional[Decimal] = None
    conciliado: bool = False
    
    def __post_init__(self):
        """
        Validações executadas após a inicialização do objeto.
        
        Raises:
            ValueError: Se tipo não for 'D' ou 'C'
            ValueError: Se valor for negativo ou zero
            ValueError: Se data for inválida
            ValueError: Se descrição estiver vazia
        """
        # Validar tipo
        if self.tipo not in ['D', 'C']:
            raise ValueError(
                f"Tipo deve ser 'D' (débito) ou 'C' (crédito), "
                f"recebido: '{self.tipo}'"
            )
        
        # Validar valor
        if self.valor <= 0:
            raise ValueError(
                f"Valor deve ser positivo, recebido: {self.valor}"
            )
        
        # Validar descrição
        if not self.descricao or not self.descricao.strip():
            raise ValueError("Descrição não pode estar vazia")
        
        # Limpar descrição (remover espaços extras)
        self.descricao = ' '.join(self.descricao.split())
        
        # Validar data (garante que é um objeto date válido)
        if not isinstance(self.data, date):
            raise ValueError(
                f"Data deve ser um objeto date, recebido: {type(self.data)}"
            )
    
    @property
    def valor_com_sinal(self) -> Decimal:
        """
        Retorna o valor com sinal apropriado.
        
        Returns:
            Valor positivo para crédito, negativo para débito
            
        Examples:
            >>> debito = Lancamento(date.today(), Decimal('100'), 'Teste', 'D')
            >>> debito.valor_com_sinal
            Decimal('-100')
            >>> 
            >>> credito = Lancamento(date.today(), Decimal('100'), 'Teste', 'C')
            >>> credito.valor_com_sinal
            Decimal('100')
        """
        return self.valor if self.tipo == 'C' else -self.valor
    
    @property
    def tipo_descritivo(self) -> str:
        """
        Retorna o tipo por extenso.
        
        Returns:
            'Débito' ou 'Crédito'
        """
        return 'Débito' if self.tipo == 'D' else 'Crédito'
    
    def marcar_como_conciliado(self) -> None:
        """
        Marca o lançamento como conciliado.
        
        Este método deve ser chamado após um match bem-sucedido.
        """
        self.conciliado = True
    
    def desmarcar_conciliacao(self) -> None:
        """
        Remove a marcação de conciliação.
        
        Útil para desfazer matches incorretos.
        """
        self.conciliado = False
    
    def __str__(self) -> str:
        """
        Representação amigável do lançamento.
        
        Returns:
            String formatada com data, tipo, valor e descrição
        """
        data_formatada = self.data.strftime('%d/%m/%Y')
        valor_formatado = f'R$ {self.valor:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
        status = ' [CONCILIADO]' if self.conciliado else ''
        return f"Lancamento({data_formatada}, {self.tipo}, {valor_formatado}): {self.descricao}{status}"
    
    def __repr__(self) -> str:
        """Representação técnica do objeto."""
        return (
            f"Lancamento(data={self.data!r}, valor={self.valor!r}, "
            f"descricao={self.descricao!r}, tipo={self.tipo!r}, "
            f"conciliado={self.conciliado})"
        )
    
    def to_dict(self) -> dict:
        """
        Converte o lançamento para dicionário.
        
        Útil para serialização e exportação de dados.
        
        Returns:
            Dicionário com todos os atributos do lançamento
            
        Examples:
            >>> lancamento = Lancamento(date.today(), Decimal('100'), 'Teste', 'D')
            >>> dados = lancamento.to_dict()
            >>> print(dados['tipo'])
            D
        """
        return {
            'data': self.data,
            'valor': self.valor,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'documento': self.documento,
            'categoria': self.categoria,
            'saldo': self.saldo,
            'conciliado': self.conciliado,
            'valor_com_sinal': self.valor_com_sinal,
            'tipo_descritivo': self.tipo_descritivo
        }


# Exceção customizada para erros relacionados a lançamentos
class LancamentoError(Exception):
    """Erro base para problemas relacionados a lançamentos."""
    pass


class LancamentoInvalidoError(LancamentoError):
    """Erro quando um lançamento possui dados inválidos."""
    pass
