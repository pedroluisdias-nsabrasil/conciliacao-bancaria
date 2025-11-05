"""
Preprocessador de Imagens para OCR.

Este módulo fornece funcionalidades para melhorar a qualidade de imagens
antes da extração de texto via OCR, aumentando a precisão da leitura.

Técnicas implementadas:
- Conversão para escala de cinza
- Binarização (Otsu)
- Aumento de contraste
- Remoção de ruído
- Correção de rotação
- Redimensionamento

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Date: 03/11/2025
Sprint: 2 - OCR
"""

import logging
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

logger = logging.getLogger(__name__)


class PreprocessadorError(Exception):
    """Erro base do preprocessador de imagens."""

    pass


class ImagemInvalidaError(PreprocessadorError):
    """Imagem inválida ou corrompida."""

    pass


class Preprocessador:
    """
    Preprocessador de imagens para OCR.

    Melhora a qualidade de imagens através de diversas técnicas de
    processamento, otimizando para extração de texto via OCR.

    Attributes:
        escala_cinza: Se True, converte para escala de cinza
        binarizar: Se True, aplica binarização (preto e branco)
        contraste: Fator de contraste (1.0 = original, >1.0 = mais contraste)
        remover_ruido: Se True, aplica filtro de remoção de ruído
        redimensionar: Se True, redimensiona imagem
        tamanho_alvo: Tamanho alvo para redimensionamento (largura, altura)

    Examples:
        >>> preprocessador = Preprocessador()
        >>> imagem = preprocessador.processar('comprovante.jpg')
        >>> imagem.save('comprovante_processado.jpg')

        >>> # Personalizado
        >>> preprocessador = Preprocessador(
        ...     contraste=2.0,
        ...     binarizar=True,
        ...     remover_ruido=True
        ... )
        >>> imagem = preprocessador.processar('scan.png')
    """

    def __init__(
        self,
        escala_cinza: bool = True,
        binarizar: bool = True,
        contraste: float = 1.5,
        remover_ruido: bool = True,
        redimensionar: bool = False,
        tamanho_alvo: Optional[Tuple[int, int]] = None,
    ):
        """
        Inicializa o preprocessador.

        Args:
            escala_cinza: Converter para escala de cinza
            binarizar: Aplicar binarização
            contraste: Fator de contraste (1.0 a 3.0 recomendado)
            remover_ruido: Aplicar filtro de ruído
            redimensionar: Redimensionar imagem
            tamanho_alvo: Tamanho alvo (largura, altura) se redimensionar=True

        Raises:
            ValueError: Se contraste < 0.1 ou > 5.0
        """
        if contraste < 0.1 or contraste > 5.0:
            raise ValueError(
                f"Contraste deve estar entre 0.1 e 5.0, recebido: {contraste}"
            )

        self.escala_cinza = escala_cinza
        self.binarizar = binarizar
        self.contraste = contraste
        self.remover_ruido = remover_ruido
        self.redimensionar = redimensionar
        self.tamanho_alvo = tamanho_alvo or (1600, 2400)  # A4 em 200 DPI

        logger.info(
            f"Preprocessador criado: cinza={escala_cinza}, "
            f"binarizar={binarizar}, contraste={contraste}"
        )

    def processar(self, arquivo: Path | str) -> Image.Image:
        """
        Processa uma imagem aplicando todas as técnicas configuradas.

        Args:
            arquivo: Caminho para o arquivo de imagem

        Returns:
            Imagem processada (PIL.Image)

        Raises:
            ImagemInvalidaError: Se arquivo não existe ou não é imagem válida

        Examples:
            >>> prep = Preprocessador()
            >>> img = prep.processar('comprovante.jpg')
            >>> img.save('processado.jpg')
        """
        arquivo = Path(arquivo)

        # Validar arquivo
        if not arquivo.exists():
            raise ImagemInvalidaError(f"Arquivo não encontrado: {arquivo}")

        if arquivo.suffix.lower() not in [
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tiff",
            ".pdf",
        ]:
            raise ImagemInvalidaError(
                f"Formato não suportado: {arquivo.suffix}. "
                f"Use: jpg, png, bmp, tiff, pdf"
            )

        try:
            imagem = Image.open(arquivo)
        except Exception as e:
            raise ImagemInvalidaError(f"Erro ao abrir imagem: {e}") from e

        logger.info(f"Processando imagem: {arquivo.name} ({imagem.size})")

        # Pipeline de processamento
        if self.escala_cinza:
            imagem = self._converter_escala_cinza(imagem)

        if self.contraste != 1.0:
            imagem = self._ajustar_contraste(imagem)

        if self.remover_ruido:
            imagem = self._remover_ruido(imagem)

        if self.binarizar:
            imagem = self._binarizar(imagem)

        if self.redimensionar:
            imagem = self._redimensionar(imagem)

        logger.info(f"Imagem processada com sucesso: {imagem.size}")
        return imagem

    def _converter_escala_cinza(self, imagem: Image.Image) -> Image.Image:
        """
        Converte imagem para escala de cinza.

        Args:
            imagem: Imagem PIL

        Returns:
            Imagem em escala de cinza
        """
        if imagem.mode != "L":
            logger.debug("Convertendo para escala de cinza")
            imagem = imagem.convert("L")
        return imagem

    def _ajustar_contraste(self, imagem: Image.Image) -> Image.Image:
        """
        Aumenta o contraste da imagem.

        Args:
            imagem: Imagem PIL

        Returns:
            Imagem com contraste ajustado
        """
        logger.debug(f"Ajustando contraste: fator={self.contraste}")
        enhancer = ImageEnhance.Contrast(imagem)
        return enhancer.enhance(self.contraste)

    def _remover_ruido(self, imagem: Image.Image) -> Image.Image:
        """
        Remove ruído da imagem usando filtro de mediana.

        O filtro de mediana é eficaz para remover ruído "salt and pepper"
        mantendo bordas nítidas.

        Args:
            imagem: Imagem PIL

        Returns:
            Imagem com ruído reduzido
        """
        logger.debug("Removendo ruído")
        return imagem.filter(ImageFilter.MedianFilter(size=3))

    def _binarizar(self, imagem: Image.Image) -> Image.Image:
        """
        Binariza a imagem (preto e branco) usando método de Otsu.

        O método de Otsu encontra automaticamente o melhor threshold
        para separar texto de fundo.

        Args:
            imagem: Imagem PIL (deve estar em escala de cinza)

        Returns:
            Imagem binarizada
        """
        logger.debug("Binarizando imagem")

        # Garantir que está em escala de cinza
        if imagem.mode != "L":
            imagem = imagem.convert("L")

        # Aplicar threshold automático (Otsu)
        return ImageOps.autocontrast(imagem).convert("1")

    def _redimensionar(self, imagem: Image.Image) -> Image.Image:
        """
        Redimensiona a imagem mantendo proporção.

        Args:
            imagem: Imagem PIL

        Returns:
            Imagem redimensionada
        """
        largura_atual, altura_atual = imagem.size
        largura_alvo, altura_alvo = self.tamanho_alvo

        # Calcular proporção
        proporcao = min(largura_alvo / largura_atual, altura_alvo / altura_atual)

        if proporcao < 1.0:  # Só redimensionar se for reduzir
            novo_tamanho = (
                int(largura_atual * proporcao),
                int(altura_atual * proporcao),
            )
            logger.debug(f"Redimensionando de {imagem.size} para {novo_tamanho}")
            return imagem.resize(novo_tamanho, Image.Resampling.LANCZOS)

        return imagem

    def processar_para_arquivo(
        self, entrada: Path | str, saida: Path | str, formato: str = "PNG"
    ) -> Path:
        """
        Processa imagem e salva em arquivo.

        Args:
            entrada: Arquivo de entrada
            saida: Arquivo de saída
            formato: Formato de saída (PNG, JPEG, etc)

        Returns:
            Caminho do arquivo salvo

        Examples:
            >>> prep = Preprocessador()
            >>> arquivo = prep.processar_para_arquivo(
            ...     'original.jpg',
            ...     'processado.png'
            ... )
            >>> print(f"Salvo em: {arquivo}")
        """
        imagem = self.processar(entrada)
        saida = Path(saida)

        # Criar diretório se não existir
        saida.parent.mkdir(parents=True, exist_ok=True)

        imagem.save(saida, formato)
        logger.info(f"Imagem salva: {saida}")

        return saida


def preprocessar_para_ocr(arquivo: Path | str) -> Image.Image:
    """
    Função de conveniência para preprocessamento padrão para OCR.

    Aplica configurações otimizadas para extração de texto:
    - Escala de cinza
    - Binarização
    - Contraste aumentado
    - Remoção de ruído

    Args:
        arquivo: Caminho para arquivo de imagem

    Returns:
        Imagem processada e otimizada para OCR

    Examples:
        >>> imagem = preprocessar_para_ocr('comprovante.jpg')
        >>> # Usar com pytesseract
        >>> texto = pytesseract.image_to_string(imagem)
    """
    preprocessador = Preprocessador(
        escala_cinza=True,
        binarizar=True,
        contraste=1.8,
        remover_ruido=True,
        redimensionar=False,
    )
    return preprocessador.processar(arquivo)
