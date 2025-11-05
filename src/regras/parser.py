"""
Parser de regras YAML.

Lê arquivos YAML e retorna lista de regras validadas.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ParserRegras:
    """Parser de arquivos YAML de regras."""

    def __init__(self, arquivo_regras: Path):
        """
        Inicializa parser.

        Args:
            arquivo_regras: Caminho para arquivo YAML

        Examples:
            >>> parser = ParserRegras(Path('config/regras/tarifas.yaml'))
            >>> regras = parser.carregar()
        """
        self.arquivo_regras = Path(arquivo_regras)
        self.regras: List[Dict[str, Any]] = []

    def carregar(self) -> List[Dict[str, Any]]:
        """
        Carrega e valida regras do arquivo YAML.

        Returns:
            Lista de regras validadas

        Raises:
            FileNotFoundError: Se arquivo não existe
            yaml.YAMLError: Se YAML inválido
            ValueError: Se estrutura de regras inválida

        Examples:
            >>> parser = ParserRegras(Path('config/regras/tarifas.yaml'))
            >>> regras = parser.carregar()
            >>> len(regras) > 0
            True
        """
        if not self.arquivo_regras.exists():
            raise FileNotFoundError(
                f"Arquivo de regras não encontrado: {self.arquivo_regras}"
            )

        try:
            with open(self.arquivo_regras, "r", encoding="utf-8") as f:
                dados = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Erro ao parsear YAML: {e}")
            raise

        if not dados or "regras" not in dados:
            logger.warning(f"Nenhuma regra encontrada em {self.arquivo_regras}")
            return []

        self.regras = dados["regras"]
        self._validar_regras()

        # Filtrar apenas regras ativas
        regras_ativas = [r for r in self.regras if r.get("ativo", True)]

        logger.info(
            f"Carregadas {len(regras_ativas)} regras ativas de "
            f"{len(self.regras)} totais de {self.arquivo_regras}"
        )

        return regras_ativas

    def _validar_regras(self) -> None:
        """
        Valida estrutura das regras.

        Raises:
            ValueError: Se alguma regra tem estrutura inválida
        """
        campos_obrigatorios = ["id", "nome", "condicoes", "acao"]

        for i, regra in enumerate(self.regras):
            # Verificar campos obrigatórios
            for campo in campos_obrigatorios:
                if campo not in regra:
                    raise ValueError(
                        f"Regra #{i} sem campo obrigatório '{campo}': {regra}"
                    )

            # Validar ID único
            ids = [r["id"] for r in self.regras]
            if ids.count(regra["id"]) > 1:
                raise ValueError(f"ID duplicado encontrado: '{regra['id']}'")

            # Validar condições
            if not isinstance(regra["condicoes"], list):
                raise ValueError(
                    f"Regra '{regra['id']}': 'condicoes' deve ser uma lista"
                )

            if len(regra["condicoes"]) == 0:
                raise ValueError(
                    f"Regra '{regra['id']}': 'condicoes' não pode estar vazia"
                )

            # Validar cada condição
            for j, condicao in enumerate(regra["condicoes"]):
                campos_condicao = ["campo", "operador", "valor"]
                for campo in campos_condicao:
                    if campo not in condicao:
                        raise ValueError(
                            f"Regra '{regra['id']}', condição #{j}: "
                            f"falta campo '{campo}'"
                        )

                # Validar operadores conhecidos
                operadores_validos = [
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

                if condicao["operador"] not in operadores_validos:
                    raise ValueError(
                        f"Regra '{regra['id']}', condição #{j}: "
                        f"operador inválido '{condicao['operador']}'. "
                        f"Válidos: {operadores_validos}"
                    )

            # Validar ação
            if not isinstance(regra["acao"], dict):
                raise ValueError(
                    f"Regra '{regra['id']}': 'acao' deve ser um dicionário"
                )

            if "tipo" not in regra["acao"]:
                raise ValueError(f"Regra '{regra['id']}': 'acao' deve ter campo 'tipo'")

            # Validar tipo de ação
            tipos_validos = ["auto_aprovar", "sugerir", "ignorar"]
            if regra["acao"]["tipo"] not in tipos_validos:
                raise ValueError(
                    f"Regra '{regra['id']}': tipo de ação inválido "
                    f"'{regra['acao']['tipo']}'. Válidos: {tipos_validos}"
                )

        logger.debug(f"{len(self.regras)} regras validadas com sucesso")
