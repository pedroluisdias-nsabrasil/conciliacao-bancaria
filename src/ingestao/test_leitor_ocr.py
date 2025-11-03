"""
Testes para Preprocessador e LeitorOCR.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Date: 03/11/2025
Sprint: 2 - OCR
"""

import pytest
from pathlib import Path
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import tempfile

from src.ingestao.preprocessador import (
    Preprocessador,
    PreprocessadorError,
    ImagemInvalidaError,
    preprocessar_para_ocr
)
from src.ingestao.leitor_ocr import (
    LeitorOCR,
    LeitorOCRError,
    TesseractNaoEncontradoError,
    ExtracaoOCRError
)


# ============================================================================
# TESTES DO PREPROCESSADOR
# ============================================================================

class TestPreprocessadorInicializacao:
    """Testes de inicializaÃ§Ã£o do Preprocessador."""
    
    def test_criar_preprocessador_padrao(self):
        """Deve criar preprocessador com configuraÃ§Ãµes padrÃ£o."""
        prep = Preprocessador()
        
        assert prep.escala_cinza is True
        assert prep.binarizar is True
        assert prep.contraste == 1.5
        assert prep.remover_ruido is True
        assert prep.redimensionar is False
    
    def test_criar_preprocessador_personalizado(self):
        """Deve criar preprocessador com configuraÃ§Ãµes personalizadas."""
        prep = Preprocessador(
            escala_cinza=False,
            binarizar=False,
            contraste=2.5,
            remover_ruido=False,
            redimensionar=True,
            tamanho_alvo=(800, 1200)
        )
        
        assert prep.escala_cinza is False
        assert prep.binarizar is False
        assert prep.contraste == 2.5
        assert prep.remover_ruido is False
        assert prep.redimensionar is True
        assert prep.tamanho_alvo == (800, 1200)
    
    def test_contraste_invalido_muito_baixo(self):
        """Deve rejeitar contraste muito baixo."""
        with pytest.raises(ValueError, match="Contraste deve estar"):
            Preprocessador(contraste=0.05)
    
    def test_contraste_invalido_muito_alto(self):
        """Deve rejeitar contraste muito alto."""
        with pytest.raises(ValueError, match="Contraste deve estar"):
            Preprocessador(contraste=6.0)


class TestPreprocessadorProcessamento:
    """Testes de processamento de imagens."""
    
    @pytest.fixture
    def imagem_teste(self):
        """Cria uma imagem temporÃ¡ria para testes."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Criar imagem de teste
            img = Image.new('RGB', (100, 100), color='white')
            img.save(f.name)
            yield Path(f.name)
            # Cleanup
            Path(f.name).unlink(missing_ok=True)
    
    def test_processar_imagem_valida(self, imagem_teste):
        """Deve processar imagem vÃ¡lida com sucesso."""
        prep = Preprocessador()
        imagem = prep.processar(imagem_teste)
        
        assert isinstance(imagem, Image.Image)
        assert imagem.mode in ['L', '1']  # Escala de cinza ou binÃ¡rio
    
    def test_arquivo_nao_existe(self):
        """Deve lanÃ§ar erro se arquivo nÃ£o existe."""
        prep = Preprocessador()
        
        with pytest.raises(ImagemInvalidaError, match="nÃ£o encontrado"):
            prep.processar('arquivo_inexistente.jpg')
    
    def test_formato_nao_suportado(self, tmp_path):
        """Deve rejeitar formato nÃ£o suportado."""
        arquivo = tmp_path / "teste.txt"
        arquivo.write_text("teste")
        
        prep = Preprocessador()
        
        with pytest.raises(ImagemInvalidaError, match="Formato nÃ£o suportado"):
            prep.processar(arquivo)
    
    def test_processar_sem_binarizar(self, imagem_teste):
        """Deve processar sem binarizaÃ§Ã£o."""
        prep = Preprocessador(binarizar=False)
        imagem = prep.processar(imagem_teste)
        
        assert imagem.mode == 'L'  # Escala de cinza, nÃ£o binÃ¡rio
    
    def test_processar_sem_escala_cinza(self, imagem_teste):
        """Deve processar mantendo cores."""
        prep = Preprocessador(
            escala_cinza=False,
            binarizar=False
        )
        imagem = prep.processar(imagem_teste)
        
        assert imagem.mode == 'RGB'
    
    def test_processar_para_arquivo(self, imagem_teste, tmp_path):
        """Deve processar e salvar em arquivo."""
        saida = tmp_path / "processado.png"
        prep = Preprocessador()
        
        resultado = prep.processar_para_arquivo(
            imagem_teste,
            saida,
            formato='PNG'
        )
        
        assert resultado == saida
        assert saida.exists()
        assert saida.stat().st_size > 0


class TestPreprocessarParaOCR:
    """Testes da funÃ§Ã£o de conveniÃªncia."""
    
    @pytest.fixture
    def imagem_teste(self):
        """Cria uma imagem temporÃ¡ria para testes."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            img = Image.new('RGB', (200, 200), color='blue')
            img.save(f.name)
            yield Path(f.name)
            Path(f.name).unlink(missing_ok=True)
    
    def test_preprocessar_para_ocr(self, imagem_teste):
        """Deve preprocessar com configuraÃ§Ãµes otimizadas para OCR."""
        imagem = preprocessar_para_ocr(imagem_teste)
        
        assert isinstance(imagem, Image.Image)
        assert imagem.mode in ['L', '1']


# ============================================================================
# TESTES DO LEITOR OCR
# ============================================================================

class TestLeitorOCRInicializacao:
    """Testes de inicializaÃ§Ã£o do LeitorOCR."""
    
    @patch('leitor_ocr.pytesseract')
    def test_criar_leitor_padrao(self, mock_tess):
        """Deve criar leitor com configuraÃ§Ãµes padrÃ£o."""
        mock_tess.pytesseract.tesseract_cmd = None
        mock_tess.get_tesseract_version.return_value = "5.0"
        
        leitor = LeitorOCR()
        
        assert leitor.confianca_minima == 0.6
        assert leitor.preprocessar is True
        assert leitor.idioma == 'por'
        assert leitor.preprocessador is not None
    
    @patch('leitor_ocr.pytesseract')
    def test_criar_leitor_personalizado(self, mock_tess):
        """Deve criar leitor com configuraÃ§Ãµes personalizadas."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        
        leitor = LeitorOCR(
            confianca_minima=0.8,
            preprocessar=False,
            idioma='eng'
        )
        
        assert leitor.confianca_minima == 0.8
        assert leitor.preprocessar is False
        assert leitor.idioma == 'eng'
        assert leitor.preprocessador is None
    
    def test_confianca_invalida_negativa(self):
        """Deve rejeitar confianÃ§a negativa."""
        with pytest.raises(ValueError, match="deve estar entre 0 e 1"):
            LeitorOCR(confianca_minima=-0.1)
    
    def test_confianca_invalida_maior_que_1(self):
        """Deve rejeitar confianÃ§a maior que 1."""
        with pytest.raises(ValueError, match="deve estar entre 0 e 1"):
            LeitorOCR(confianca_minima=1.5)


class TestLeitorOCRExtracaoValor:
    """Testes de extraÃ§Ã£o de valores monetÃ¡rios."""
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_valor_simples(self, mock_tess):
        """Deve extrair valor simples."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Valor pago: R$ 150,50"
        valor = leitor._extrair_valor(texto)
        
        assert valor == Decimal('150.50')
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_valor_com_milhares(self, mock_tess):
        """Deve extrair valor com separador de milhares."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Total: R$ 1.234,56"
        valor = leitor._extrair_valor(texto)
        
        assert valor == Decimal('1234.56')
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_valor_sem_espaco(self, mock_tess):
        """Deve extrair valor sem espaÃ§o."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Pagamento R$99,90 realizado"
        valor = leitor._extrair_valor(texto)
        
        assert valor == Decimal('99.90')
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_valor_nao_encontrado(self, mock_tess):
        """Deve retornar None se valor nÃ£o encontrado."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Texto sem valor monetÃ¡rio"
        valor = leitor._extrair_valor(texto)
        
        assert valor is None


class TestLeitorOCRExtracaoData:
    """Testes de extraÃ§Ã£o de datas."""
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_data_formato_barra(self, mock_tess):
        """Deve extrair data no formato dd/mm/yyyy."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Data: 15/11/2025"
        data_extraida = leitor._extrair_data(texto)
        
        assert data_extraida == date(2025, 11, 15)
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_data_formato_traco(self, mock_tess):
        """Deve extrair data no formato dd-mm-yyyy."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Realizado em 20-12-2025"
        data_extraida = leitor._extrair_data(texto)
        
        assert data_extraida == date(2025, 12, 20)
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_data_nao_encontrada(self, mock_tess):
        """Deve retornar None se data nÃ£o encontrada."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Texto sem data"
        data_extraida = leitor._extrair_data(texto)
        
        assert data_extraida is None


class TestLeitorOCRExtracaoBeneficiario:
    """Testes de extraÃ§Ã£o de beneficiÃ¡rio."""
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_beneficiario_com_para(self, mock_tess):
        """Deve extrair beneficiÃ¡rio com 'Para:'."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Para: JoÃ£o Silva Santos"
        beneficiario = leitor._extrair_beneficiario(texto)
        
        assert beneficiario == "JoÃ£o Silva Santos"
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_beneficiario_com_favorecido(self, mock_tess):
        """Deve extrair beneficiÃ¡rio com 'Favorecido:'."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Favorecido: Maria Oliveira"
        beneficiario = leitor._extrair_beneficiario(texto)
        
        assert beneficiario == "Maria Oliveira"
    
    @patch('leitor_ocr.pytesseract')
    def test_extrair_beneficiario_nao_encontrado(self, mock_tess):
        """Deve retornar None se beneficiÃ¡rio nÃ£o encontrado."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        texto = "Texto sem beneficiÃ¡rio identificÃ¡vel"
        beneficiario = leitor._extrair_beneficiario(texto)
        
        assert beneficiario is None


class TestLeitorOCRInfo:
    """Testes de informaÃ§Ãµes do OCR."""
    
    @patch('leitor_ocr.pytesseract')
    def test_obter_info_ocr(self, mock_tess):
        """Deve retornar informaÃ§Ãµes do OCR."""
        mock_tess.get_tesseract_version.return_value = "5.3.0"
        mock_tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        leitor = LeitorOCR(confianca_minima=0.7, idioma='por')
        info = leitor.obter_info_ocr()
        
        assert 'versao_tesseract' in info
        assert info['idioma'] == 'por'
        assert info['confianca_minima'] == 0.7
        assert info['preprocessar'] is True


class TestIntegracaoLeitorOCR:
    """Testes de integraÃ§Ã£o do pipeline completo."""
    
    @pytest.fixture
    def imagem_mock(self):
        """Cria imagem mock para testes."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(f.name)
            yield Path(f.name)
            Path(f.name).unlink(missing_ok=True)
    
    @patch('leitor_ocr.pytesseract')
    def test_ler_imagem_completo(self, mock_tess, imagem_mock):
        """Deve processar imagem completa gerando Comprovante."""
        # Configurar mock
        mock_tess.get_tesseract_version.return_value = "5.0"
        mock_tess.image_to_data.return_value = {
            'conf': ['90', '85', '88', '92']
        }
        mock_tess.image_to_string.return_value = (
            "Comprovante de Pagamento\n"
            "Para: JoÃ£o Silva\n"
            "Valor: R$ 250,00\n"
            "Data: 03/11/2025"
        )
        
        leitor = LeitorOCR(preprocessar=False)
        comprovante = leitor.ler_arquivo(imagem_mock)
        
        assert comprovante.valor == Decimal('250.00')
        assert comprovante.data_pagamento == date(2025, 11, 3)
        assert comprovante.beneficiario == "JoÃ£o Silva"
        assert 0.85 <= comprovante.confianca_ocr <= 0.92
    
    @patch('leitor_ocr.pytesseract')
    def test_arquivo_nao_existe(self, mock_tess):
        """Deve lanÃ§ar erro se arquivo nÃ£o existe."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        leitor = LeitorOCR()
        
        with pytest.raises(LeitorOCRError, match="nÃ£o encontrado"):
            leitor.ler_arquivo('arquivo_inexistente.jpg')
    
    @patch('leitor_ocr.pytesseract')
    def test_formato_nao_suportado(self, mock_tess, tmp_path):
        """Deve rejeitar formato nÃ£o suportado."""
        mock_tess.get_tesseract_version.return_value = "5.0"
        arquivo = tmp_path / "teste.txt"
        arquivo.write_text("teste")
        
        leitor = LeitorOCR()
        
        with pytest.raises(LeitorOCRError, match="Formato nÃ£o suportado"):
            leitor.ler_arquivo(arquivo)

