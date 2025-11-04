"""
Leitor de arquivos CSV de extratos bancários.

Este módulo implementa a leitura e parsing de arquivos CSV de diferentes bancos,
convertendo-os em uma lista de objetos Lancamento padronizados.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date

import pandas as pd

from ..modelos import Lancamento
from .normalizadores import (
    normalizar_data,
    normalizar_valor,
    limpar_descricao,
    identificar_tipo_lancamento,
)

logger = logging.getLogger(__name__)


class LeitorCSVError(Exception):
    """Exceção base para erros do LeitorCSV."""
    pass


class FormatoNaoReconhecidoError(LeitorCSVError):
    """Formato de CSV não reconhecido."""
    pass


class ArquivoInvalidoError(LeitorCSVError):
    """Arquivo CSV inválido ou corrompido."""
    pass


class LeitorCSV:
    """
    Leitor de arquivos CSV de extratos bancários.
    
    Suporta diferentes formatos de bancos brasileiros e detecta
    automaticamente o layout do arquivo.
    
    Examples:
        >>> leitor = LeitorCSV()
        >>> lancamentos = leitor.ler_arquivo('extrato_novembro.csv')
        >>> print(f"Lidos {len(lancamentos)} lançamentos")
        Lidos 150 lançamentos
        
        >>> # Forçar banco específico
        >>> leitor = LeitorCSV(banco='itau')
        >>> lancamentos = leitor.ler_arquivo('extrato.csv')
    """
    
    # Mapeamentos de colunas por banco
    MAPEAMENTOS = {
        'itau': {
            'data': ['data', 'data lancamento', 'dt lancamento'],
            'valor': ['valor', 'valor r$', 'vlr lancamento'],
            'descricao': ['descricao', 'descrição', 'historico', 'histórico'],
            'tipo': ['tipo', 'd/c', 'dc'],
        },
        'bradesco': {
            'data': ['data', 'data movto', 'data movimento'],
            'valor': ['valor', 'valor r$'],
            'descricao': ['historico', 'histórico', 'descricao'],
            'tipo': ['tipo', 'd/c'],
        },
        'generico': {
            'data': ['data', 'dt', 'date'],
            'valor': ['valor', 'value', 'vlr'],
            'descricao': ['descricao', 'descrição', 'historico', 'histórico', 'description'],
            'tipo': ['tipo', 'type', 'd/c', 'dc'],
        }
    }
    
    def __init__(self, banco: Optional[str] = None):
        """
        Inicializa o leitor CSV.
        
        Args:
            banco: Nome do banco ('itau', 'bradesco', etc).
                   Se None, tentará detectar automaticamente.
        """
        self.banco = banco
        self._df: Optional[pd.DataFrame] = None
        self._mapeamento: Dict[str, str] = {}
        
    def ler_arquivo(
        self,
        caminho: str,
        encoding: str = 'utf-8',
        separador: str = ';',
        decimal: str = ',',
        pular_linhas: int = 0
    ) -> List[Lancamento]:
        """
        Lê um arquivo CSV e retorna lista de Lançamentos.
        
        Args:
            caminho: Caminho para o arquivo CSV
            encoding: Encoding do arquivo (padrão: utf-8)
            separador: Separador de colunas (padrão: ;)
            decimal: Separador decimal (padrão: ,)
            pular_linhas: Número de linhas a pular no início (padrão: 0)
            
        Returns:
            Lista de objetos Lancamento
            
        Raises:
            ArquivoInvalidoError: Se o arquivo não puder ser lido
            FormatoNaoReconhecidoError: Se o formato não for reconhecido
            
        Examples:
            >>> leitor = LeitorCSV()
            >>> lancamentos = leitor.ler_arquivo('extrato.csv')
            >>> lancamentos = leitor.ler_arquivo('extrato.csv', encoding='latin-1')
        """
        arquivo = Path(caminho)
        
        if not arquivo.exists():
            raise ArquivoInvalidoError(f"Arquivo não encontrado: {caminho}")
        
        if not arquivo.suffix.lower() in ['.csv', '.txt']:
            raise ArquivoInvalidoError(f"Extensão não suportada: {arquivo.suffix}")
        
        logger.info(f"Lendo arquivo CSV: {caminho}")
        
        try:
            # Ler CSV com pandas
            self._df = pd.read_csv(
                caminho,
                encoding=encoding,
                sep=separador,
                decimal=decimal,
                skiprows=pular_linhas,
                dtype=str,  # Ler tudo como string primeiro
            )
            
            logger.info(f"Arquivo lido: {len(self._df)} linhas, {len(self._df.columns)} colunas")
            
        except Exception as e:
            # Tentar com encoding alternativo
            if encoding == 'utf-8':
                logger.warning(f"Falha com UTF-8, tentando latin-1...")
                try:
                    self._df = pd.read_csv(
                        caminho,
                        encoding='latin-1',
                        sep=separador,
                        decimal=decimal,
                        skiprows=pular_linhas,
                        dtype=str,
                    )
                except Exception as e2:
                    raise ArquivoInvalidoError(f"Erro ao ler arquivo: {e2}")
            else:
                raise ArquivoInvalidoError(f"Erro ao ler arquivo: {e}")
        
        # Limpar nomes das colunas
        self._df.columns = self._df.columns.str.strip().str.lower()
        
        # Detectar formato se não especificado
        if not self.banco:
            self.banco = self._detectar_formato()
            logger.info(f"Formato detectado: {self.banco}")
        
        # Mapear colunas
        self._mapear_colunas()
        
        # Processar linhas
        lancamentos = self._processar_linhas()
        
        logger.info(f"✓ {len(lancamentos)} lançamentos extraídos com sucesso")
        
        return lancamentos
    
    def _detectar_formato(self) -> str:
        """
        Detecta o formato do CSV baseado nos nomes das colunas.
        
        Returns:
            Nome do banco detectado ou 'generico'
        """
        if self._df is None:
            return 'generico'
        
        colunas = set(self._df.columns)
        
        # Verificar Itaú (geralmente tem "data lancamento")
        if any('lancamento' in col for col in colunas):
            return 'itau'
        
        # Verificar Bradesco (geralmente tem "data movto")
        if any('movto' in col or 'movimento' in col for col in colunas):
            return 'bradesco'
        
        # Default para genérico
        logger.warning("Formato não reconhecido especificamente, usando mapeamento genérico")
        return 'generico'
    
    def _mapear_colunas(self) -> None:
        """
        Mapeia as colunas do CSV para campos padrão.
        
        Raises:
            FormatoNaoReconhecidoError: Se colunas essenciais não forem encontradas
        """
        if self._df is None:
            raise FormatoNaoReconhecidoError("DataFrame não carregado")
        
        mapeamento_banco = self.MAPEAMENTOS.get(self.banco, self.MAPEAMENTOS['generico'])
        colunas_df = set(self._df.columns)
        
        # Mapear cada campo essencial
        for campo, possiveis_nomes in mapeamento_banco.items():
            encontrado = None
            for nome in possiveis_nomes:
                if nome in colunas_df:
                    encontrado = nome
                    break
            
            if encontrado:
                self._mapeamento[campo] = encontrado
            elif campo in ['data', 'valor', 'descricao']:
                # Campos essenciais
                raise FormatoNaoReconhecidoError(
                    f"Coluna '{campo}' não encontrada. Colunas disponíveis: {list(colunas_df)}"
                )
            # Campo 'tipo' é opcional (pode ser inferido)
        
        logger.debug(f"Mapeamento de colunas: {self._mapeamento}")
    
    def _processar_linhas(self) -> List[Lancamento]:
        """
        Processa cada linha do DataFrame e cria Lançamentos.
        
        Returns:
            Lista de Lançamentos válidos
        """
        lancamentos: List[Lancamento] = []
        erros = 0
        
        for idx, row in self._df.iterrows():
            try:
                lancamento = self._processar_linha(row)
                lancamentos.append(lancamento)
            except Exception as e:
                erros += 1
                logger.warning(f"Erro na linha {idx + 1}: {e}")
                # Continuar processando outras linhas
                continue
        
        if erros > 0:
            logger.warning(f"⚠ {erros} linhas com erro foram ignoradas")
        
        return lancamentos
    
    def _processar_linha(self, row: pd.Series) -> Lancamento:
        """
        Processa uma linha do CSV e cria um Lançamento.
        
        Args:
            row: Linha do DataFrame
            
        Returns:
            Objeto Lancamento
            
        Raises:
            ValueError: Se a linha não puder ser processada
        """
        # Extrair valores usando mapeamento
        data_str = str(row[self._mapeamento['data']]).strip()
        valor_str = str(row[self._mapeamento['valor']]).strip()
        descricao_str = str(row[self._mapeamento['descricao']]).strip()
        
        # Pegar tipo se existir
        tipo_str = None
        if 'tipo' in self._mapeamento:
            tipo_str = str(row[self._mapeamento['tipo']]).strip()
        
        # Normalizar
        data_lancamento = normalizar_data(data_str)
        valor_lancamento = normalizar_valor(valor_str)
        descricao_limpa = limpar_descricao(descricao_str)
        
        # Identificar tipo (D ou C)
        tipo_lancamento = identificar_tipo_lancamento(
            descricao_limpa,
            valor_lancamento,
            tipo_str
        )
        
        # Criar Lançamento
        return Lancamento(
            data=data_lancamento,
            valor=valor_lancamento,
            descricao=descricao_limpa,
            tipo=tipo_lancamento,
        )
    
    def obter_resumo(self) -> Dict[str, Any]:
        """
        Retorna resumo dos dados lidos.
        
        Returns:
            Dicionário com estatísticas do arquivo
        """
        if self._df is None:
            return {}
        
        return {
            'total_linhas': len(self._df),
            'colunas': list(self._df.columns),
            'banco_detectado': self.banco,
            'mapeamento': self._mapeamento,
        }
