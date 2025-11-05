"""
Testes da EstrategiaRegras.

Testa integração de Parser + Engine ao Motor de Conciliação.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from decimal import Decimal
from datetime import date

from src.conciliacao.estrategias.regras import EstrategiaRegras
from src.modelos.lancamento import Lancamento


class TestEstrategiaRegras:
    """Testes da estratégia de regras YAML."""

    # ========================================
    # FIXTURES
    # ========================================

    @pytest.fixture
    def lancamento_tarifa_doc(self):
        """Lançamento de tarifa DOC (deve fazer match)."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("15.00"),
            descricao="TARIFA DOC TRANSFERENCIA",
            tipo="D",
        )

    @pytest.fixture
    def lancamento_tarifa_pix(self):
        """Lançamento de tarifa PIX (deve fazer match)."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("2.50"),
            descricao="TARIFA PIX ENVIADO",
            tipo="D",
        )

    @pytest.fixture
    def lancamento_compra_normal(self):
        """Lançamento de compra normal (NÃO deve fazer match)."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("250.00"),
            descricao="COMPRA LOJA ABC LTDA",
            tipo="D",
        )

    @pytest.fixture
    def lancamento_iof(self):
        """Lançamento de IOF (deve fazer match)."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("5.50"),
            descricao="IOF CARTAO CREDITO",
            tipo="D",
        )

    @pytest.fixture
    def lancamento_rendimento_poupanca(self):
        """Lançamento de rendimento (deve fazer match)."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("12.30"),
            descricao="RENDIMENTO POUPANCA",
            tipo="C",
        )

    # ========================================
    # TESTES DE INICIALIZAÇÃO
    # ========================================

    def test_inicializacao_padrao(self):
        """Testa inicialização com arquivo padrão."""
        estrategia = EstrategiaRegras()

        assert estrategia.nome == "Regras YAML"
        assert estrategia.prioridade == 20  # Alta prioridade
        assert estrategia.arquivo_regras == Path("config/regras/tarifas.yaml")
        assert estrategia.engine is not None

    def test_inicializacao_com_arquivo_customizado(self, tmp_path):
        """Testa inicialização com arquivo customizado."""
        # Criar arquivo YAML temporário
        arquivo = tmp_path / "custom.yaml"
        arquivo.write_text(
            """
regras:
  - id: teste
    nome: Regra Teste
    condicoes:
      - campo: valor
        operador: equals
        valor: 10.00
    acao:
      tipo: auto_aprovar
      confianca: 0.90
""",
            encoding="utf-8",
        )

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)

        assert estrategia.arquivo_regras == arquivo
        assert estrategia.engine is not None
        assert len(estrategia.engine.regras) == 1

    def test_inicializacao_arquivo_inexistente(self):
        """Testa inicialização com arquivo inexistente."""
        estrategia = EstrategiaRegras(arquivo_regras=Path("arquivo_nao_existe.yaml"))

        # Deve criar engine vazia
        assert estrategia.engine is not None
        assert len(estrategia.engine.regras) == 0

    def test_carregar_arquivo_tarifas_real(self):
        """Testa carregamento do arquivo real de tarifas."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo config/regras/tarifas.yaml não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)

        assert estrategia.engine is not None
        assert len(estrategia.engine.regras) > 0
        print(f"\nCarregadas {len(estrategia.engine.regras)} regras")

    # ========================================
    # TESTES DE MATCHING
    # ========================================

    def test_match_tarifa_doc(self, lancamento_tarifa_doc):
        """Testa match de tarifa DOC."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        match = estrategia.encontrar_match(lancamento_tarifa_doc, [], set())

        assert match is not None
        assert match.lancamento == lancamento_tarifa_doc
        assert match.comprovante is None  # Auto-conciliação sem comprovante
        assert match.metodo == "regra"
        assert match.confianca >= 0.90  # Alta confiança
        assert "DOC/TED" in match.observacoes or "tarifa" in match.observacoes.lower()

    def test_match_tarifa_pix(self, lancamento_tarifa_pix):
        """Testa match de tarifa PIX."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        match = estrategia.encontrar_match(lancamento_tarifa_pix, [], set())

        assert match is not None
        assert match.metodo == "regra"
        assert match.confianca >= 0.90
        assert "PIX" in match.observacoes or "pix" in match.observacoes.lower()

    def test_match_iof(self, lancamento_iof):
        """Testa match de IOF."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        match = estrategia.encontrar_match(lancamento_iof, [], set())

        assert match is not None
        assert match.metodo == "regra"
        assert "IOF" in match.observacoes or "iof" in match.observacoes.lower()

    def test_match_rendimento(self, lancamento_rendimento_poupanca):
        """Testa match de rendimento de poupança."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        match = estrategia.encontrar_match(lancamento_rendimento_poupanca, [], set())

        assert match is not None
        assert match.metodo == "regra"
        assert match.lancamento.tipo == "C"  # Crédito
        assert (
            "rendimento" in match.observacoes.lower()
            or "poupan" in match.observacoes.lower()
        )

    def test_nao_encontrar_match_compra_normal(self, lancamento_compra_normal):
        """Testa que compra normal NÃO faz match."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        match = estrategia.encontrar_match(lancamento_compra_normal, [], set())

        # Compra normal não deve fazer match com regras de tarifas
        assert match is None

    def test_estrategia_nao_usa_comprovantes(self, lancamento_tarifa_doc):
        """Testa que estratégia ignora lista de comprovantes."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)

        # Passar lista vazia ou lista cheia - não deve fazer diferença
        match1 = estrategia.encontrar_match(lancamento_tarifa_doc, [], set())
        match2 = estrategia.encontrar_match(lancamento_tarifa_doc, [None], set())

        # Ambos devem ter mesmo resultado (match ou None)
        assert (match1 is None) == (match2 is None)

        if match1:
            assert match1.comprovante is None
            assert match2.comprovante is None

    # ========================================
    # TESTES DE FUNCIONALIDADES
    # ========================================

    def test_recarregar_regras(self):
        """Testa recarregamento de regras."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        num_regras_inicial = len(estrategia.engine.regras)

        # Recarregar
        num_regras_recarregado = estrategia.recarregar_regras()

        assert num_regras_recarregado == num_regras_inicial
        assert num_regras_recarregado > 0

    def test_obter_estatisticas(self):
        """Testa obtenção de estatísticas."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        stats = estrategia.obter_estatisticas()

        assert "total_regras" in stats
        assert "arquivo" in stats
        assert "estrategia" in stats
        assert "prioridade" in stats

        assert stats["total_regras"] > 0
        assert stats["arquivo"] == str(arquivo)
        assert stats["estrategia"] == "Regras YAML"
        assert stats["prioridade"] == 20

    def test_estatisticas_engine_vazia(self):
        """Testa estatísticas com engine não carregada."""
        estrategia = EstrategiaRegras(arquivo_regras=Path("nao_existe.yaml"))

        stats = estrategia.obter_estatisticas()

        assert stats["total_regras"] == 0
        assert "status" in stats
        assert stats["status"] == "não carregada"

    def test_repr(self):
        """Testa representação string."""
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo de regras não encontrado")

        estrategia = EstrategiaRegras(arquivo_regras=arquivo)
        repr_str = repr(estrategia)

        assert "EstrategiaRegras" in repr_str
        assert "Regras YAML" in repr_str
        assert "prioridade=20" in repr_str
        assert "regras=" in repr_str

    # ========================================
    # TESTES DE PRIORIDADE
    # ========================================

    def test_prioridade_maior_que_exato(self):
        """Testa que prioridade é maior que EstrategiaExato."""
        estrategia = EstrategiaRegras()

        # EstrategiaRegras deve ter prioridade > EstrategiaExato (10)
        assert estrategia.prioridade == 20
        assert estrategia.prioridade > 10  # Maior que exato

    def test_prioridade_customizada(self):
        """Testa definição de prioridade customizada."""
        estrategia = EstrategiaRegras(prioridade=50)

        assert estrategia.prioridade == 50
