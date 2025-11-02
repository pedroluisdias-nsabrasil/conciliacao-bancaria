"""
Testes para o módulo de leitura de PDF.

Testa:
- Leitura de PDFs com tabelas
- Leitura de PDFs com texto livre
- Tratamento de erros
- Extração de múltiplas páginas
"""

import pytest
from pathlib import Path
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.ingestao.leitor_pdf import (
    LeitorPDF,
    LeitorPDFError,
    PDFNaoSuportadoError,
    PDFSemConteudoError,
    PDFPLUMBER_DISPONIVEL,
)
from src.modelos import Lancamento


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_pagina_com_tabela():
    """Fixture que simula uma página PDF com tabela."""
    pagina = Mock()
    
    # Simular tabela de extrato
    pagina.extract_tables.return_value = [[
        ['Data', 'Descrição', 'Valor', 'Tipo'],  # Cabeçalho
        ['02/11/2025', 'PAGAMENTO FORNECEDOR', '150,50', 'D'],
        ['03/11/2025', 'PIX RECEBIDO', '500,00', 'C'],
        ['04/11/2025', 'TARIFA', '25,90', 'D'],
    ]]
    
    pagina.extract_text.return_value = ""
    
    return pagina


@pytest.fixture
def mock_pagina_com_texto():
    """Fixture que simula uma página PDF com texto livre."""
    pagina = Mock()
    
    pagina.extract_tables.return_value = []
    
    # Simular texto livre
    pagina.extract_text.return_value = """
    02/11/2025 PAGAMENTO FORNECEDOR 150,50 D
    03/11/2025 PIX RECEBIDO CLIENTE 500,00 C
    04/11/2025 TARIFA BANCARIA 25,90 D
    """
    
    return pagina


@pytest.fixture
def mock_pdf_com_multiplas_paginas(mock_pagina_com_tabela):
    """Fixture que simula um PDF com múltiplas páginas."""
    pdf = Mock()
    pdf.pages = [mock_pagina_com_tabela, mock_pagina_com_tabela]
    pdf.metadata = {'Author': 'Banco Teste'}
    pdf.__enter__ = Mock(return_value=pdf)
    pdf.__exit__ = Mock(return_value=False)
    return pdf


# ============================================================================
# TESTES DE INICIALIZAÇÃO
# ============================================================================

class TestLeitorPDFInicializacao:
    """Testes de inicialização do LeitorPDF."""
    
    @pytest.mark.skipif(
        not PDFPLUMBER_DISPONIVEL,
        reason="pdfplumber não está instalado"
    )
    def test_criar_leitor_padrao(self):
        """Testa criação do leitor com configurações padrão."""
        leitor = LeitorPDF()
        
        assert leitor.primeira_pagina == 1
        assert leitor.ultima_pagina is None
        assert 'data' in leitor.indices
        assert 'valor' in leitor.indices
    
    @pytest.mark.skipif(
        not PDFPLUMBER_DISPONIVEL,
        reason="pdfplumber não está instalado"
    )
    def test_criar_leitor_personalizado(self):
        """Testa criação com índices personalizados."""
        indices = {'data': 1, 'descricao': 2, 'valor': 0}
        leitor = LeitorPDF(indices_colunas=indices)
        
        assert leitor.indices['data'] == 1
        assert leitor.indices['valor'] == 0
    
    @pytest.mark.skipif(
        not PDFPLUMBER_DISPONIVEL,
        reason="pdfplumber não está instalado"
    )
    def test_criar_leitor_com_intervalo_paginas(self):
        """Testa criação com intervalo de páginas."""
        leitor = LeitorPDF(primeira_pagina=2, ultima_pagina=5)
        
        assert leitor.primeira_pagina == 2
        assert leitor.ultima_pagina == 5


# ============================================================================
# TESTES DE LEITURA DE TABELAS
# ============================================================================

@pytest.mark.skipif(
    not PDFPLUMBER_DISPONIVEL,
    reason="pdfplumber não está instalado"
)
class TestLeitorPDFTabelas:
    """Testes de leitura de PDFs com tabelas."""
    
    @patch('pdfplumber.open')
    def test_ler_pdf_com_tabela(self, mock_open, mock_pagina_com_tabela):
        """Testa leitura de PDF com tabela."""
        # Configurar mock
        mock_pdf = Mock()
        mock_pdf.pages = [mock_pagina_com_tabela]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        # Executar
        leitor = LeitorPDF()
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        # Verificar
        assert len(lancamentos) == 3  # Cabeçalho não é incluído
        
        primeiro = lancamentos[0]
        assert primeiro.data == date(2025, 11, 2)
        assert primeiro.valor == Decimal('150.50')
        assert primeiro.tipo == 'D'
    
    @patch('pdfplumber.open')
    def test_extrair_valores_corretos(self, mock_open, mock_pagina_com_tabela):
        """Testa se valores são extraídos corretamente."""
        mock_pdf = Mock()
        mock_pdf.pages = [mock_pagina_com_tabela]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        leitor = LeitorPDF()
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        valores = [l.valor for l in lancamentos]
        assert Decimal('150.50') in valores
        assert Decimal('500.00') in valores
        assert Decimal('25.90') in valores
    
    @patch('pdfplumber.open')
    def test_tipos_identificados_corretamente(self, mock_open, mock_pagina_com_tabela):
        """Testa se tipos são identificados corretamente."""
        mock_pdf = Mock()
        mock_pdf.pages = [mock_pagina_com_tabela]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        leitor = LeitorPDF()
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        tipos = [l.tipo for l in lancamentos]
        assert tipos.count('D') == 2
        assert tipos.count('C') == 1


# ============================================================================
# TESTES DE LEITURA DE TEXTO LIVRE
# ============================================================================

@pytest.mark.skipif(
    not PDFPLUMBER_DISPONIVEL,
    reason="pdfplumber não está instalado"
)
class TestLeitorPDFTexto:
    """Testes de leitura de PDFs com texto livre."""
    
    @patch('pdfplumber.open')
    def test_ler_pdf_com_texto(self, mock_open, mock_pagina_com_texto):
        """Testa leitura de PDF com texto livre."""
        mock_pdf = Mock()
        mock_pdf.pages = [mock_pagina_com_texto]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        leitor = LeitorPDF()
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        assert len(lancamentos) == 3
    
    @patch('pdfplumber.open')
    def test_texto_livre_valores_corretos(self, mock_open, mock_pagina_com_texto):
        """Testa valores de texto livre."""
        mock_pdf = Mock()
        mock_pdf.pages = [mock_pagina_com_texto]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        leitor = LeitorPDF()
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        primeiro = lancamentos[0]
        assert primeiro.valor == Decimal('150.50')
        assert primeiro.tipo == 'D'


# ============================================================================
# TESTES DE MÚLTIPLAS PÁGINAS
# ============================================================================

@pytest.mark.skipif(
    not PDFPLUMBER_DISPONIVEL,
    reason="pdfplumber não está instalado"
)
class TestLeitorPDFMultiplasPaginas:
    """Testes de leitura de PDFs com múltiplas páginas."""
    
    @patch('pdfplumber.open')
    def test_ler_multiplas_paginas(self, mock_open, mock_pdf_com_multiplas_paginas):
        """Testa leitura de múltiplas páginas."""
        mock_open.return_value = mock_pdf_com_multiplas_paginas
        
        leitor = LeitorPDF()
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        # Deve ler de ambas as páginas (3 lançamentos por página)
        assert len(lancamentos) == 6
    
    @patch('pdfplumber.open')
    def test_ler_intervalo_paginas(self, mock_open, mock_pdf_com_multiplas_paginas):
        """Testa leitura de intervalo de páginas."""
        mock_open.return_value = mock_pdf_com_multiplas_paginas
        
        # Ler apenas primeira página
        leitor = LeitorPDF(primeira_pagina=1, ultima_pagina=1)
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        assert len(lancamentos) == 3


# ============================================================================
# TESTES DE TRATAMENTO DE ERROS
# ============================================================================

@pytest.mark.skipif(
    not PDFPLUMBER_DISPONIVEL,
    reason="pdfplumber não está instalado"
)
class TestLeitorPDFErros:
    """Testes de tratamento de erros."""
    
    def test_arquivo_nao_existe(self):
        """Testa erro quando arquivo não existe."""
        leitor = LeitorPDF()
        
        with pytest.raises(PDFNaoSuportadoError, match="Arquivo não encontrado"):
            leitor.ler_arquivo('arquivo_inexistente.pdf')
    
    def test_nao_eh_pdf(self):
        """Testa erro com arquivo que não é PDF."""
        leitor = LeitorPDF()
        
        with pytest.raises(PDFNaoSuportadoError, match="Não é um arquivo PDF"):
            leitor.ler_arquivo('arquivo.txt')
    
    @patch('pdfplumber.open')
    def test_pdf_sem_conteudo(self, mock_open):
        """Testa erro quando PDF não tem conteúdo extraível."""
        # PDF vazio
        mock_pagina = Mock()
        mock_pagina.extract_tables.return_value = []
        mock_pagina.extract_text.return_value = ""
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_pagina]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        leitor = LeitorPDF()
        
        with pytest.raises(PDFSemConteudoError, match="Nenhum lançamento extraído"):
            leitor.ler_arquivo('fake.pdf')
    
    @patch('pdfplumber.open')
    def test_pagina_inicial_invalida(self, mock_open):
        """Testa erro com página inicial inválida."""
        mock_pdf = Mock()
        mock_pdf.pages = [Mock()]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        leitor = LeitorPDF(primeira_pagina=10)
        
        with pytest.raises(PDFNaoSuportadoError, match="Página inicial inválida"):
            leitor.ler_arquivo('fake.pdf')


# ============================================================================
# TESTES DE INFORMAÇÕES DO PDF
# ============================================================================

@pytest.mark.skipif(
    not PDFPLUMBER_DISPONIVEL,
    reason="pdfplumber não está instalado"
)
class TestLeitorPDFInfo:
    """Testes de obtenção de informações do PDF."""
    
    @patch('pdfplumber.open')
    def test_obter_info_pdf(self, mock_open, mock_pdf_com_multiplas_paginas):
        """Testa obtenção de informações do PDF."""
        mock_open.return_value = mock_pdf_com_multiplas_paginas
        
        leitor = LeitorPDF()
        info = leitor.obter_info_pdf('fake.pdf')
        
        assert 'total_paginas' in info
        assert info['total_paginas'] == 2
        assert 'metadata' in info


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

@pytest.mark.skipif(
    not PDFPLUMBER_DISPONIVEL,
    reason="pdfplumber não está instalado"
)
class TestIntegracaoLeitorPDF:
    """Testes de integração do leitor PDF."""
    
    @patch('pdfplumber.open')
    def test_pipeline_completo(self, mock_open, mock_pagina_com_tabela):
        """Testa pipeline completo de leitura."""
        mock_pdf = Mock()
        mock_pdf.pages = [mock_pagina_com_tabela]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)
        mock_open.return_value = mock_pdf
        
        # 1. Ler arquivo
        leitor = LeitorPDF()
        lancamentos = leitor.ler_arquivo('fake.pdf')
        
        # 2. Verificar que todos são válidos
        assert all(isinstance(l, Lancamento) for l in lancamentos)
        
        # 3. Verificar que não há conciliados
        assert all(not l.conciliado for l in lancamentos)
        
        # 4. Verificar que valores são positivos
        assert all(l.valor > 0 for l in lancamentos)
        
        # 5. Verificar que tipos são válidos
        assert all(l.tipo in ['D', 'C'] for l in lancamentos)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
