"""
Testes do ParserRegras.

Testa leitura, validação e parsing de arquivos YAML de regras.
"""

import pytest
import yaml
from pathlib import Path
from src.regras.parser import ParserRegras


class TestParserRegras:
    """Testes do parser de regras YAML."""

    def test_carregar_regras_validas(self, tmp_path):
        """Testa carregamento de arquivo YAML válido."""
        # Criar arquivo YAML temporário
        arquivo = tmp_path / "regras_validas.yaml"

        conteudo = """
regras:
  - id: teste_1
    nome: "Regra de Teste"
    descricao: "Teste básico"
    ativo: true
    prioridade: 10
    
    condicoes:
      - campo: descricao
        operador: equals
        valor: "TESTE"
    
    acao:
      tipo: auto_aprovar
      confianca: 0.90
      observacao: "Teste"
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        # Carregar regras
        parser = ParserRegras(arquivo)
        regras = parser.carregar()

        # Verificações
        assert len(regras) == 1
        assert regras[0]["id"] == "teste_1"
        assert regras[0]["nome"] == "Regra de Teste"
        assert regras[0]["ativo"] is True
        assert len(regras[0]["condicoes"]) == 1
        assert regras[0]["acao"]["tipo"] == "auto_aprovar"

    def test_carregar_arquivo_inexistente(self):
        """Testa erro ao carregar arquivo que não existe."""
        parser = ParserRegras(Path("arquivo_que_nao_existe.yaml"))

        with pytest.raises(FileNotFoundError) as exc_info:
            parser.carregar()

        assert "não encontrado" in str(exc_info.value)

    def test_carregar_yaml_invalido(self, tmp_path):
        """Testa erro com YAML inválido."""
        arquivo = tmp_path / "yaml_invalido.yaml"
        arquivo.write_text("{ invalid yaml content [", encoding="utf-8")

        parser = ParserRegras(arquivo)

        with pytest.raises(yaml.YAMLError):
            parser.carregar()

    def test_arquivo_vazio(self, tmp_path):
        """Testa arquivo YAML vazio."""
        arquivo = tmp_path / "vazio.yaml"
        arquivo.write_text("", encoding="utf-8")

        parser = ParserRegras(arquivo)
        regras = parser.carregar()

        assert regras == []

    def test_sem_chave_regras(self, tmp_path):
        """Testa YAML sem chave 'regras'."""
        arquivo = tmp_path / "sem_regras.yaml"
        arquivo.write_text("outro_campo: valor", encoding="utf-8")

        parser = ParserRegras(arquivo)
        regras = parser.carregar()

        assert regras == []

    def test_filtrar_regras_inativas(self, tmp_path):
        """Testa filtragem de regras inativas."""
        arquivo = tmp_path / "com_inativas.yaml"

        conteudo = """
regras:
  - id: ativa
    nome: "Regra Ativa"
    ativo: true
    condicoes:
      - campo: valor
        operador: equals
        valor: 100
    acao:
      tipo: auto_aprovar
  
  - id: inativa
    nome: "Regra Inativa"
    ativo: false
    condicoes:
      - campo: valor
        operador: equals
        valor: 200
    acao:
      tipo: auto_aprovar
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)
        regras = parser.carregar()

        # Deve retornar apenas a regra ativa
        assert len(regras) == 1
        assert regras[0]["id"] == "ativa"

    def test_validacao_campo_obrigatorio_faltando(self, tmp_path):
        """Testa erro quando falta campo obrigatório."""
        arquivo = tmp_path / "sem_id.yaml"

        conteudo = """
regras:
  - nome: "Regra Sem ID"
    condicoes:
      - campo: valor
        operador: equals
        valor: 100
    acao:
      tipo: auto_aprovar
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)

        with pytest.raises(ValueError) as exc_info:
            parser.carregar()

        assert "id" in str(exc_info.value)

    def test_validacao_id_duplicado(self, tmp_path):
        """Testa erro com IDs duplicados."""
        arquivo = tmp_path / "ids_duplicados.yaml"

        conteudo = """
regras:
  - id: duplicado
    nome: "Regra 1"
    condicoes:
      - campo: valor
        operador: equals
        valor: 100
    acao:
      tipo: auto_aprovar
  
  - id: duplicado
    nome: "Regra 2"
    condicoes:
      - campo: valor
        operador: equals
        valor: 200
    acao:
      tipo: auto_aprovar
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)

        with pytest.raises(ValueError) as exc_info:
            parser.carregar()

        assert "duplicado" in str(exc_info.value).lower()

    def test_validacao_condicoes_lista_vazia(self, tmp_path):
        """Testa erro quando condições está vazio."""
        arquivo = tmp_path / "condicoes_vazias.yaml"

        conteudo = """
regras:
  - id: teste
    nome: "Regra Teste"
    condicoes: []
    acao:
      tipo: auto_aprovar
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)

        with pytest.raises(ValueError) as exc_info:
            parser.carregar()

        assert "vazia" in str(exc_info.value).lower()

    def test_validacao_operador_invalido(self, tmp_path):
        """Testa erro com operador inválido."""
        arquivo = tmp_path / "operador_invalido.yaml"

        conteudo = """
regras:
  - id: teste
    nome: "Regra Teste"
    condicoes:
      - campo: valor
        operador: operador_inexistente
        valor: 100
    acao:
      tipo: auto_aprovar
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)

        with pytest.raises(ValueError) as exc_info:
            parser.carregar()

        assert "operador inválido" in str(exc_info.value).lower()

    def test_validacao_tipo_acao_invalido(self, tmp_path):
        """Testa erro com tipo de ação inválido."""
        arquivo = tmp_path / "acao_invalida.yaml"

        conteudo = """
regras:
  - id: teste
    nome: "Regra Teste"
    condicoes:
      - campo: valor
        operador: equals
        valor: 100
    acao:
      tipo: tipo_inexistente
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)

        with pytest.raises(ValueError) as exc_info:
            parser.carregar()

        assert "tipo de ação inválido" in str(exc_info.value).lower()

    def test_carregar_arquivo_tarifas_real(self):
        """Testa carregamento do arquivo real de tarifas."""
        # Este teste assume que o arquivo existe no projeto
        arquivo = Path("config/regras/tarifas.yaml")

        if not arquivo.exists():
            pytest.skip("Arquivo config/regras/tarifas.yaml não encontrado")

        parser = ParserRegras(arquivo)
        regras = parser.carregar()

        # Verificações básicas
        assert len(regras) > 0

        # Verificar que todas têm campos obrigatórios
        for regra in regras:
            assert "id" in regra
            assert "nome" in regra
            assert "condicoes" in regra
            assert "acao" in regra
            assert len(regra["condicoes"]) > 0

    def test_regras_multiplas_condicoes(self, tmp_path):
        """Testa regra com múltiplas condições."""
        arquivo = tmp_path / "multiplas_condicoes.yaml"

        conteudo = """
regras:
  - id: multi
    nome: "Múltiplas Condições"
    condicoes:
      - campo: descricao
        operador: contains
        valor: "TESTE"
      - campo: valor
        operador: between
        valor: [10.00, 100.00]
      - campo: tipo
        operador: equals
        valor: "D"
    acao:
      tipo: auto_aprovar
      confianca: 0.95
"""

        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)
        regras = parser.carregar()

        assert len(regras) == 1
        assert len(regras[0]["condicoes"]) == 3
        assert regras[0]["acao"]["confianca"] == 0.95

    def test_todos_operadores_validos(self, tmp_path):
        """Testa que todos os operadores documentados são aceitos."""
        arquivo = tmp_path / "todos_operadores.yaml"

        operadores = [
            "equals",
            "not_equals",
            "contains",
            "not_contains",
            "regex",
            "greater_than",
            "less_than",
            "between",
            "in",
            "not_in",
        ]

        regras_yaml = ["regras:"]

        for i, op in enumerate(operadores):
            regra = f"""
  - id: teste_{i}
    nome: "Teste {op}"
    condicoes:
      - campo: campo_teste
        operador: {op}
        valor: "valor_teste"
    acao:
      tipo: auto_aprovar
"""
            regras_yaml.append(regra)

        conteudo = "\n".join(regras_yaml)
        arquivo.write_text(conteudo, encoding="utf-8")

        parser = ParserRegras(arquivo)
        regras = parser.carregar()

        # Todos devem carregar sem erro
        assert len(regras) == len(operadores)
