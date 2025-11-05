"""
Leitor de arquivos PDF de extratos bancários.

Este módulo implementa a leitura e parsing de arquivos PDF de diferentes bancos,
convertendo-os em uma lista de objetos Lancamento padronizados.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date

try:
    import pdfplumber

    PDFPLUMBER_DISPONIVEL = True
except ImportError:
    PDFPLUMBER_DISPONIVEL = False

from ..modelos import Lancamento
from .normalizadores import (
    normalizar_data,
    normalizar_valor,
    limpar_descricao,
    identificar_tipo_lancamento,
)

logger = logging.getLogger(__name__)


class LeitorPDFError(Exception):
    """Exceção base para erros do LeitorPDF."""

    pass


class PDFNaoSuportadoError(LeitorPDFError):
    """PDF não suportado ou biblioteca não instalada."""

    pass


class PDFSemConteudoError(LeitorPDFError):
    """PDF não contém texto extraível."""

    pass


class LeitorPDF:
    """
    Leitor de arquivos PDF de extratos bancários.

    Extrai texto e tabelas de PDFs, convertendo em objetos Lancamento.
    Requer a biblioteca pdfplumber instalada.

    Examples:
        >>> leitor = LeitorPDF()
        >>> lancamentos = leitor.ler_arquivo('extrato.pdf')
        >>> print(f"Lidos {len(lancamentos)} lançamentos")
        Lidos 45 lançamentos

        >>> # Com configuração de colunas personalizada
        >>> leitor = LeitorPDF(
        ...     indices_colunas={'data': 0, 'valor': 2, 'descricao': 1}
        ... )
        >>> lancamentos = leitor.ler_arquivo('extrato_personalizado.pdf')
    """

    # Índices padrão das colunas em tabelas de extrato
    INDICES_PADRAO = {
        "data": 0,
        "descricao": 1,
        "valor": 2,
        "tipo": 3,  # Opcional
    }

    def __init__(
        self,
        indices_colunas: Optional[Dict[str, int]] = None,
        primeira_pagina: int = 1,
        ultima_pagina: Optional[int] = None,
    ):
        """
        Inicializa o leitor PDF.

        Args:
            indices_colunas: Mapeamento de campo → índice da coluna.
                           Se None, usa INDICES_PADRAO.
            primeira_pagina: Primeira página a ler (1-indexed)
            ultima_pagina: Última página a ler (None = todas)

        Raises:
            PDFNaoSuportadoError: Se pdfplumber não estiver instalado
        """
        if not PDFPLUMBER_DISPONIVEL:
            raise PDFNaoSuportadoError(
                "Biblioteca pdfplumber não instalada. "
                "Instale com: pip install pdfplumber"
            )

        self.indices = indices_colunas or self.INDICES_PADRAO.copy()
        self.primeira_pagina = primeira_pagina
        self.ultima_pagina = ultima_pagina
        self._pdf = None
        self._total_paginas = 0

    def ler_arquivo(
        self, caminho: str, usar_tabelas: bool = True, min_colunas: int = 3
    ) -> List[Lancamento]:
        """
        Lê um arquivo PDF e retorna lista de Lançamentos.

        Args:
            caminho: Caminho para o arquivo PDF
            usar_tabelas: Se True, tenta extrair como tabela primeiro
            min_colunas: Número mínimo de colunas para considerar uma linha válida

        Returns:
            Lista de objetos Lancamento

        Raises:
            PDFNaoSuportadoError: Se o arquivo não puder ser lido
            PDFSemConteudoError: Se não houver texto extraível

        Examples:
            >>> leitor = LeitorPDF()
            >>> lancamentos = leitor.ler_arquivo('extrato.pdf')
            >>> lancamentos = leitor.ler_arquivo('extrato.pdf', usar_tabelas=False)
        """
        arquivo = Path(caminho)

        # Validação de extensão
        if arquivo.suffix.lower() != ".pdf":
            raise PDFNaoSuportadoError(f"Não é um arquivo PDF: {arquivo.suffix}")

        logger.info(f"Lendo arquivo PDF: {caminho}")

        try:
            # Abrir PDF
            self._pdf = pdfplumber.open(caminho)
            self._total_paginas = len(self._pdf.pages)

            logger.info(f"PDF aberto: {self._total_paginas} páginas")

            # Determinar intervalo de páginas
            inicio = self.primeira_pagina - 1  # Converter para 0-indexed
            fim = self.ultima_pagina or self._total_paginas

            if inicio < 0 or inicio >= self._total_paginas:
                raise PDFNaoSuportadoError(
                    f"Página inicial inválida: {self.primeira_pagina}"
                )

            # Extrair lançamentos de todas as páginas
            todos_lancamentos = []

            for num_pagina in range(inicio, fim):
                try:
                    pagina = self._pdf.pages[num_pagina]

                    if usar_tabelas:
                        # Tentar extrair como tabela
                        lancamentos = self._extrair_de_tabela(pagina, min_colunas)
                    else:
                        # Extrair como texto livre
                        lancamentos = self._extrair_de_texto(pagina)

                    todos_lancamentos.extend(lancamentos)

                    logger.debug(
                        f"Página {num_pagina + 1}: "
                        f"{len(lancamentos)} lançamentos extraídos"
                    )

                except Exception as e:
                    logger.warning(f"Erro ao processar página {num_pagina + 1}: {e}")
                    continue

            # Fechar PDF
            self._pdf.close()

            if not todos_lancamentos:
                raise PDFSemConteudoError(
                    "Nenhum lançamento extraído. "
                    "PDF pode estar vazio ou ser imagem escaneada."
                )

            logger.info(
                f"✓ {len(todos_lancamentos)} lançamentos extraídos "
                f"de {fim - inicio} página(s)"
            )

            return todos_lancamentos

        except pdfplumber.pdfminer.pdfparser.PDFSyntaxError as e:
            raise PDFNaoSuportadoError(f"PDF corrompido ou inválido: {e}")

        except FileNotFoundError:
            raise PDFNaoSuportadoError(f"Arquivo não encontrado: {caminho}")

        except PDFSemConteudoError:
            raise  # Re-lançar sem transformar

        except Exception as e:
            if self._pdf:
                self._pdf.close()
            raise PDFNaoSuportadoError(f"Erro ao ler PDF: {e}")

    def _extrair_de_tabela(self, pagina, min_colunas: int) -> List[Lancamento]:
        """
        Extrai lançamentos de uma página usando detecção de tabelas.

        Args:
            pagina: Objeto página do pdfplumber
            min_colunas: Número mínimo de colunas

        Returns:
            Lista de Lançamentos extraídos
        """
        lancamentos = []

        # Extrair todas as tabelas da página
        tabelas = pagina.extract_tables()

        if not tabelas:
            logger.debug("Nenhuma tabela encontrada, tentando texto livre")
            return self._extrair_de_texto(pagina)

        for tabela in tabelas:
            for linha in tabela:
                # Pular linhas vazias ou com poucas colunas
                if not linha or len([c for c in linha if c]) < min_colunas:
                    continue

                # Pular cabeçalhos (heurística simples)
                primeira_coluna = str(linha[0] or "").strip().upper()
                if primeira_coluna in ["DATA", "DT", "DATE"]:
                    continue

                try:
                    lancamento = self._processar_linha_tabela(linha)
                    lancamentos.append(lancamento)
                except Exception as e:
                    logger.debug(f"Erro ao processar linha: {e}")
                    continue

        return lancamentos

    def _extrair_de_texto(self, pagina) -> List[Lancamento]:
        """
        Extrai lançamentos de uma página como texto livre.

        Args:
            pagina: Objeto página do pdfplumber

        Returns:
            Lista de Lançamentos extraídos
        """
        lancamentos = []

        # Extrair texto da página
        texto = pagina.extract_text()

        if not texto:
            return lancamentos

        # Processar linha por linha
        linhas = texto.split("\n")

        for linha in linhas:
            linha = linha.strip()

            if not linha:
                continue

            # Tentar extrair lançamento da linha
            try:
                # Dividir por espaços múltiplos ou tabs
                partes = linha.split()

                if len(partes) < 3:
                    continue

                lancamento = self._processar_linha_texto(partes)
                lancamentos.append(lancamento)

            except Exception as e:
                logger.debug(f"Erro ao processar linha de texto: {e}")
                continue

        return lancamentos

    def _processar_linha_tabela(self, linha: List[str]) -> Lancamento:
        """
        Processa uma linha de tabela e cria um Lançamento.

        Args:
            linha: Lista com valores das colunas

        Returns:
            Objeto Lancamento

        Raises:
            ValueError: Se a linha não puder ser processada
        """
        # Extrair valores usando índices configurados
        idx_data = self.indices.get("data", 0)
        idx_descricao = self.indices.get("descricao", 1)
        idx_valor = self.indices.get("valor", 2)
        idx_tipo = self.indices.get("tipo", None)

        # Validar índices
        if idx_data >= len(linha) or idx_valor >= len(linha):
            raise ValueError("Linha com colunas insuficientes")

        # Extrair e processar dados
        data_str = str(linha[idx_data] or "").strip()
        descricao_str = str(linha[idx_descricao] or "").strip()
        valor_str = str(linha[idx_valor] or "").strip()

        tipo_str = None
        if idx_tipo is not None and idx_tipo < len(linha):
            tipo_str = str(linha[idx_tipo] or "").strip()

        # Validar dados mínimos
        if not data_str or not valor_str:
            raise ValueError("Data ou valor ausente")

        # Normalizar
        data_lancamento = normalizar_data(data_str)
        valor_lancamento = normalizar_valor(valor_str)
        descricao_limpa = limpar_descricao(descricao_str) or "SEM DESCRIÇÃO"

        # Identificar tipo
        tipo_lancamento = identificar_tipo_lancamento(
            descricao_limpa, valor_lancamento, tipo_str
        )

        # Criar Lançamento
        return Lancamento(
            data=data_lancamento,
            valor=valor_lancamento,
            descricao=descricao_limpa,
            tipo=tipo_lancamento,
        )

    def _processar_linha_texto(self, partes: List[str]) -> Lancamento:
        """
        Processa uma linha de texto livre e cria um Lançamento.

        Assume formato: DATA DESCRICAO... VALOR [TIPO]

        Args:
            partes: Lista de palavras da linha

        Returns:
            Objeto Lancamento

        Raises:
            ValueError: Se a linha não puder ser processada
        """
        # Primeira parte deve ser data
        data_str = partes[0]

        # Última parte é valor (ou penúltima se última for tipo D/C)
        ultima = partes[-1].upper()
        if ultima in ["D", "C", "DEBITO", "CREDITO", "DEB", "CRED"]:
            valor_str = partes[-2]
            tipo_str = ultima
            descricao_partes = partes[1:-2]
        else:
            valor_str = partes[-1]
            tipo_str = None
            descricao_partes = partes[1:-1]

        # Montar descrição
        descricao_str = " ".join(descricao_partes)

        # Normalizar
        data_lancamento = normalizar_data(data_str)
        valor_lancamento = normalizar_valor(valor_str)
        descricao_limpa = limpar_descricao(descricao_str) or "SEM DESCRIÇÃO"

        # Identificar tipo
        tipo_lancamento = identificar_tipo_lancamento(
            descricao_limpa, valor_lancamento, tipo_str
        )

        # Criar Lançamento
        return Lancamento(
            data=data_lancamento,
            valor=valor_lancamento,
            descricao=descricao_limpa,
            tipo=tipo_lancamento,
        )

    def obter_info_pdf(self, caminho: str) -> Dict[str, Any]:
        """
        Retorna informações sobre o PDF.

        Args:
            caminho: Caminho para o arquivo PDF

        Returns:
            Dicionário com informações do PDF
        """
        try:
            with pdfplumber.open(caminho) as pdf:
                return {
                    "total_paginas": len(pdf.pages),
                    "metadata": pdf.metadata,
                    "tem_tabelas": any(page.extract_tables() for page in pdf.pages),
                }
        except Exception as e:
            logger.error(f"Erro ao obter informações do PDF: {e}")
            return {}
