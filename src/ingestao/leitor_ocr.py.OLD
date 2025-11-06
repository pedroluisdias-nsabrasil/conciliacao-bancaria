"""
Leitor OCR para Comprovantes.

Este módulo fornece funcionalidades para extrair dados de comprovantes
de pagamento em formato PDF ou imagem usando OCR (Optical Character Recognition).

Features:
- Extração de texto via Tesseract
- Identificação de valores monetários
- Identificação de datas
- Cálculo de confiança do OCR
- Suporte a PDF e imagens (PNG, JPG, etc)

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Date: 03/11/2025
Sprint: 2 - OCR
"""

import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from datetime import date, datetime

# Importações externas
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# Importações locais
from ..modelos import Comprovante
from .normalizadores import normalizar_data, normalizar_valor
from .preprocessador import Preprocessador

logger = logging.getLogger(__name__)


class LeitorOCRError(Exception):
    """Erro base do leitor OCR."""

    pass


class TesseractNaoEncontradoError(LeitorOCRError):
    """Tesseract OCR não encontrado no sistema."""

    pass


class ExtracaoOCRError(LeitorOCRError):
    """Erro durante extração de texto via OCR."""

    pass


class LeitorOCR:
    """
    Leitor de comprovantes usando OCR.

    Extrai dados de comprovantes de pagamento em PDF ou imagem,
    identificando valores, datas e calculando confiança da extração.

    Attributes:
        preprocessador: Preprocessador de imagens
        confianca_minima: Confiança mínima aceitável (0.0 a 1.0)
        idioma: Idioma do Tesseract ('por' para português)

    Examples:
        >>> leitor = LeitorOCR()
        >>> comprovante = leitor.ler_arquivo('comprovante.pdf')
        >>> print(f"Valor: R$ {comprovante.valor}")
        >>> print(f"Confiança: {comprovante.confianca_ocr:.0%}")

        >>> # Configuração personalizada
        >>> leitor = LeitorOCR(
        ...     confianca_minima=0.7,
        ...     preprocessar=True
        ... )
        >>> comprovantes = leitor.ler_arquivo('comprovante_multiplo.pdf')
    """

    # Padrões regex para extração
    REGEX_VALOR = re.compile(r"R\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2}))", re.IGNORECASE)

    REGEX_DATA = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")

    # Caminhos possíveis do Tesseract no Windows
    TESSERACT_PATHS = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Arquivos de Programas\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    def __init__(
        self,
        confianca_minima: float = 0.6,
        preprocessar: bool = True,
        idioma: str = "por",
    ):
        """
        Inicializa o leitor OCR.

        Args:
            confianca_minima: Confiança mínima aceitável (0.0 a 1.0)
            preprocessar: Se True, preprocessa imagens antes do OCR
            idioma: Idioma do Tesseract ('por', 'eng', etc)

        Raises:
            ValueError: Se confianca_minima não está entre 0 e 1
            TesseractNaoEncontradoError: Se Tesseract não encontrado
        """
        if not 0.0 <= confianca_minima <= 1.0:
            raise ValueError(
                f"confianca_minima deve estar entre 0 e 1, "
                f"recebido: {confianca_minima}"
            )

        self.confianca_minima = confianca_minima
        self.preprocessar = preprocessar
        self.idioma = idioma

        # Configurar preprocessador
        self.preprocessador = (
            Preprocessador(
                escala_cinza=True, binarizar=True, contraste=1.8, remover_ruido=True
            )
            if preprocessar
            else None
        )

        # Configurar Tesseract
        self._configurar_tesseract()

        logger.info(
            f"LeitorOCR criado: confianca_min={confianca_minima}, "
            f"idioma={idioma}, preprocessar={preprocessar}"
        )

    def _configurar_tesseract(self) -> None:
        """
        Configura o caminho do Tesseract automaticamente.

        Tenta encontrar o Tesseract nos caminhos comuns do Windows.

        Raises:
            TesseractNaoEncontradoError: Se Tesseract não encontrado
        """
        # Tentar detectar automaticamente
        for caminho in self.TESSERACT_PATHS:
            if Path(caminho).exists():
                pytesseract.pytesseract.tesseract_cmd = caminho
                logger.info(f"Tesseract encontrado: {caminho}")
                return

        # Tentar usar do PATH (Linux/Mac ou Windows com PATH configurado)
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract encontrado no PATH do sistema")
            return
        except Exception:
            pass

        # Não encontrado
        raise TesseractNaoEncontradoError(
            "Tesseract OCR não encontrado. "
            "Instale em: https://github.com/UB-Mannheim/tesseract/wiki"
        )

    def ler_arquivo(
        self, arquivo: Path | str, pagina: Optional[int] = None
    ) -> Comprovante | List[Comprovante]:
        """
        Lê um arquivo de comprovante (PDF ou imagem).

        Args:
            arquivo: Caminho para arquivo PDF ou imagem
            pagina: Número da página (apenas para PDF, 1-indexed)
                   Se None, lê todas as páginas

        Returns:
            Se pagina especificada: um Comprovante
            Se pagina=None: lista de Comprovantes (um por página)

        Raises:
            LeitorOCRError: Se erro ao ler arquivo

        Examples:
            >>> leitor = LeitorOCR()
            >>>
            >>> # Imagem única
            >>> comp = leitor.ler_arquivo('comprovante.jpg')
            >>>
            >>> # PDF com uma página
            >>> comp = leitor.ler_arquivo('comprovante.pdf', pagina=1)
            >>>
            >>> # PDF com múltiplas páginas
            >>> comps = leitor.ler_arquivo('comprovantes.pdf')
            >>> print(f"{len(comps)} comprovantes extraídos")
        """
        arquivo = Path(arquivo)

        # Validar arquivo
        if not arquivo.exists():
            raise LeitorOCRError(f"Arquivo não encontrado: {arquivo}")

        extensao = arquivo.suffix.lower()

        # PDF: converter para imagens
        if extensao == ".pdf":
            return self._ler_pdf(arquivo, pagina)

        # Imagem: processar diretamente
        elif extensao in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            return self._ler_imagem(arquivo)

        else:
            raise LeitorOCRError(
                f"Formato não suportado: {extensao}. " f"Use: pdf, png, jpg, bmp, tiff"
            )

    def _ler_pdf(
        self, arquivo: Path, pagina: Optional[int] = None
    ) -> Comprovante | List[Comprovante]:
        """
        Lê comprovante(s) de um PDF.

        Args:
            arquivo: Caminho para PDF
            pagina: Número da página (1-indexed) ou None para todas

        Returns:
            Comprovante único ou lista de Comprovantes
        """
        try:
            # Converter PDF para imagens
            if pagina:
                imagens = convert_from_path(
                    arquivo, first_page=pagina, last_page=pagina, dpi=200
                )
            else:
                imagens = convert_from_path(arquivo, dpi=200)

            logger.info(f"PDF convertido: {len(imagens)} página(s)")

        except Exception as e:
            raise ExtracaoOCRError(f"Erro ao converter PDF: {e}") from e

        # Processar cada página
        comprovantes = []
        for idx, imagem in enumerate(imagens, start=1):
            logger.info(f"Processando página {idx}/{len(imagens)}")
            comprovante = self._extrair_de_imagem(imagem, arquivo)
            comprovantes.append(comprovante)

        # Retornar único ou lista
        if pagina:
            return comprovantes[0]
        return comprovantes

    def _ler_imagem(self, arquivo: Path) -> Comprovante:
        """
        Lê comprovante de uma imagem.

        Args:
            arquivo: Caminho para imagem

        Returns:
            Comprovante extraído
        """
        try:
            imagem = Image.open(arquivo)
        except Exception as e:
            raise LeitorOCRError(f"Erro ao abrir imagem: {e}") from e

        return self._extrair_de_imagem(imagem, arquivo)

    def _extrair_de_imagem(self, imagem: Image.Image, arquivo: Path) -> Comprovante:
        """
        Extrai dados de uma imagem PIL usando OCR.

        Args:
            imagem: Imagem PIL
            arquivo: Arquivo original (para referência)

        Returns:
            Comprovante com dados extraídos
        """
        # Preprocessar se configurado
        if self.preprocessador:
            # Salvar em memória temporária
            imagem_processada = self.preprocessador.processar(arquivo)
        else:
            imagem_processada = imagem

        # Extrair texto e dados
        texto, confianca = self._extrair_texto(imagem_processada)

        # Extrair informações estruturadas
        valor = self._extrair_valor(texto)
        data_pagamento = self._extrair_data(texto)
        beneficiario = self._extrair_beneficiario(texto)

        # Criar comprovante
        comprovante = Comprovante(
            arquivo=str(arquivo),
            valor=valor if valor else Decimal("0.00"),
            data_pagamento=data_pagamento,
            beneficiario=beneficiario or "Não identificado",
            confianca_ocr=confianca,
        )

        logger.info(
            f"Comprovante extraído: valor=R${valor}, " f"confiança={confianca:.0%}"
        )

        return comprovante

    def _extrair_texto(self, imagem: Image.Image) -> Tuple[str, float]:
        """
        Extrai texto da imagem usando Tesseract.

        Args:
            imagem: Imagem PIL

        Returns:
            Tuple (texto, confianca)

        Raises:
            ExtracaoOCRError: Se erro durante OCR
        """
        try:
            # Extrair texto com dados de confiança
            dados = pytesseract.image_to_data(
                imagem, lang=self.idioma, output_type=pytesseract.Output.DICT
            )

            # Calcular confiança média
            confidencias = [int(c) for c in dados["conf"] if c != "-1"]

            if confidencias:
                confianca = sum(confidencias) / len(confidencias) / 100.0
            else:
                confianca = 0.0

            # Extrair texto completo
            texto = pytesseract.image_to_string(imagem, lang=self.idioma)

            logger.debug(
                f"Texto extraído: {len(texto)} caracteres, confiança={confianca:.0%}"
            )

            return texto, confianca

        except Exception as e:
            raise ExtracaoOCRError(f"Erro durante OCR: {e}") from e

    def _extrair_valor(self, texto: str) -> Optional[Decimal]:
        """
        Extrai valor monetário do texto.

        Procura por padrões como: R$ 1.234,56 ou R$1234,56

        Args:
            texto: Texto extraído do OCR

        Returns:
            Valor como Decimal ou None se não encontrado
        """
        matches = self.REGEX_VALOR.findall(texto)

        if not matches:
            logger.warning("Nenhum valor monetário encontrado no texto")
            return None

        # Pegar o primeiro valor encontrado
        valor_str = matches[0]

        try:
            valor = normalizar_valor(valor_str)
            logger.debug(f"Valor extraído: R$ {valor}")
            return valor
        except Exception as e:
            logger.error(f"Erro ao normalizar valor '{valor_str}': {e}")
            return None

    def _extrair_data(self, texto: str) -> Optional[date]:
        """
        Extrai data do texto.

        Procura por padrões como: 01/11/2025 ou 01-11-2025

        Args:
            texto: Texto extraído do OCR

        Returns:
            Data como date ou None se não encontrado
        """
        matches = self.REGEX_DATA.findall(texto)

        if not matches:
            logger.warning("Nenhuma data encontrada no texto")
            return None

        # Pegar a primeira data encontrada
        data_str = matches[0]

        try:
            data = normalizar_data(data_str)
            logger.debug(f"Data extraída: {data}")
            return data
        except Exception as e:
            logger.error(f"Erro ao normalizar data '{data_str}': {e}")
            return None

    def _extrair_beneficiario(self, texto: str) -> Optional[str]:
        """
        Tenta extrair nome do beneficiário do texto.

        Procura por padrões comuns em comprovantes:
        - "Para: Nome"
        - "Beneficiário: Nome"
        - "Favorecido: Nome"

        Args:
            texto: Texto extraído do OCR

        Returns:
            Nome do beneficiário ou None
        """
        # Padrões comuns
        padroes = [
            r"(?:Para|Beneficiário|Favorecido|Destino):\s*([A-ZÀÁÃÂÇ][A-Za-zÀ-ÿ\s]+)",
            r"(?:Para|Beneficiário|Favorecido)\s+([A-ZÀÁÃÂÇ][A-Za-zÀ-ÿ\s]+)",
        ]

        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                beneficiario = match.group(1).strip()
                logger.debug(f"Beneficiário extraído: {beneficiario}")
                return beneficiario

        logger.warning("Beneficiário não identificado no texto")
        return None

    def obter_info_ocr(self) -> Dict[str, Any]:
        """
        Retorna informações sobre a configuração do OCR.

        Returns:
            Dicionário com informações do Tesseract e configurações

        Examples:
            >>> leitor = LeitorOCR()
            >>> info = leitor.obter_info_ocr()
            >>> print(f"Versão Tesseract: {info['versao_tesseract']}")
        """
        try:
            versao = pytesseract.get_tesseract_version()
        except Exception:
            versao = "Desconhecida"

        return {
            "versao_tesseract": str(versao),
            "idioma": self.idioma,
            "confianca_minima": self.confianca_minima,
            "preprocessar": self.preprocessar,
            "tesseract_cmd": pytesseract.pytesseract.tesseract_cmd,
        }
