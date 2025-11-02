"""
Testes para o módulo de ingestão de CSV.

Testa:
- Funções de normalização (datas, valores, descrições)
- Leitor CSV básico
- Detecção de formato
- Tratamento de erros
"""

import pytest
from pathlib import Path
from datetime import date
from decimal import Decimal

from src.ingestao import (
    LeitorCSV,
    normalizar_data,
    normalizar_valor,
    limpar_descricao,
    identificar_tipo_lancamento,
)
from src.ingestao.leitor_csv import (
    ArquivoInvalidoError,
    FormatoNaoReconhecidoError,
)
from src.modelos import Lancamento


# ============================================================================
# TESTES DE NORMALIZAÇÃO
# ============================================================================

class TestNormalizadores:
    """Testes para funções de normalização."""
    
    def test_normalizar_data_formato_br(self):
        """Testa normalização de data no formato DD/MM/YYYY."""
        assert normalizar_data("02/11/2025") == date(2025, 11, 2)
        assert normalizar_data("31/12/2024") == date(2024, 12, 31)
        assert normalizar_data("01/01/2025") == date(2025, 1, 1)
    
    def test_normalizar_data_formato_br_hifen(self):
        """Testa normalização de data no formato DD-MM-YYYY."""
        assert normalizar_data("02-11-2025") == date(2025, 11, 2)
        assert normalizar_data("15-08-2024") == date(2024, 8, 15)
    
    def test_normalizar_data_formato_iso(self):
        """Testa normalização de data no formato YYYY-MM-DD."""
        assert normalizar_data("2025-11-02") == date(2025, 11, 2)
        assert normalizar_data("2024-12-31") == date(2024, 12, 31)
    
    def test_normalizar_data_ano_curto(self):
        """Testa normalização de data com ano de 2 dígitos."""
        assert normalizar_data("02/11/25") == date(2025, 11, 2)
        assert normalizar_data("31/12/24") == date(2024, 12, 31)
    
    def test_normalizar_data_invalida(self):
        """Testa erro com data inválida."""
        with pytest.raises(ValueError, match="Formato de data não reconhecido"):
            normalizar_data("32/13/2025")
        
        with pytest.raises(ValueError, match="Data inválida"):
            normalizar_data("")
        
        with pytest.raises(ValueError, match="Data inválida"):
            normalizar_data(None)
    
    def test_normalizar_valor_com_moeda(self):
        """Testa normalização de valor com símbolo R$."""
        assert normalizar_valor("R$ 1.234,56") == Decimal("1234.56")
        assert normalizar_valor("R$ 150,50") == Decimal("150.50")
        assert normalizar_valor("R$100,00") == Decimal("100.00")
    
    def test_normalizar_valor_sem_moeda(self):
        """Testa normalização de valor sem símbolo."""
        assert normalizar_valor("1.234,56") == Decimal("1234.56")
        assert normalizar_valor("150,50") == Decimal("150.50")
        assert normalizar_valor("100") == Decimal("100.00")
    
    def test_normalizar_valor_negativo(self):
        """Testa normalização de valor negativo (retorna positivo)."""
        assert normalizar_valor("-150,50") == Decimal("150.50")
        assert normalizar_valor("-1.234,56") == Decimal("1234.56")
    
    def test_normalizar_valor_contabil(self):
        """Testa normalização de valor em formato contábil (parênteses)."""
        assert normalizar_valor("(150,50)") == Decimal("150.50")
        assert normalizar_valor("(1.234,56)") == Decimal("1234.56")
    
    def test_normalizar_valor_invalido(self):
        """Testa erro com valor inválido."""
        with pytest.raises(ValueError, match="Valor inválido"):
            normalizar_valor("")
        
        with pytest.raises(ValueError, match="Valor inválido"):
            normalizar_valor(None)
        
        with pytest.raises(ValueError):
            normalizar_valor("abc")
    
    def test_limpar_descricao(self):
        """Testa limpeza de descrição."""
        assert limpar_descricao("  PAG  FORNECEDOR  ") == "PAG FORNECEDOR"
        assert limpar_descricao("TED\nPAGAMENTO") == "TED PAGAMENTO"
        assert limpar_descricao("  COMPRA   LOJA  \n  XYZ  ") == "COMPRA LOJA XYZ"
    
    def test_limpar_descricao_vazia(self):
        """Testa limpeza de descrição vazia."""
        assert limpar_descricao("") == ""
        assert limpar_descricao(None) == ""
    
    def test_identificar_tipo_debito(self):
        """Testa identificação de lançamento débito."""
        assert identificar_tipo_lancamento("PAGAMENTO FORNECEDOR", Decimal("100")) == "D"
        assert identificar_tipo_lancamento("TED ENVIADA", Decimal("100")) == "D"
        assert identificar_tipo_lancamento("COMPRA LOJA", Decimal("50")) == "D"
        assert identificar_tipo_lancamento("SAQUE", Decimal("200")) == "D"
    
    def test_identificar_tipo_credito(self):
        """Testa identificação de lançamento crédito."""
        assert identificar_tipo_lancamento("DEPOSITO", Decimal("100")) == "C"
        assert identificar_tipo_lancamento("PIX RECEBIDO", Decimal("100")) == "C"
        assert identificar_tipo_lancamento("CREDITO SALARIO", Decimal("1000")) == "C"
    
    def test_identificar_tipo_com_coluna(self):
        """Testa identificação quando coluna tipo é fornecida."""
        assert identificar_tipo_lancamento("QUALQUER", Decimal("100"), "D") == "D"
        assert identificar_tipo_lancamento("QUALQUER", Decimal("100"), "C") == "C"
        assert identificar_tipo_lancamento("QUALQUER", Decimal("100"), "DEBITO") == "D"
        assert identificar_tipo_lancamento("QUALQUER", Decimal("100"), "CREDITO") == "C"


# ============================================================================
# TESTES DO LEITOR CSV
# ============================================================================

class TestLeitorCSV:
    """Testes para o LeitorCSV."""
    
    @pytest.fixture
    def extrato_itau(self):
        """Fixture com caminho do extrato Itaú."""
        return "tests/fixtures/extratos_exemplo/extrato_itau.csv"
    
    @pytest.fixture
    def extrato_generico(self):
        """Fixture com caminho do extrato genérico."""
        return "tests/fixtures/extratos_exemplo/extrato_generico.csv"
    
    def test_criar_leitor(self):
        """Testa criação do leitor."""
        leitor = LeitorCSV()
        assert leitor.banco is None
        
        leitor = LeitorCSV(banco='itau')
        assert leitor.banco == 'itau'
    
    def test_ler_extrato_itau(self, extrato_itau):
        """Testa leitura de extrato Itaú."""
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        # Verificar quantidade
        assert len(lancamentos) == 5
        
        # Verificar primeiro lançamento
        primeiro = lancamentos[0]
        assert isinstance(primeiro, Lancamento)
        assert primeiro.data == date(2025, 11, 2)
        assert primeiro.valor == Decimal("150.50")
        assert primeiro.tipo == "D"
        assert "FORNECEDOR XYZ" in primeiro.descricao
        
        # Verificar segundo lançamento (crédito)
        segundo = lancamentos[1]
        assert segundo.tipo == "C"
        assert segundo.valor == Decimal("500.00")
    
    def test_ler_extrato_generico(self, extrato_generico):
        """Testa leitura de extrato genérico."""
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_generico)
        
        # Verificar quantidade
        assert len(lancamentos) == 4
        
        # Verificar tipos identificados
        tipos = [l.tipo for l in lancamentos]
        assert 'D' in tipos  # Deve ter débitos
        assert 'C' in tipos  # Deve ter créditos
    
    def test_ler_extrato_com_banco_especifico(self, extrato_itau):
        """Testa leitura forçando banco específico."""
        leitor = LeitorCSV(banco='itau')
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        assert len(lancamentos) == 5
        assert leitor.banco == 'itau'
    
    def test_arquivo_nao_existe(self):
        """Testa erro quando arquivo não existe."""
        leitor = LeitorCSV()
        
        with pytest.raises(ArquivoInvalidoError, match="Arquivo não encontrado"):
            leitor.ler_arquivo("arquivo_inexistente.csv")
    
    def test_extensao_invalida(self):
        """Testa erro com extensão inválida."""
        leitor = LeitorCSV()
        
        with pytest.raises(ArquivoInvalidoError, match="Extensão não suportada"):
            leitor.ler_arquivo("arquivo.docx")
    
    def test_obter_resumo(self, extrato_itau):
        """Testa obtenção de resumo do arquivo."""
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        resumo = leitor.obter_resumo()
        
        assert resumo['total_linhas'] == 5
        assert 'data' in resumo['colunas']
        assert 'valor' in resumo['colunas']
        assert resumo['banco_detectado'] in ['itau', 'generico']
    
    def test_valores_corretos(self, extrato_itau):
        """Testa se valores são extraídos corretamente."""
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        # Verificar valores específicos
        valores = [l.valor for l in lancamentos]
        assert Decimal("150.50") in valores
        assert Decimal("500.00") in valores
        assert Decimal("1234.56") in valores
    
    def test_datas_corretas(self, extrato_itau):
        """Testa se datas são extraídas corretamente."""
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        # Verificar datas específicas
        datas = [l.data for l in lancamentos]
        assert date(2025, 11, 2) in datas
        assert date(2025, 11, 3) in datas
        assert date(2025, 11, 6) in datas
    
    def test_descricoes_limpas(self, extrato_itau):
        """Testa se descrições são limpas corretamente."""
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        # Todas descrições devem estar em uppercase
        for lanc in lancamentos:
            assert lanc.descricao == lanc.descricao.upper()
            assert not lanc.descricao.startswith(' ')
            assert not lanc.descricao.endswith(' ')


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

class TestIntegracaoLeitorCSV:
    """Testes de integração do leitor CSV."""
    
    @pytest.fixture
    def extrato_itau(self):
        """Fixture com caminho do extrato Itaú."""
        return "tests/fixtures/extratos_exemplo/extrato_itau.csv"
    
    def test_pipeline_completo(self, extrato_itau):
        """Testa pipeline completo de leitura."""
        # 1. Ler arquivo
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        # 2. Verificar que todos são válidos
        assert all(isinstance(l, Lancamento) for l in lancamentos)
        
        # 3. Verificar que não há conciliados
        assert all(not l.conciliado for l in lancamentos)
        
        # 4. Verificar que valores são positivos
        assert all(l.valor > 0 for l in lancamentos)
        
        # 5. Verificar que tipos são válidos
        assert all(l.tipo in ['D', 'C'] for l in lancamentos)
    
    def test_estatisticas_basicas(self, extrato_itau):
        """Testa cálculo de estatísticas básicas."""
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(extrato_itau)
        
        # Calcular totais
        total_debitos = sum(
            l.valor for l in lancamentos if l.tipo == 'D'
        )
        total_creditos = sum(
            l.valor for l in lancamentos if l.tipo == 'C'
        )
        
        # Verificar que há movimentação
        assert total_debitos > 0
        assert total_creditos > 0
        
        # Verificar valores esperados (do CSV de exemplo)
        assert total_debitos == Decimal("1410.96")  # 150.50 + 25.90 + 1234.56
        assert total_creditos == Decimal("3000.00")  # 500 + 2500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
