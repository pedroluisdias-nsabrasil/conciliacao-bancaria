"""Leitor OCR para extração de dados de comprovantes."""

import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date

import pytesseract
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path

from src.modelos.comprovante import Comprovante

# Configurar Tesseract ANTES de qualquer uso
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

logger = logging.getLogger(__name__)


class LeitorOCR:
    """Leitor de comprovantes usando OCR (Tesseract)."""
    
    def __init__(self, confianca_minima: float = 0.6, idioma: str = 'por', preprocessar: bool = True):
        """Inicializa o leitor OCR."""
        self.confianca_minima = confianca_minima
        self.idioma = idioma
        self.preprocessar = preprocessar
        self._padroes = self._criar_padroes()
        logger.info("✓ LeitorOCR inicializado")
    
    def _criar_padroes(self) -> Dict[str, re.Pattern]:
        """Cria padrões regex para extração de dados."""
        return {
            'valor': re.compile(r'(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})(?!\d)', re.IGNORECASE),
            'data': re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'),
            'beneficiario': re.compile(
                r'(?:para|favorecido|benefici[aá]rio|destinat[aá]rio|nome)[:\s]+([A-ZÀ-Ú][A-Za-zÀ-ú\s]+)',
                re.IGNORECASE
            ),
        }
    
    def ler_arquivo(self, caminho: str, pagina: int = 0) -> Optional[Comprovante]:
        """Lê arquivo e extrai dados via OCR."""
        arquivo = Path(caminho)
        
        if not arquivo.exists():
            logger.error(f"Arquivo não encontrado: {caminho}")
            return None
        
        extensao = arquivo.suffix.lower()
        
        try:
            if extensao == '.pdf':
                return self._ler_pdf(str(arquivo), pagina)
            elif extensao in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                return self._ler_imagem(str(arquivo))
            else:
                logger.error(f"Formato não suportado: {extensao}")
                return None
        except Exception as e:
            logger.error(f"Erro ao processar {arquivo.name}: {e}")
            return None
    
    def _ler_pdf(self, arquivo: str, pagina: int = 0) -> Optional[Comprovante]:
        """Processa arquivo PDF e extrai dados via OCR."""
        import tempfile
        import os
        
        try:
            imagens = convert_from_path(arquivo, first_page=pagina + 1, last_page=pagina + 1, dpi=300)
            
            if not imagens:
                logger.error(f"Não foi possível converter PDF: {arquivo}")
                return None
            
            imagem = imagens[0]
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                imagem.save(tmp.name, 'PNG')
                temp_path = tmp.name
            
            try:
                comprovante = self._processar_imagem(temp_path, arquivo)
                return comprovante
            finally:
                try:
                    os.unlink(temp_path)
                except:
                    pass
        except Exception as e:
            logger.error(f"Erro ao processar PDF {arquivo}: {e}")
            return None
    
    def _ler_imagem(self, arquivo: str) -> Optional[Comprovante]:
        """Processa arquivo de imagem via OCR."""
        try:
            return self._processar_imagem(arquivo, arquivo)
        except Exception as e:
            logger.error(f"Erro ao processar imagem {arquivo}: {e}")
            return None
    
    def _processar_imagem(self, caminho_imagem: str, arquivo_original: str) -> Optional[Comprovante]:
        """Processa imagem com OCR e extrai dados."""
        try:
            imagem = Image.open(caminho_imagem)
            
            if self.preprocessar:
                imagem = self._preprocessar_imagem(imagem)
            
            texto = pytesseract.image_to_string(imagem, lang=self.idioma, config='--psm 6')
            
            dados = self._extrair_dados(texto)
            confianca = self._calcular_confianca(dados)
            
            if confianca < self.confianca_minima:
                logger.warning(
                    f"Confiança {confianca:.1%} abaixo do mínimo "
                    f"{self.confianca_minima:.1%} para {Path(arquivo_original).name}"
                )
            
            if dados.get('valor') and dados.get('data'):
                comprovante = Comprovante(
                    arquivo=arquivo_original,
                    data=dados['data'],
                    valor=dados['valor'],
                    beneficiario=dados.get('beneficiario', ''),
                    confianca_ocr=confianca
                )
                
                logger.debug(
                    f"Extraído: R$ {comprovante.valor} em {comprovante.data} "
                    f"(confiança: {confianca:.0%})"
                )
                
                return comprovante
            else:
                logger.warning(f"Dados insuficientes de {Path(arquivo_original).name}")
                return None
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            return None
    
    def _preprocessar_imagem(self, imagem: Image.Image) -> Image.Image:
        """Preprocessa imagem para melhorar qualidade do OCR."""
        if imagem.mode != 'L':
            imagem = imagem.convert('L')
        
        enhancer = ImageEnhance.Contrast(imagem)
        imagem = enhancer.enhance(2.0)
        
        return imagem
    
    def _extrair_dados(self, texto: str) -> Dict[str, Any]:
        """Extrai dados estruturados do texto via regex."""
        dados = {}
        
        match_valor = self._padroes['valor'].search(texto)
        if match_valor:
            valor_str = match_valor.group(1).replace('.', '').replace(',', '.')
            try:
                dados['valor'] = Decimal(valor_str)
            except:
                pass
        
        match_data = self._padroes['data'].search(texto)
        if match_data:
            data_str = match_data.group(1)
            dados['data'] = self._parsear_data(data_str)
        
        match_beneficiario = self._padroes['beneficiario'].search(texto)
        if match_beneficiario:
            dados['beneficiario'] = match_beneficiario.group(1).strip()
        
        return dados
    
    def _parsear_data(self, data_str: str) -> Optional[date]:
        """Converte string de data para objeto date."""
        formatos = ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']
        
        for formato in formatos:
            try:
                dt = datetime.strptime(data_str, formato)
                return dt.date()
            except ValueError:
                continue
        
        logger.warning(f"Não foi possível parsear data: {data_str}")
        return None
    
    def _calcular_confianca(self, dados: Dict[str, Any]) -> float:
        """Calcula confiança da extração baseado nos dados encontrados."""
        score = 0.0
        
        if dados.get('valor'):
            score += 0.4
        if dados.get('data'):
            score += 0.3
        if dados.get('beneficiario'):
            score += 0.3
        
        return min(score, 1.0)
