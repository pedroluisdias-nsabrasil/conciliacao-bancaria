"""
Estratégia de Matching Exato

Implementa matching entre lançamentos e comprovantes usando critérios exatos:
- Valor monetário exato (Decimal)
- Data dentro de janela de tolerância (±N dias)
- Sistema de confiança baseado em múltiplos fatores

Esta é a estratégia de maior prioridade, executada primeiro pelo motor,
pois tem alta taxa de acerto (>95%) em casos comuns.

Autor: Pedro Luis (pedroluisdias@br-nsa.com)
Data: 03/11/2025
Sprint: 3 - Motor de Conciliação
"""

from typing import List, Optional, Set
from decimal import Decimal
from datetime import date, timedelta
import logging

# Imports do projeto
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.modelos import Lancamento, Comprovante, Match
from src.conciliacao.estrategias.base import (
    EstrategiaBase,
    criar_match_com_confianca,
    validar_confianca,
)

logger = logging.getLogger(__name__)


class EstrategiaExato(EstrategiaBase):
    """
    Estratégia de matching por valor e data exatos.
    
    Esta estratégia procura matches "perfeitos" onde:
    - Valor do lançamento = Valor do comprovante (exato)
    - Data do lançamento está próxima da data do comprovante (±N dias)
    
    É a estratégia de maior prioridade (prioridade=10) pois tem:
    - Alta precisão (>95%)
    - Alta confiança nos matches
    - Baixa taxa de falsos positivos
    
    Sistema de Confiança:
        A confiança é calculada somando pontos por critérios:
        
        - Valor exato: +0.50 (50%)
        - Data exata: +0.30 (30%)
        - Data ±1 dia: +0.25 (25%)
        - Data ±2 dias: +0.20 (20%)
        - Data ±3 dias: +0.15 (15%)
        - Descrição similar: +0.15 (15%) [opcional]
        - OCR confiável (>0.8): +0.05 (5%) [opcional]
        
        Confiança >= 0.90 → Auto-aprovar
        Confiança >= 0.60 → Revisar
        Confiança <  0.60 → Não conciliar
    
    Attributes:
        tolerancia_dias: Janela de dias para matching (padrão: 3)
        tolerancia_valor: Tolerância em centavos (padrão: 0.00 = exato)
        usar_descricao: Se deve considerar similaridade de descrição
        min_similaridade_descricao: Similaridade mínima da descrição (0.0-1.0)
    
    Examples:
        >>> estrategia = EstrategiaExato(tolerancia_dias=3)
        >>> match = estrategia.encontrar_match(lancamento, comprovantes, set())
        >>> if match and match.confianca >= 0.90:
        ...     print("Match de alta confiança!")
    """
    
    def __init__(
        self,
        tolerancia_dias: int = 3,
        tolerancia_valor: Decimal = Decimal('0.00'),
        usar_descricao: bool = False,
        min_similaridade_descricao: float = 0.7
    ):
        """
        Inicializa a estratégia de matching exato.
        
        Args:
            tolerancia_dias: Dias de tolerância para matching de data (padrão: 3)
            tolerancia_valor: Tolerância de valor em R$ (padrão: 0.00 = exato)
            usar_descricao: Se deve considerar similaridade de descrição
            min_similaridade_descricao: Similaridade mínima (0.0-1.0)
        
        Raises:
            ValueError: Se tolerância de dias < 0 ou > 10
            ValueError: Se tolerância de valor < 0
            ValueError: Se min_similaridade < 0 ou > 1
        """
        # Inicializar classe base com nome e prioridade alta
        super().__init__(nome="Matching Exato", prioridade=10)
        
        # Validar parâmetros
        if tolerancia_dias < 0 or tolerancia_dias > 10:
            raise ValueError(
                f"Tolerância de dias deve estar entre 0 e 10, "
                f"recebido: {tolerancia_dias}"
            )
        
        if tolerancia_valor < 0:
            raise ValueError(
                f"Tolerância de valor não pode ser negativa, "
                f"recebido: {tolerancia_valor}"
            )
        
        if not 0.0 <= min_similaridade_descricao <= 1.0:
            raise ValueError(
                f"Similaridade mínima deve estar entre 0.0 e 1.0, "
                f"recebido: {min_similaridade_descricao}"
            )
        
        # Armazenar configurações
        self.tolerancia_dias = tolerancia_dias
        self.tolerancia_valor = tolerancia_valor
        self.usar_descricao = usar_descricao
        self.min_similaridade_descricao = min_similaridade_descricao
        
        logger.info(
            f"EstrategiaExato inicializada: "
            f"tolerancia_dias={tolerancia_dias}, "
            f"tolerancia_valor={tolerancia_valor}, "
            f"usar_descricao={usar_descricao}"
        )
    
    def encontrar_match(
        self,
        lancamento: Lancamento,
        comprovantes: List[Comprovante],
        usados: Set[int]
    ) -> Optional[Match]:
        """
        Encontra o melhor match para um lançamento.
        
        Procura entre os comprovantes disponíveis por aquele que melhor
        corresponde ao lançamento em termos de valor e data.
        
        Args:
            lancamento: Lançamento bancário a ser conciliado
            comprovantes: Lista de comprovantes disponíveis
            usados: Set com IDs dos comprovantes já usados
        
        Returns:
            Match com o melhor candidato e confiança, ou None se não encontrar
        
        Examples:
            >>> estrategia = EstrategiaExato()
            >>> match = estrategia.encontrar_match(lanc, comps, set())
            >>> if match:
            ...     print(f"Confiança: {match.confianca:.0%}")
        """
        logger.debug(
            f"Buscando match para lançamento: "
            f"valor={lancamento.valor}, data={lancamento.data}"
        )
        
        melhor_match = None
        melhor_confianca = 0.0
        
        # Iterar sobre comprovantes disponíveis
        for comprovante in comprovantes:
            # Pular se já foi usado
            if id(comprovante) in usados:
                logger.debug(f"Comprovante {id(comprovante)} já usado, pulando")
                continue
            
            # Validação básica (sinais, valores zero)
            if not self.validar_match(lancamento, comprovante):
                logger.debug(
                    f"Match inviável entre lançamento e comprovante {id(comprovante)}"
                )
                continue
            
            # Verificar se valor é compatível
            if not self._valores_compativeis(lancamento.valor, comprovante.valor):
                logger.debug(
                    f"Valores incompatíveis: {lancamento.valor} vs {comprovante.valor}"
                )
                continue
            
            # Verificar se data é compatível
            if not self._datas_compativeis(lancamento.data, comprovante.data):
                logger.debug(
                    f"Datas incompatíveis: {lancamento.data} vs {comprovante.data}"
                )
                continue
            
            # Calcular confiança deste candidato
            confianca = self.calcular_confianca(lancamento, comprovante)
            
            logger.debug(
                f"Candidato encontrado: comprovante {id(comprovante)}, "
                f"confiança={confianca:.2%}"
            )
            
            # Atualizar melhor match se este for melhor
            if confianca > melhor_confianca:
                melhor_confianca = confianca
                melhor_match = comprovante
        
        # Se encontrou um match válido, criar objeto Match
        if melhor_match and melhor_confianca >= 0.60:
            observacoes = self._gerar_observacoes(
                lancamento, melhor_match, melhor_confianca
            )
            
            match = criar_match_com_confianca(
                lancamento=lancamento,
                comprovante=melhor_match,
                confianca=melhor_confianca,
                metodo="exato",  
                observacoes=observacoes
            )
            
            logger.info(
                f"Match encontrado com confiança {melhor_confianca:.0%}: "
                f"lançamento {lancamento.descricao[:30]}... ↔ "
                f"comprovante valor={melhor_match.valor}"
            )
            
            return match
        
        # Nenhum match adequado encontrado
        if melhor_match:
            logger.debug(
                f"Match encontrado mas confiança muito baixa: {melhor_confianca:.0%}"
            )
        else:
            logger.debug("Nenhum match encontrado")
        
        return None
    
    def calcular_confianca(
        self,
        lancamento: Lancamento,
        comprovante: Comprovante,
        **kwargs
    ) -> float:
        """
        Calcula a confiança do match entre lançamento e comprovante.
        
        Sistema de pontuação:
            - Valor exato: +0.50
            - Data exata: +0.30
            - Data ±1 dia: +0.25
            - Data ±2 dias: +0.20
            - Data ±3 dias: +0.15
            - Descrição similar: +0.15 (se usar_descricao=True)
            - OCR confiável: +0.05 (se disponível)
        
        Args:
            lancamento: Lançamento bancário
            comprovante: Comprovante de pagamento
            **kwargs: Argumentos adicionais (não usado nesta estratégia)
        
        Returns:
            float: Confiança entre 0.0 e 1.0
        
        Examples:
            >>> confianca = estrategia.calcular_confianca(lanc, comp)
            >>> assert 0.0 <= confianca <= 1.0
        """
        confianca = 0.0
        
        # 1. VALOR EXATO: +0.50
        if self._valores_exatos(lancamento.valor, comprovante.valor):
            confianca += 0.50
            logger.debug("  +0.50 (valor exato)")
        
        # 2. DATA: +0.15 a +0.30 (proporcional à proximidade)
        diff_dias = abs((lancamento.data - comprovante.data).days)
        
        if diff_dias == 0:
            confianca += 0.30
            logger.debug("  +0.30 (data exata)")
        elif diff_dias == 1:
            confianca += 0.25
            logger.debug("  +0.25 (data ±1 dia)")
        elif diff_dias == 2:
            confianca += 0.20
            logger.debug("  +0.20 (data ±2 dias)")
        elif diff_dias <= self.tolerancia_dias:
            confianca += 0.15
            logger.debug(f"  +0.15 (data ±{diff_dias} dias)")
        
        # 3. DESCRIÇÃO SIMILAR: +0.15 (opcional)
        if self.usar_descricao:
            similaridade = self._calcular_similaridade_descricao(
                lancamento.descricao,
                comprovante.beneficiario or ""
            )
            
            if similaridade >= self.min_similaridade_descricao:
                confianca += 0.15
                logger.debug(f"  +0.15 (descrição similar: {similaridade:.0%})")
        
        # 4. OCR CONFIÁVEL: +0.05 (se disponível)
        if hasattr(comprovante, 'confianca_ocr') and comprovante.confianca_ocr:
            if comprovante.confianca_ocr >= 0.80:
                confianca += 0.05
                logger.debug(
                    f"  +0.05 (OCR confiável: {comprovante.confianca_ocr:.0%})"
                )
        
        # Garantir que confiança está no intervalo válido
        confianca = max(0.0, min(1.0, confianca))
        
        logger.debug(f"Confiança total calculada: {confianca:.2%}")
        
        return confianca
    
    def _valores_compativeis(self, valor1: Decimal, valor2: Decimal) -> bool:
        """
        Verifica se dois valores são compatíveis dentro da tolerância.
        
        Args:
            valor1: Primeiro valor (lançamento)
            valor2: Segundo valor (comprovante)
        
        Returns:
            bool: True se valores são compatíveis
        """
        diferenca = abs(valor1 - valor2)
        compativel = diferenca <= self.tolerancia_valor
        
        if not compativel:
            logger.debug(
                f"Valores incompatíveis: diferença={diferenca} > "
                f"tolerância={self.tolerancia_valor}"
            )
        
        return compativel
    
    def _valores_exatos(self, valor1: Decimal, valor2: Decimal) -> bool:
        """
        Verifica se dois valores são exatamente iguais.
        
        Args:
            valor1: Primeiro valor
            valor2: Segundo valor
        
        Returns:
            bool: True se valores são exatamente iguais
        """
        return valor1 == valor2
    
    def _datas_compativeis(self, data1: date, data2: date) -> bool:
        """
        Verifica se duas datas estão dentro da janela de tolerância.
        
        Args:
            data1: Primeira data (lançamento)
            data2: Segunda data (comprovante)
        
        Returns:
            bool: True se datas são compatíveis
        """
        diferenca_dias = abs((data1 - data2).days)
        compativel = diferenca_dias <= self.tolerancia_dias
        
        if not compativel:
            logger.debug(
                f"Datas incompatíveis: diferença={diferenca_dias} dias > "
                f"tolerância={self.tolerancia_dias} dias"
            )
        
        return compativel
    
    def _calcular_similaridade_descricao(
        self,
        descricao1: str,
        descricao2: str
    ) -> float:
        """
        Calcula similaridade entre duas descrições de texto.
        
        Usa algoritmo simples baseado em palavras em comum.
        Para versão futura: usar fuzzywuzzy ou similar.
        
        Args:
            descricao1: Primeira descrição
            descricao2: Segunda descrição
        
        Returns:
            float: Similaridade entre 0.0 e 1.0
        """
        if not descricao1 or not descricao2:
            return 0.0
        
        # Normalizar: lowercase e remover espaços extras
        desc1 = descricao1.lower().strip()
        desc2 = descricao2.lower().strip()
        
        # Dividir em palavras
        palavras1 = set(desc1.split())
        palavras2 = set(desc2.split())
        
        # Calcular interseção e união
        intersecao = palavras1.intersection(palavras2)
        uniao = palavras1.union(palavras2)
        
        # Similaridade de Jaccard
        if len(uniao) == 0:
            return 0.0
        
        similaridade = len(intersecao) / len(uniao)
        
        return similaridade
    
    def _gerar_observacoes(
        self,
        lancamento: Lancamento,
        comprovante: Comprovante,
        confianca: float
    ) -> str:
        """
        Gera texto de observações sobre o match.
        
        Args:
            lancamento: Lançamento matched
            comprovante: Comprovante matched
            confianca: Confiança do match
        
        Returns:
            str: Texto de observações
        """
        obs = []
        
        # Nível de confiança
        if confianca >= 0.90:
            obs.append("✅ Alta confiança - Auto-aprovado")
        elif confianca >= 0.60:
            obs.append("⚠️ Média confiança - Revisar")
        else:
            obs.append("❌ Baixa confiança - Verificar manualmente")
        
        # Diferença de dias
        diff_dias = abs((lancamento.data - comprovante.data).days)
        if diff_dias == 0:
            obs.append("Datas exatas")
        else:
            obs.append(f"Datas com diferença de {diff_dias} dia(s)")
        
        # Valor exato
        if lancamento.valor == comprovante.valor:
            obs.append("Valores exatos")
        
        # OCR confiável
        if hasattr(comprovante, 'confianca_ocr') and comprovante.confianca_ocr:
            if comprovante.confianca_ocr >= 0.80:
                obs.append(f"OCR confiável ({comprovante.confianca_ocr:.0%})")
        
        # Estratégia utilizada
        obs.append(f"Estratégia: {self.nome}")
        
        return " | ".join(obs)
    
    def __str__(self) -> str:
        """Representação em string."""
        return (
            f"EstrategiaExato(tolerancia_dias={self.tolerancia_dias}, "
            f"tolerancia_valor={self.tolerancia_valor})"
        )


# Exemplo de uso (para testes rápidos)
if __name__ == "__main__":
    from datetime import date
    from decimal import Decimal
    
    print("=" * 60)
    print("EstrategiaExato - Exemplo de Uso")
    print("=" * 60)
    print()
    
    # Configurar logging para ver o processo
    logging.basicConfig(level=logging.DEBUG)
    
    # Criar estratégia
    estrategia = EstrategiaExato(tolerancia_dias=3)
    print(f"Estratégia criada: {estrategia}")
    print(f"Prioridade: {estrategia.prioridade}")
    print()
    
    # Criar lançamento de exemplo
    lancamento = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('150.00'),
        descricao="Pagamento Fornecedor XYZ",
        tipo='D'
    )
    
    # Criar comprovantes de exemplo
    comprovantes = [
        Comprovante(
            data=date(2025, 11, 1),
            valor=Decimal('150.00'),
            beneficiario="Fornecedor XYZ"
        ),
        Comprovante(
            data=date(2025, 11, 3),
            valor=Decimal('150.00'),
            beneficiario="Outro Fornecedor"
        ),
        Comprovante(
            data=date(2025, 11, 1),
            valor=Decimal('200.00'),
            beneficiario="Fornecedor ABC"
        ),
    ]
    
    print("Buscando match...")
    print()
    
    # Buscar match
    match = estrategia.encontrar_match(lancamento, comprovantes, set())
    
    if match:
        print("✅ Match encontrado!")
        print(f"   Confiança: {match.confianca:.0%}")
        print(f"   Comprovante: {match.comprovante.beneficiario}")
        print(f"   Valor: R$ {match.comprovante.valor}")
        print(f"   Data: {match.comprovante.data_pagamento}")
    else:
        print("❌ Nenhum match encontrado")
    
    print()
    print("=" * 60)
