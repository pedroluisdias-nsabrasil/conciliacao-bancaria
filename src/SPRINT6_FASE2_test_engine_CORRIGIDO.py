"""
Testes da EngineRegras.

Testa processamento de regras e todos os operadores.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path para imports funcionarem
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from decimal import Decimal
from datetime import date

from src.regras.engine import EngineRegras
from src.modelos.lancamento import Lancamento


class TestEngineRegras:
    """Testes da engine de regras."""

    # ========================================
    # FIXTURES
    # ========================================

    @pytest.fixture
    def lancamento_tarifa_doc(self):
        """Lançamento de tarifa DOC."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("15.00"),
            descricao="TARIFA DOC TRANSF",
            tipo="D",
        )

    @pytest.fixture
    def lancamento_pix(self):
        """Lançamento PIX."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("250.00"),
            descricao="PIX ENVIADO JOAO SILVA",
            tipo="D",
        )

    @pytest.fixture
    def lancamento_grande_valor(self):
        """Lançamento de grande valor."""
        return Lancamento(
            data=date(2025, 11, 5),
            valor=Decimal("5000.00"),
            descricao="COMPRA LOJA XYZ",
            tipo="D",
        )

    # ========================================
    # TESTES BÁSICOS
    # ========================================

    def test_engine_vazia(self):
        """Testa engine sem regras."""
        engine = EngineRegras([])

        lancamento = Lancamento(
            data=date(2025, 11, 5), valor=Decimal("10.00"), descricao="TESTE", tipo="D"
        )

        match = engine.processar(lancamento)
        assert match is None

    def test_engine_com_regras(self):
        """Testa engine com regras carregadas."""
        regras = [
            {
                "id": "teste",
                "nome": "Regra Teste",
                "prioridade": 10,
                "condicoes": [{"campo": "valor", "operador": "equals", "valor": 10.00}],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        assert len(engine.regras) == 1

    def test_prioridade_regras(self):
        """Testa ordenação por prioridade."""
        regras = [
            {"id": "baixa", "prioridade": 5, "condicoes": [], "acao": {}},
            {"id": "alta", "prioridade": 10, "condicoes": [], "acao": {}},
            {"id": "media", "prioridade": 7, "condicoes": [], "acao": {}},
        ]

        engine = EngineRegras(regras)

        # Deve ordenar: alta (10), media (7), baixa (5)
        assert engine.regras[0]["id"] == "alta"
        assert engine.regras[1]["id"] == "media"
        assert engine.regras[2]["id"] == "baixa"

    # ========================================
    # TESTES DE OPERADORES
    # ========================================

    def test_operador_equals(self, lancamento_tarifa_doc):
        """Testa operador equals."""
        regras = [
            {
                "id": "teste_equals",
                "nome": "Teste Equals",
                "prioridade": 10,
                "condicoes": [{"campo": "tipo", "operador": "equals", "valor": "D"}],
                "acao": {
                    "tipo": "auto_aprovar",
                    "confianca": 0.90,
                    "observacao": "Match equals",
                },
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None
        assert match.confianca == 0.90
        assert "Match equals" in match.observacoes

    def test_operador_not_equals(self, lancamento_tarifa_doc):
        """Testa operador not_equals."""
        regras = [
            {
                "id": "teste_not_equals",
                "nome": "Teste Not Equals",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "tipo", "operador": "not_equals", "valor": "C"}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    def test_operador_contains(self, lancamento_tarifa_doc):
        """Testa operador contains."""
        regras = [
            {
                "id": "teste_contains",
                "nome": "Teste Contains",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "descricao", "operador": "contains", "valor": "TARIFA"}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    def test_operador_contains_case_insensitive(self, lancamento_tarifa_doc):
        """Testa que contains é case-insensitive."""
        regras = [
            {
                "id": "teste_case",
                "nome": "Teste Case",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "descricao", "operador": "contains", "valor": "tarifa"}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    def test_operador_contains_lista(self, lancamento_pix):
        """Testa operador contains com lista de valores."""
        regras = [
            {
                "id": "teste_lista",
                "nome": "Teste Lista",
                "prioridade": 10,
                "condicoes": [
                    {
                        "campo": "descricao",
                        "operador": "contains",
                        "valor": ["PIX", "TED"],
                    }
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_pix)

        assert match is not None

    def test_operador_not_contains(self, lancamento_tarifa_doc):
        """Testa operador not_contains."""
        regras = [
            {
                "id": "teste_not_contains",
                "nome": "Teste Not Contains",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "descricao", "operador": "not_contains", "valor": "PIX"}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    def test_operador_regex(self, lancamento_tarifa_doc):
        """Testa operador regex."""
        regras = [
            {
                "id": "teste_regex",
                "nome": "Teste Regex",
                "prioridade": 10,
                "condicoes": [
                    {
                        "campo": "descricao",
                        "operador": "regex",
                        "valor": r"TARIFA\s+(DOC|TED)",
                    }
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.95},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None
        assert match.confianca == 0.95

    def test_operador_greater_than(self, lancamento_grande_valor):
        """Testa operador greater_than."""
        regras = [
            {
                "id": "teste_gt",
                "nome": "Teste Greater Than",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "valor", "operador": "greater_than", "valor": 1000.00}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_grande_valor)

        assert match is not None

    def test_operador_less_than(self, lancamento_tarifa_doc):
        """Testa operador less_than."""
        regras = [
            {
                "id": "teste_lt",
                "nome": "Teste Less Than",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "valor", "operador": "less_than", "valor": 100.00}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    def test_operador_between(self, lancamento_tarifa_doc):
        """Testa operador between."""
        regras = [
            {
                "id": "teste_between",
                "nome": "Teste Between",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "valor", "operador": "between", "valor": [10.00, 20.00]}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    def test_operador_in(self, lancamento_tarifa_doc):
        """Testa operador in."""
        regras = [
            {
                "id": "teste_in",
                "nome": "Teste In",
                "prioridade": 10,
                "condicoes": [{"campo": "tipo", "operador": "in", "valor": ["D", "C"]}],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    def test_operador_not_in(self, lancamento_tarifa_doc):
        """Testa operador not_in."""
        regras = [
            {
                "id": "teste_not_in",
                "nome": "Teste Not In",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "tipo", "operador": "not_in", "valor": ["X", "Y"]}
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None

    # ========================================
    # TESTES DE MÚLTIPLAS CONDIÇÕES
    # ========================================

    def test_multiplas_condicoes_todas_true(self, lancamento_tarifa_doc):
        """Testa múltiplas condições - todas verdadeiras."""
        regras = [
            {
                "id": "teste_multi",
                "nome": "Teste Múltiplas",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "tipo", "operador": "equals", "valor": "D"},
                    {"campo": "valor", "operador": "less_than", "valor": 100.00},
                    {"campo": "descricao", "operador": "contains", "valor": "TARIFA"},
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.95},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        # Todas condições satisfeitas
        assert match is not None
        assert match.confianca == 0.95

    def test_multiplas_condicoes_uma_false(self, lancamento_tarifa_doc):
        """Testa múltiplas condições - uma falsa."""
        regras = [
            {
                "id": "teste_multi_false",
                "nome": "Teste Multi False",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "tipo", "operador": "equals", "valor": "D"},
                    {
                        "campo": "valor",
                        "operador": "greater_than",
                        "valor": 1000.00,
                    },  # FALSO
                    {"campo": "descricao", "operador": "contains", "valor": "TARIFA"},
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.95},
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        # Uma condição falhou - não deve fazer match
        assert match is None

    # ========================================
    # TESTES DE CASCATA
    # ========================================

    def test_cascata_primeira_regra_match(self, lancamento_tarifa_doc):
        """Testa que para na primeira regra que faz match."""
        regras = [
            {
                "id": "regra1",
                "nome": "Regra 1",
                "prioridade": 10,
                "condicoes": [{"campo": "tipo", "operador": "equals", "valor": "D"}],
                "acao": {
                    "tipo": "auto_aprovar",
                    "confianca": 0.90,
                    "observacao": "Regra 1",
                },
            },
            {
                "id": "regra2",
                "nome": "Regra 2",
                "prioridade": 5,
                "condicoes": [{"campo": "tipo", "operador": "equals", "valor": "D"}],
                "acao": {
                    "tipo": "auto_aprovar",
                    "confianca": 0.80,
                    "observacao": "Regra 2",
                },
            },
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        # Deve aplicar regra1 (maior prioridade)
        assert match is not None
        assert "Regra 1" in match.observacoes
        assert match.confianca == 0.90

    def test_cascata_segunda_regra_match(self, lancamento_tarifa_doc):
        """Testa que tenta segunda regra se primeira falhar."""
        regras = [
            {
                "id": "regra1",
                "nome": "Regra 1",
                "prioridade": 10,
                "condicoes": [
                    {"campo": "tipo", "operador": "equals", "valor": "C"}  # Não match
                ],
                "acao": {"tipo": "auto_aprovar", "confianca": 0.90},
            },
            {
                "id": "regra2",
                "nome": "Regra 2",
                "prioridade": 5,
                "condicoes": [
                    {"campo": "tipo", "operador": "equals", "valor": "D"}  # Match!
                ],
                "acao": {
                    "tipo": "auto_aprovar",
                    "confianca": 0.80,
                    "observacao": "Regra 2",
                },
            },
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        # Deve aplicar regra2
        assert match is not None
        assert "Regra 2" in match.observacoes

    # ========================================
    # TESTES DE MATCH
    # ========================================

    def test_match_contem_informacoes_regra(self, lancamento_tarifa_doc):
        """Testa que Match contém informações da regra."""
        regras = [
            {
                "id": "teste_info",
                "nome": "Regra de Teste",
                "prioridade": 10,
                "condicoes": [{"campo": "tipo", "operador": "equals", "valor": "D"}],
                "acao": {
                    "tipo": "auto_aprovar",
                    "confianca": 0.95,
                    "observacao": "Tarifa bancária identificada",
                    "categoria": "Despesa Bancária",
                },
            }
        ]

        engine = EngineRegras(regras)
        match = engine.processar(lancamento_tarifa_doc)

        assert match is not None
        assert match.confianca == 0.95
        assert match.metodo == "regra"
        assert match.comprovante is None
        assert "Tarifa bancária identificada" in match.observacoes
        assert "teste_info" in match.observacoes
        assert "Despesa Bancária" in match.observacoes

    # ========================================
    # TESTES DE ESTATÍSTICAS
    # ========================================

    def test_estatisticas(self):
        """Testa método de estatísticas."""
        regras = [
            {
                "id": "regra1",
                "prioridade": 10,
                "condicoes": [],
                "acao": {"tipo": "auto_aprovar"},
            },
            {
                "id": "regra2",
                "prioridade": 5,
                "condicoes": [],
                "acao": {"tipo": "sugerir"},
            },
        ]

        engine = EngineRegras(regras)
        stats = engine.estatisticas()

        assert stats["total_regras"] == 2
        assert "regra1" in stats["por_prioridade"]
        assert stats["por_prioridade"]["regra1"] == 10
        assert stats["tipos_acao"]["regra1"] == "auto_aprovar"
