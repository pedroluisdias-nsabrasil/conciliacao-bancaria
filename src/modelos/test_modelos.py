"""
Testes Unitários para Modelos de Dados.

Este módulo contém testes completos para Lancamento, Comprovante e Match.

Para executar:
    pytest test_modelos.py -v

Author: Pedro Luis
Date: 02/11/2025
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from src.modelos.lancamento import Lancamento, LancamentoError, LancamentoInvalidoError
from src.modelos.comprovante import Comprovante, ComprovanteError, ComprovanteInvalidoError, OCRError
from src.modelos.match import Match, MatchError, MatchInvalidoError, MatchConflitanteError


# ============================================================================
# TESTES PARA LANCAMENTO
# ============================================================================

class TestLancamento:
    """Testes para a classe Lancamento."""
    
    def test_criar_lancamento_valido_debito(self):
        """Deve criar um lançamento de débito válido."""
        lanc = Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('150.50'),
            descricao='Pagamento fornecedor XYZ',
            tipo='D'
        )
        
        assert lanc.data == date(2025, 11, 2)
        assert lanc.valor == Decimal('150.50')
        assert lanc.descricao == 'Pagamento fornecedor XYZ'
        assert lanc.tipo == 'D'
        assert lanc.conciliado == False
    
    def test_criar_lancamento_valido_credito(self):
        """Deve criar um lançamento de crédito válido."""
        lanc = Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal('5000.00'),
            descricao='Recebimento de cliente',
            tipo='C'
        )
        
        assert lanc.tipo == 'C'
        assert lanc.valor == Decimal('5000.00')
    
    def test_tipo_invalido(self):
        """Deve rejeitar tipo diferente de 'D' ou 'C'."""
        with pytest.raises(ValueError, match="Tipo deve ser 'D'.*ou 'C'"):
            Lancamento(
                data=date.today(),
                valor=Decimal('100'),
                descricao='Teste',
                tipo='X'
            )
    
    def test_valor_zero(self):
        """Deve rejeitar valor zero."""
        with pytest.raises(ValueError, match="Valor deve ser positivo"):
            Lancamento(
                data=date.today(),
                valor=Decimal('0'),
                descricao='Teste',
                tipo='D'
            )
    
    def test_valor_negativo(self):
        """Deve rejeitar valor negativo."""
        with pytest.raises(ValueError, match="Valor deve ser positivo"):
            Lancamento(
                data=date.today(),
                valor=Decimal('-50'),
                descricao='Teste',
                tipo='D'
            )
    
    def test_descricao_vazia(self):
        """Deve rejeitar descrição vazia."""
        with pytest.raises(ValueError, match="Descrição não pode estar vazia"):
            Lancamento(
                data=date.today(),
                valor=Decimal('100'),
                descricao='',
                tipo='D'
            )
    
    def test_descricao_apenas_espacos(self):
        """Deve rejeitar descrição com apenas espaços."""
        with pytest.raises(ValueError, match="Descrição não pode estar vazia"):
            Lancamento(
                data=date.today(),
                valor=Decimal('100'),
                descricao='   ',
                tipo='D'
            )
    
    def test_descricao_limpa_espacos_extras(self):
        """Deve limpar espaços extras da descrição."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='  Teste   com    espaços  ',
            tipo='D'
        )
        
        assert lanc.descricao == 'Teste com espaços'
    
    def test_valor_com_sinal_debito(self):
        """Débito deve retornar valor negativo."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        assert lanc.valor_com_sinal == Decimal('-100')
    
    def test_valor_com_sinal_credito(self):
        """Crédito deve retornar valor positivo."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='C'
        )
        
        assert lanc.valor_com_sinal == Decimal('100')
    
    def test_tipo_descritivo_debito(self):
        """Deve retornar 'Débito' para tipo D."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        assert lanc.tipo_descritivo == 'Débito'
    
    def test_tipo_descritivo_credito(self):
        """Deve retornar 'Crédito' para tipo C."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='C'
        )
        
        assert lanc.tipo_descritivo == 'Crédito'
    
    def test_marcar_como_conciliado(self):
        """Deve marcar lançamento como conciliado."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        assert lanc.conciliado == False
        lanc.marcar_como_conciliado()
        assert lanc.conciliado == True
    
    def test_desmarcar_conciliacao(self):
        """Deve desmarcar conciliação."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        lanc.marcar_como_conciliado()
        assert lanc.conciliado == True
        
        lanc.desmarcar_conciliacao()
        assert lanc.conciliado == False
    
    def test_to_dict(self):
        """Deve converter lançamento para dicionário."""
        lanc = Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('150.50'),
            descricao='Teste',
            tipo='D'
        )
        
        dados = lanc.to_dict()
        
        assert dados['data'] == date(2025, 11, 2)
        assert dados['valor'] == Decimal('150.50')
        assert dados['descricao'] == 'Teste'
        assert dados['tipo'] == 'D'
        assert dados['conciliado'] == False
        assert dados['valor_com_sinal'] == Decimal('-150.50')


# ============================================================================
# TESTES PARA COMPROVANTE
# ============================================================================

class TestComprovante:
    """Testes para a classe Comprovante."""
    
    def test_criar_comprovante_valido(self):
        """Deve criar um comprovante válido."""
        comp = Comprovante(
            arquivo='comprovantes/nf_123.pdf',
            data=date(2025, 11, 2),
            valor=Decimal('150.50'),
            beneficiario='Fornecedor XYZ',
            confianca_ocr=0.95
        )
        
        assert comp.arquivo == 'comprovantes/nf_123.pdf'
        assert comp.data == date(2025, 11, 2)
        assert comp.valor == Decimal('150.50')
        assert comp.beneficiario == 'Fornecedor XYZ'
        assert comp.confianca_ocr == 0.95
        assert comp.conciliado == False
    
    def test_arquivo_vazio(self):
        """Deve rejeitar arquivo vazio."""
        with pytest.raises(ValueError, match="Caminho do arquivo não pode estar vazio"):
            Comprovante(
                arquivo='',
                data=date.today(),
                valor=Decimal('100')
            )
    
    def test_valor_zero(self):
        """Deve rejeitar valor zero."""
        with pytest.raises(ValueError, match="Valor deve ser positivo"):
            Comprovante(
                arquivo='teste.pdf',
                data=date.today(),
                valor=Decimal('0')
            )
    
    def test_confianca_ocr_invalida_negativa(self):
        """Deve rejeitar confiança OCR negativa."""
        with pytest.raises(ValueError, match="Confiança OCR deve estar entre 0.0 e 1.0"):
            Comprovante(
                arquivo='teste.pdf',
                data=date.today(),
                valor=Decimal('100'),
                confianca_ocr=-0.1
            )
    
    def test_confianca_ocr_invalida_maior_que_1(self):
        """Deve rejeitar confiança OCR maior que 1."""
        with pytest.raises(ValueError, match="Confiança OCR deve estar entre 0.0 e 1.0"):
            Comprovante(
                arquivo='teste.pdf',
                data=date.today(),
                valor=Decimal('100'),
                confianca_ocr=1.5
            )
    
    def test_nome_arquivo(self):
        """Deve extrair nome do arquivo corretamente."""
        comp = Comprovante(
            arquivo='dados/entrada/comprovantes/nf_123.pdf',
            data=date.today(),
            valor=Decimal('100')
        )
        
        assert comp.nome_arquivo == 'nf_123.pdf'
    
    def test_extensao_arquivo(self):
        """Deve extrair extensão do arquivo corretamente."""
        comp = Comprovante(
            arquivo='nf_123.pdf',
            data=date.today(),
            valor=Decimal('100')
        )
        
        assert comp.extensao_arquivo == '.pdf'
    
    def test_nivel_confianca_alta(self):
        """Confiança >= 0.9 deve retornar 'Alta'."""
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100'),
            confianca_ocr=0.95
        )
        
        assert comp.nivel_confianca_ocr == 'Alta'
    
    def test_nivel_confianca_media(self):
        """Confiança entre 0.7 e 0.9 deve retornar 'Média'."""
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100'),
            confianca_ocr=0.8
        )
        
        assert comp.nivel_confianca_ocr == 'Média'
    
    def test_nivel_confianca_baixa(self):
        """Confiança < 0.7 deve retornar 'Baixa'."""
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100'),
            confianca_ocr=0.5
        )
        
        assert comp.nivel_confianca_ocr == 'Baixa'
    
    def test_cor_confianca_alta(self):
        """Alta confiança deve retornar 'green'."""
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100'),
            confianca_ocr=0.95
        )
        
        assert comp.cor_confianca_ocr == 'green'
    
    def test_tem_boa_qualidade_sim(self):
        """Confiança >= 0.8 deve ter boa qualidade."""
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100'),
            confianca_ocr=0.9
        )
        
        assert comp.tem_boa_qualidade() == True
    
    def test_tem_boa_qualidade_nao(self):
        """Confiança < 0.8 não deve ter boa qualidade."""
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100'),
            confianca_ocr=0.7
        )
        
        assert comp.tem_boa_qualidade() == False
    
    def test_marcar_como_conciliado(self):
        """Deve marcar comprovante como conciliado."""
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100')
        )
        
        assert comp.conciliado == False
        comp.marcar_como_conciliado()
        assert comp.conciliado == True


# ============================================================================
# TESTES PARA MATCH
# ============================================================================

class TestMatch:
    """Testes para a classe Match."""
    
    def test_criar_match_valido(self):
        """Deve criar um match válido."""
        lanc = Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('150.50'),
            descricao='Pagamento XYZ',
            tipo='D'
        )
        
        comp = Comprovante(
            arquivo='nf_123.pdf',
            data=date(2025, 11, 2),
            valor=Decimal('150.50')
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=comp,
            confianca=0.98,
            metodo='exato'
        )
        
        assert match.lancamento == lanc
        assert match.comprovante == comp
        assert match.confianca == 0.98
        assert match.metodo == 'exato'
        assert match.confirmado == False
    
    def test_match_sem_comprovante(self):
        """Deve criar match sem comprovante (regra)."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('10.50'),
            descricao='Tarifa bancária',
            tipo='D'
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=None,
            confianca=1.0,
            metodo='regra',
            observacoes='Tarifa automática'
        )
        
        assert match.comprovante is None
        assert match.metodo == 'regra'
    
    def test_confianca_invalida_negativa(self):
        """Deve rejeitar confiança negativa."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        with pytest.raises(ValueError, match="Confiança deve estar entre 0.0 e 1.0"):
            Match(
                lancamento=lanc,
                comprovante=None,
                confianca=-0.5,
                metodo='exato'
            )
    
    def test_metodo_invalido(self):
        """Deve rejeitar método inválido."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        with pytest.raises(ValueError, match="Método deve ser um dos seguintes"):
            Match(
                lancamento=lanc,
                comprovante=None,
                confianca=0.9,
                metodo='invalido'
            )
    
    def test_nivel_confianca_alta(self):
        """Confiança >= 0.9 deve retornar 'Alta'."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=None,
            confianca=0.95,
            metodo='exato'
        )
        
        assert match.nivel_confianca == 'Alta'
    
    def test_requer_revisao_baixa_confianca(self):
        """Match com confiança < 0.9 requer revisão."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=None,
            confianca=0.75,
            metodo='fuzzy'
        )
        
        assert match.requer_revisao == True
    
    def test_requer_revisao_alta_confianca(self):
        """Match com confiança >= 0.9 não requer revisão."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=None,
            confianca=0.95,
            metodo='exato'
        )
        
        assert match.requer_revisao == False
    
    def test_pode_auto_aprovar_sim(self):
        """Confiança >= 0.9 pode auto-aprovar."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=None,
            confianca=0.95,
            metodo='exato'
        )
        
        assert match.pode_auto_aprovar == True
    
    def test_pode_auto_aprovar_nao(self):
        """Confiança < 0.9 não pode auto-aprovar."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=None,
            confianca=0.85,
            metodo='fuzzy'
        )
        
        assert match.pode_auto_aprovar == False
    
    def test_confirmar_match(self):
        """Deve confirmar match e marcar itens como conciliados."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100')
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=comp,
            confianca=0.95,
            metodo='exato'
        )
        
        match.confirmar('Pedro Luis')
        
        assert match.confirmado == True
        assert match.usuario == 'Pedro Luis'
        assert lanc.conciliado == True
        assert comp.conciliado == True
    
    def test_desfazer_match(self):
        """Deve desfazer match e desmarcar conciliação."""
        lanc = Lancamento(
            data=date.today(),
            valor=Decimal('100'),
            descricao='Teste',
            tipo='D'
        )
        
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date.today(),
            valor=Decimal('100')
        )
        
        match = Match(
            lancamento=lanc,
            comprovante=comp,
            confianca=0.95,
            metodo='exato'
        )
        
        match.confirmar()
        assert match.confirmado == True
        
        match.desfazer()
        assert match.confirmado == False
        assert lanc.conciliado == False
        assert comp.conciliado == False


# ============================================================================
# EXECUTAR TESTES
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
