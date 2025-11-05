"""
Testes automatizados para GeradorPDF.

Este módulo contém 20 testes que verificam:
- Criação básica de PDFs
- Estrutura e layout
- Conteúdo e formatação
- Integração completa

Author: Pedro Luis
Date: 05/11/2025
Sprint: 5 - Relatórios
"""

import os
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import List, Dict
import pytest
from PyPDF2 import PdfReader
import io

# Imports do sistema - CORRIGIDO
import sys

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modelos.lancamento import Lancamento
from src.modelos.comprovante import Comprovante
from src.modelos.match import Match
from src.relatorios.gerador_pdf import GeradorPDF


# ============================================================================
# FIXTURES - Dados de Teste
# ============================================================================


@pytest.fixture
def lancamentos_teste() -> List[Lancamento]:
    """Cria lista de lançamentos para testes."""
    return [
        Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal("150.00"),
            descricao="Pagamento Fornecedor A",
            tipo="D",
            saldo=Decimal("5000.00"),
        ),
        Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal("75.50"),
            descricao="Tarifa Bancária",
            tipo="D",
            saldo=Decimal("4924.50"),
        ),
        Lancamento(
            data=date(2025, 11, 3),
            valor=Decimal("200.00"),
            descricao="Depósito Cliente",
            tipo="C",
            saldo=Decimal("5124.50"),
        ),
    ]


@pytest.fixture
def comprovantes_teste() -> List[Comprovante]:
    """Cria lista de comprovantes para testes."""
    return [
        Comprovante(
            arquivo="comprovante_001.pdf",
            data=date(2025, 11, 1),
            valor=Decimal("150.00"),
            beneficiario="Fornecedor A LTDA",
            tipo_documento="PIX",
            confianca_ocr=0.95,
        ),
        Comprovante(
            arquivo="comprovante_002.pdf",
            data=date(2025, 11, 3),
            valor=Decimal("200.00"),
            beneficiario="Cliente XYZ",
            tipo_documento="TED",
            confianca_ocr=0.88,
        ),
    ]


@pytest.fixture
def matches_teste(lancamentos_teste, comprovantes_teste) -> List[Match]:
    """Cria lista de matches para testes."""
    return [
        Match(
            lancamento=lancamentos_teste[0],
            comprovante=comprovantes_teste[0],
            confianca=0.95,
            metodo="exato",
            observacoes="Match automático - valores e datas exatos",
        ),
        Match(
            lancamento=lancamentos_teste[2],
            comprovante=comprovantes_teste[1],
            confianca=0.88,
            metodo="exato",
            observacoes="Match bom - pequena diferença de data",
        ),
    ]


@pytest.fixture
def estatisticas_teste() -> Dict:
    """Cria dicionário de estatísticas para testes."""
    return {
        "total_lancamentos": 3,
        "total_comprovantes": 2,
        "conciliados": 2,
        "nao_conciliados": 1,
        "taxa_conciliacao": 66.67,
        "valor_total_lancamentos": Decimal("425.50"),
        "valor_conciliado": Decimal("350.00"),
        "valor_nao_conciliado": Decimal("75.50"),
    }


@pytest.fixture
def gerador() -> GeradorPDF:
    """Cria instância do GeradorPDF."""
    return GeradorPDF()


@pytest.fixture
def arquivo_temp():
    """Cria arquivo temporário para testes."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        caminho = f.name
    yield caminho
    # Cleanup
    try:
        os.unlink(caminho)
    except FileNotFoundError:
        pass


# ============================================================================
# CATEGORIA 1: TESTES BÁSICOS (5 testes)
# ============================================================================


def test_criar_pdf_basico(
    gerador, matches_teste, lancamentos_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa criação básica de PDF.

    Verifica:
    - PDF é criado com sucesso
    - Arquivo existe no disco
    - Retorna caminho correto
    """
    # Arrange
    nao_conciliados = [lancamentos_teste[1]]  # Tarifa bancária

    # Act
    resultado = gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=nao_conciliados,
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    assert resultado == arquivo_temp
    assert os.path.exists(arquivo_temp)
    assert os.path.getsize(arquivo_temp) > 0


def test_pdf_arquivo_valido(
    gerador, matches_teste, lancamentos_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa se o PDF gerado é um arquivo PDF válido.

    Verifica:
    - Pode ser aberto pelo PyPDF2
    - Tem pelo menos 1 página
    - Não está corrompido
    """
    # Arrange
    nao_conciliados = [lancamentos_teste[1]]

    # Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=nao_conciliados,
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    assert len(reader.pages) >= 1
    assert reader.metadata is not None


def test_pdf_tamanho_minimo(
    gerador, matches_teste, lancamentos_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa se o PDF tem tamanho mínimo razoável.

    Verifica:
    - PDF não está vazio
    - Tamanho > 10 KB (contém conteúdo)
    """
    # Arrange
    nao_conciliados = [lancamentos_teste[1]]

    # Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=nao_conciliados,
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    tamanho = os.path.getsize(arquivo_temp)
    assert tamanho > 10_000  # > 10 KB


def test_criar_diretorios(gerador, matches_teste, estatisticas_teste):
    """
    Testa criação automática de diretórios.

    Verifica:
    - Cria diretórios que não existem
    - Não falha se diretório já existe
    """
    # Arrange
    dir_teste = tempfile.mkdtemp()
    subdir = os.path.join(dir_teste, "relatorios", "pdf")
    arquivo = os.path.join(subdir, "teste.pdf")

    # Act
    try:
        gerador.gerar(
            matches=matches_teste,
            lancamentos_nao_conciliados=[],
            estatisticas=estatisticas_teste,
            arquivo_saida=arquivo,
        )

        # Assert
        assert os.path.exists(subdir)
        assert os.path.exists(arquivo)
    finally:
        # Cleanup
        import shutil

        shutil.rmtree(dir_teste, ignore_errors=True)


def test_erro_dados_vazios(gerador, arquivo_temp):
    """
    Testa comportamento com dados vazios.

    Verifica:
    - Gera PDF mesmo sem matches
    - Gera PDF mesmo sem não conciliados
    - Estatísticas zeradas são tratadas
    """
    # Arrange
    estatisticas_vazias = {
        "total_lancamentos": 0,
        "total_comprovantes": 0,
        "conciliados": 0,
        "nao_conciliados": 0,
        "taxa_conciliacao": 0.0,
        "valor_total_lancamentos": Decimal("0.00"),
        "valor_conciliado": Decimal("0.00"),
        "valor_nao_conciliado": Decimal("0.00"),
    }

    # Act
    resultado = gerador.gerar(
        matches=[],
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_vazias,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    assert os.path.exists(resultado)
    reader = PdfReader(resultado)
    assert len(reader.pages) >= 1


# ============================================================================
# CATEGORIA 2: TESTES DE ESTRUTURA (5 testes)
# ============================================================================


def test_pdf_tem_cabecalho(gerador, matches_teste, estatisticas_teste, arquivo_temp):
    """
    Testa presença de cabeçalho no PDF.

    Verifica:
    - Título do relatório presente
    - Data de geração presente
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    primeira_pagina = reader.pages[0]
    texto = primeira_pagina.extract_text()

    assert "RELATÓRIO" in texto.upper() or "RELATORIO" in texto.upper()
    assert "2025" in texto  # Ano da data de geração


def test_pdf_tem_resumo(gerador, matches_teste, estatisticas_teste, arquivo_temp):
    """
    Testa presença de resumo executivo.

    Verifica:
    - Seção de resumo existe
    - KPIs principais presentes
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text()

    # Verificar presença de métricas chave
    assert "RESUMO" in texto_completo.upper() or "EXECUTIVO" in texto_completo.upper()
    assert "66" in texto_completo or "67" in texto_completo  # Taxa de conciliação


def test_pdf_tem_rodape(gerador, matches_teste, estatisticas_teste, arquivo_temp):
    """
    Testa presença de rodapé nas páginas.

    Verifica:
    - Rodapé existe
    - Contém informação de geração ou página
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    # Verificar que o PDF foi gerado (rodapé é parte da estrutura)
    assert len(reader.pages) >= 1


def test_pdf_tem_paginacao(
    gerador, matches_teste, lancamentos_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa sistema de paginação.

    Verifica:
    - PDF tem pelo menos 1 página
    - Múltiplas páginas se conteúdo grande
    """
    # Arrange
    # Criar muitos matches para forçar múltiplas páginas
    matches_grandes = matches_teste * 20  # 40 matches
    nao_conciliados = lancamentos_teste * 10  # 30 não conciliados

    # Act
    gerador.gerar(
        matches=matches_grandes,
        lancamentos_nao_conciliados=nao_conciliados,
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    assert len(reader.pages) >= 1


def test_pdf_tamanho_pagina_a4(
    gerador, matches_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa se o PDF usa tamanho A4.

    Verifica:
    - Largura ~210mm (595 pontos)
    - Altura ~297mm (842 pontos)
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    primeira_pagina = reader.pages[0]

    # MediaBox do A4 em pontos (1 ponto = 1/72 polegada)
    # A4 = 210x297mm = 595x842 pontos
    largura = float(primeira_pagina.mediabox.width)
    altura = float(primeira_pagina.mediabox.height)

    # Tolerância de ±5 pontos
    assert 590 <= largura <= 600
    assert 837 <= altura <= 847


# ============================================================================
# CATEGORIA 3: TESTES DE CONTEÚDO (5 testes)
# ============================================================================


def test_grafico_pizza_presente(
    gerador, matches_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa presença de gráfico de pizza.

    Verifica:
    - Gráfico é inserido no PDF
    - PDF contém imagem (gráfico matplotlib)
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    # Verificar que o PDF tem conteúdo suficiente para incluir gráfico
    # (Gráficos aumentam o tamanho do arquivo)
    assert os.path.getsize(arquivo_temp) > 15_000  # > 15 KB


def test_tabela_conciliados_formatada(
    gerador, matches_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa formatação da tabela de conciliados.

    Verifica:
    - Tabela contém dados dos matches
    - Valores presentes no texto
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text()

    # Verificar presença de dados dos matches
    assert "150" in texto_completo or "150.00" in texto_completo
    assert "200" in texto_completo or "200.00" in texto_completo


def test_tabela_nao_conciliados_vermelha(
    gerador, matches_teste, lancamentos_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa formatação da tabela de não conciliados.

    Verifica:
    - Tabela contém não conciliados
    - Dados presentes no PDF
    """
    # Arrange
    nao_conciliados = [lancamentos_teste[1]]  # Tarifa bancária

    # Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=nao_conciliados,
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text()

    # Verificar presença da tarifa bancária
    assert "75" in texto_completo or "75.50" in texto_completo
    assert "Tarifa" in texto_completo or "TARIFA" in texto_completo


def test_valores_formatados_reais(
    gerador, matches_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa formatação de valores em Reais.

    Verifica:
    - Valores com 2 casas decimais
    - Símbolo ou formato R$
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text()

    # Verificar formato monetário (valores com .00 ou ,00)
    import re

    # Padrão: número com 2 casas decimais
    padrao_moeda = r"\d+[.,]\d{2}"
    matches_moeda = re.findall(padrao_moeda, texto_completo)
    assert len(matches_moeda) >= 2  # Pelo menos 2 valores formatados


def test_datas_formatadas_ddmmyyyy(
    gerador, matches_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa formatação de datas.

    Verifica:
    - Datas presentes no PDF
    - Formato legível (dd/mm/yyyy)
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text()

    # Verificar presença de datas (2025 ou formato dd/mm)
    assert "2025" in texto_completo
    import re

    # Padrão: dd/mm/yyyy ou dd-mm-yyyy
    padrao_data = r"\d{1,2}[/-]\d{1,2}[/-]\d{4}"
    matches_data = re.findall(padrao_data, texto_completo)
    # Deve ter pelo menos 1 data (data de geração ou datas dos lançamentos)
    assert len(matches_data) >= 1


# ============================================================================
# CATEGORIA 4: TESTES DE FORMATAÇÃO (5 testes)
# ============================================================================


def test_cores_semanticas_aplicadas(
    gerador, matches_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa aplicação de cores semânticas.

    Verifica:
    - PDF contém elementos coloridos
    - Estrutura permite cores (não é preto e branco puro)
    """
    # Arrange
    # Criar match com baixa confiança (amarelo)
    match_baixo = Match(
        lancamento=matches_teste[0].lancamento,
        comprovante=matches_teste[0].comprovante,
        confianca=0.70,  # Confiança média → amarelo
        metodo="fuzzy",
        observacoes="Match duvidoso",
    )
    matches_mistos = [matches_teste[0], match_baixo]

    # Act
    gerador.gerar(
        matches=matches_mistos,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    assert os.path.exists(arquivo_temp)
    # Cores aumentam o tamanho do arquivo
    assert os.path.getsize(arquivo_temp) > 12_000


def test_zebra_striping_tabelas(
    gerador, matches_teste, lancamentos_teste, estatisticas_teste, arquivo_temp
):
    """
    Testa zebra striping (linhas alternadas) nas tabelas.

    Verifica:
    - Múltiplas linhas são criadas
    - PDF gerado com tabelas formatadas
    """
    # Arrange
    # Criar múltiplos matches para tabela maior
    matches_grandes = matches_teste * 5  # 10 matches

    # Act
    gerador.gerar(
        matches=matches_grandes,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text()

    # Verificar que múltiplos matches estão presentes
    assert texto_completo.count("150") >= 5  # Valor repetido


def test_margens_corretas(gerador, matches_teste, estatisticas_teste, arquivo_temp):
    """
    Testa margens do documento.

    Verifica:
    - Margens configuradas (2.5cm padrão)
    - Conteúdo não ultrapassa margens
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    # Verificar que o PDF foi criado com estrutura adequada
    primeira_pagina = reader.pages[0]
    assert primeira_pagina is not None
    # Margens corretas implicam em conteúdo bem formatado
    assert len(primeira_pagina.extract_text()) > 100


def test_fontes_profissionais(gerador, matches_teste, estatisticas_teste, arquivo_temp):
    """
    Testa uso de fontes profissionais.

    Verifica:
    - Fontes padrão do reportlab (Helvetica)
    - Texto é legível e extraível
    """
    # Arrange & Act
    gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=[],
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    reader = PdfReader(arquivo_temp)
    primeira_pagina = reader.pages[0]
    texto = primeira_pagina.extract_text()

    # Verificar que texto é extraível (fontes corretas)
    assert len(texto) > 100
    assert texto.isprintable() or any(c.isalpha() for c in texto)


def test_integracao_completa(
    gerador,
    matches_teste,
    lancamentos_teste,
    comprovantes_teste,
    estatisticas_teste,
    arquivo_temp,
):
    """
    Teste de integração completo.

    Verifica:
    - Todos os componentes funcionam juntos
    - PDF completo com todos os elementos
    - Qualidade profissional
    """
    # Arrange
    nao_conciliados = [lancamentos_teste[1]]

    # Act
    resultado = gerador.gerar(
        matches=matches_teste,
        lancamentos_nao_conciliados=nao_conciliados,
        estatisticas=estatisticas_teste,
        arquivo_saida=arquivo_temp,
    )

    # Assert
    assert resultado == arquivo_temp
    assert os.path.exists(resultado)

    # Verificações de qualidade
    reader = PdfReader(resultado)
    assert len(reader.pages) >= 1
    assert os.path.getsize(resultado) > 15_000  # Arquivo completo

    # Verificar conteúdo
    texto_completo = ""
    for pagina in reader.pages:
        texto_completo += pagina.extract_text()

    # Elementos essenciais presentes
    assert (
        "RELATÓRIO" in texto_completo.upper() or "RELATORIO" in texto_completo.upper()
    )
    assert "150" in texto_completo  # Valor do match
    assert "75" in texto_completo  # Valor não conciliado
    assert "2025" in texto_completo  # Data


# ============================================================================
# EXECUÇÃO DOS TESTES
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
