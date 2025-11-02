"""
Modelo de dados para Comprovante de Pagamento.

Este módulo define a estrutura de um comprovante extraído de arquivo PDF/imagem,
incluindo dados do OCR e metadados do arquivo.

Author: Pedro Luis
Date: 02/11/2025
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional


@dataclass
class Comprovante:
    """
    Representa um comprovante de pagamento extraído de arquivo.
    
    Um comprovante é um documento (PDF, imagem) que comprova um pagamento,
    contendo informações extraídas via OCR ou leitura de PDF texto.
    
    Attributes:
        arquivo: Caminho do arquivo do comprovante
        data: Data do pagamento/comprovante
        valor: Valor do comprovante (usar Decimal para precisão)
        beneficiario: Nome do beneficiário/fornecedor (opcional)
        descricao: Descrição/observação extraída (opcional)
        tipo_documento: Tipo do documento (ex: 'Nota Fiscal', 'Recibo', 'Boleto')
        numero_documento: Número do documento (opcional)
        confianca_ocr: Confiança da extração OCR (0.0 a 1.0)
        texto_completo: Texto completo extraído do documento (opcional)
        data_extracao: Timestamp da extração (gerado automaticamente)
        conciliado: Indica se o comprovante já foi conciliado (padrão: False)
        
    Examples:
        >>> from decimal import Decimal
        >>> from datetime import date
        >>> 
        >>> # Criar comprovante de nota fiscal
        >>> nf = Comprovante(
        ...     arquivo='comprovantes/nf_123.pdf',
        ...     data=date(2025, 11, 2),
        ...     valor=Decimal('150.50'),
        ...     beneficiario='Fornecedor XYZ Ltda',
        ...     tipo_documento='Nota Fiscal',
        ...     numero_documento='NF-123456',
        ...     confianca_ocr=0.95
        ... )
        >>> print(nf)
        Comprovante(nf_123.pdf): R$ 150.50 - Fornecedor XYZ Ltda (95%)
        
        >>> # Criar comprovante de boleto
        >>> boleto = Comprovante(
        ...     arquivo='comprovantes/boleto_luz.pdf',
        ...     data=date(2025, 10, 30),
        ...     valor=Decimal('250.00'),
        ...     beneficiario='Companhia de Energia',
        ...     tipo_documento='Boleto',
        ...     confianca_ocr=0.88
        ... )
    """
    
    arquivo: str
    data: date
    valor: Decimal
    beneficiario: Optional[str] = None
    descricao: Optional[str] = None
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None
    confianca_ocr: float = 0.0
    texto_completo: Optional[str] = None
    data_extracao: datetime = field(default_factory=datetime.now)
    conciliado: bool = False
    
    def __post_init__(self):
        """
        Validações executadas após a inicialização do objeto.
        
        Raises:
            ValueError: Se valor for negativo ou zero
            ValueError: Se confiança OCR estiver fora do intervalo [0, 1]
            ValueError: Se data for inválida
            ValueError: Se arquivo estiver vazio
        """
        # Validar arquivo
        if not self.arquivo or not self.arquivo.strip():
            raise ValueError("Caminho do arquivo não pode estar vazio")
        
        # Validar valor
        if self.valor <= 0:
            raise ValueError(
                f"Valor deve ser positivo, recebido: {self.valor}"
            )
        
        # Validar confiança OCR
        if not 0.0 <= self.confianca_ocr <= 1.0:
            raise ValueError(
                f"Confiança OCR deve estar entre 0.0 e 1.0, "
                f"recebido: {self.confianca_ocr}"
            )
        
        # Validar data
        if not isinstance(self.data, date):
            raise ValueError(
                f"Data deve ser um objeto date, recebido: {type(self.data)}"
            )
        
        # Limpar campos de texto (remover espaços extras)
        if self.beneficiario:
            self.beneficiario = ' '.join(self.beneficiario.split())
        
        if self.descricao:
            self.descricao = ' '.join(self.descricao.split())
        
        # Normalizar caminho do arquivo
        self.arquivo = str(Path(self.arquivo).as_posix())
    
    @property
    def nome_arquivo(self) -> str:
        """
        Retorna apenas o nome do arquivo sem o caminho.
        
        Returns:
            Nome do arquivo
            
        Examples:
            >>> comp = Comprovante('dados/entrada/nf_123.pdf', date.today(), Decimal('100'))
            >>> comp.nome_arquivo
            'nf_123.pdf'
        """
        return Path(self.arquivo).name
    
    @property
    def extensao_arquivo(self) -> str:
        """
        Retorna a extensão do arquivo.
        
        Returns:
            Extensão do arquivo (incluindo o ponto)
            
        Examples:
            >>> comp = Comprovante('nf_123.pdf', date.today(), Decimal('100'))
            >>> comp.extensao_arquivo
            '.pdf'
        """
        return Path(self.arquivo).suffix
    
    @property
    def nivel_confianca_ocr(self) -> str:
        """
        Retorna o nível de confiança do OCR como string descritiva.
        
        Returns:
            'Alta', 'Média' ou 'Baixa' baseado na confiança
            
        Examples:
            >>> comp = Comprovante('teste.pdf', date.today(), Decimal('100'), confianca_ocr=0.95)
            >>> comp.nivel_confianca_ocr
            'Alta'
        """
        if self.confianca_ocr >= 0.9:
            return 'Alta'
        elif self.confianca_ocr >= 0.7:
            return 'Média'
        else:
            return 'Baixa'
    
    @property
    def cor_confianca_ocr(self) -> str:
        """
        Retorna cor para UI baseada na confiança do OCR.
        
        Returns:
            'green', 'yellow' ou 'red'
            
        Útil para interface Streamlit com indicadores coloridos.
        """
        if self.confianca_ocr >= 0.9:
            return 'green'
        elif self.confianca_ocr >= 0.7:
            return 'yellow'
        else:
            return 'red'
    
    def marcar_como_conciliado(self) -> None:
        """
        Marca o comprovante como conciliado.
        
        Este método deve ser chamado após um match bem-sucedido.
        """
        self.conciliado = True
    
    def desmarcar_conciliacao(self) -> None:
        """
        Remove a marcação de conciliação.
        
        Útil para desfazer matches incorretos.
        """
        self.conciliado = False
    
    def tem_boa_qualidade(self) -> bool:
        """
        Verifica se o comprovante tem boa qualidade de extração.
        
        Returns:
            True se confiança OCR >= 0.8, False caso contrário
            
        Examples:
            >>> comp_bom = Comprovante('teste.pdf', date.today(), Decimal('100'), confianca_ocr=0.9)
            >>> comp_bom.tem_boa_qualidade()
            True
            >>> 
            >>> comp_ruim = Comprovante('teste.pdf', date.today(), Decimal('100'), confianca_ocr=0.6)
            >>> comp_ruim.tem_boa_qualidade()
            False
        """
        return self.confianca_ocr >= 0.8
    
    def __str__(self) -> str:
        """
        Representação amigável do comprovante.
        
        Returns:
            String formatada com nome do arquivo, valor, beneficiário e confiança
        """
        valor_formatado = f'R$ {self.valor:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
        beneficiario_info = f' - {self.beneficiario}' if self.beneficiario else ''
        confianca_pct = f' ({self.confianca_ocr:.0%})' if self.confianca_ocr > 0 else ''
        status = ' [CONCILIADO]' if self.conciliado else ''
        return f"Comprovante({self.nome_arquivo}): {valor_formatado}{beneficiario_info}{confianca_pct}{status}"
    
    def __repr__(self) -> str:
        """Representação técnica do objeto."""
        return (
            f"Comprovante(arquivo={self.arquivo!r}, data={self.data!r}, "
            f"valor={self.valor!r}, confianca_ocr={self.confianca_ocr}, "
            f"conciliado={self.conciliado})"
        )
    
    def to_dict(self) -> dict:
        """
        Converte o comprovante para dicionário.
        
        Útil para serialização e exportação de dados.
        
        Returns:
            Dicionário com todos os atributos do comprovante
            
        Examples:
            >>> comp = Comprovante('teste.pdf', date.today(), Decimal('100'))
            >>> dados = comp.to_dict()
            >>> print(dados['nome_arquivo'])
            teste.pdf
        """
        return {
            'arquivo': self.arquivo,
            'nome_arquivo': self.nome_arquivo,
            'data': self.data,
            'valor': self.valor,
            'beneficiario': self.beneficiario,
            'descricao': self.descricao,
            'tipo_documento': self.tipo_documento,
            'numero_documento': self.numero_documento,
            'confianca_ocr': self.confianca_ocr,
            'nivel_confianca_ocr': self.nivel_confianca_ocr,
            'texto_completo': self.texto_completo,
            'data_extracao': self.data_extracao,
            'conciliado': self.conciliado
        }


# Exceções customizadas para erros relacionados a comprovantes
class ComprovanteError(Exception):
    """Erro base para problemas relacionados a comprovantes."""
    pass


class ComprovanteInvalidoError(ComprovanteError):
    """Erro quando um comprovante possui dados inválidos."""
    pass


class OCRError(ComprovanteError):
    """Erro durante a extração OCR do comprovante."""
    pass
