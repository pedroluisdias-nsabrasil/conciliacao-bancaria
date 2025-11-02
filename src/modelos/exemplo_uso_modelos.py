"""
Exemplo de Uso dos Modelos de Dados.

Este script demonstra como usar os modelos Lancamento, Comprovante e Match
de forma prática.

Para executar:
    python exemplo_uso_modelos.py

Author: Pedro Luis
Date: 02/11/2025
"""

from datetime import date
from decimal import Decimal
from src.modelos.lancamento import Lancamento
from src.modelos.comprovante import Comprovante
from src.modelos.match import Match


def exemplo_basico():
    """Exemplo básico de criação e uso dos modelos."""
    print("=" * 70)
    print("EXEMPLO 1: Criação Básica dos Modelos")
    print("=" * 70)
    
    # 1. Criar um lançamento bancário (débito)
    print("\n1. Criando lançamento bancário (pagamento)...")
    lancamento = Lancamento(
        data=date(2025, 11, 2),
        valor=Decimal('150.50'),
        descricao='Pagamento Fornecedor ABC Ltda',
        tipo='D',
        documento='DOC 12345'
    )
    print(f"   ✓ {lancamento}")
    
    # 2. Criar um comprovante
    print("\n2. Criando comprovante de pagamento...")
    comprovante = Comprovante(
        arquivo='comprovantes/nf_001_fornecedor_abc.pdf',
        data=date(2025, 11, 2),
        valor=Decimal('150.50'),
        beneficiario='Fornecedor ABC Ltda',
        tipo_documento='Nota Fiscal',
        numero_documento='NF-123456',
        confianca_ocr=0.95
    )
    print(f"   ✓ {comprovante}")
    
    # 3. Criar um match
    print("\n3. Criando match entre lançamento e comprovante...")
    match = Match(
        lancamento=lancamento,
        comprovante=comprovante,
        confianca=0.98,
        metodo='exato',
        observacoes='Valor e data exatos, beneficiário similar'
    )
    print(f"   ✓ {match}")
    print(f"   • Nível de confiança: {match.nivel_confianca}")
    print(f"   • Requer revisão? {match.requer_revisao}")
    print(f"   • Pode auto-aprovar? {match.pode_auto_aprovar}")


def exemplo_credito_debito():
    """Exemplo mostrando diferença entre crédito e débito."""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 2: Lançamentos de Crédito vs Débito")
    print("=" * 70)
    
    # Débito (saída de dinheiro)
    print("\n1. Débito (saída de dinheiro):")
    debito = Lancamento(
        data=date.today(),
        valor=Decimal('500.00'),
        descricao='Pagamento de fornecedor',
        tipo='D'
    )
    print(f"   Tipo: {debito.tipo_descritivo}")
    print(f"   Valor absoluto: R$ {debito.valor}")
    print(f"   Valor com sinal: R$ {debito.valor_com_sinal}")
    
    # Crédito (entrada de dinheiro)
    print("\n2. Crédito (entrada de dinheiro):")
    credito = Lancamento(
        data=date.today(),
        valor=Decimal('1000.00'),
        descricao='Recebimento de cliente',
        tipo='C'
    )
    print(f"   Tipo: {credito.tipo_descritivo}")
    print(f"   Valor absoluto: R$ {credito.valor}")
    print(f"   Valor com sinal: R$ {credito.valor_com_sinal}")


def exemplo_niveis_confianca():
    """Exemplo mostrando diferentes níveis de confiança."""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 3: Diferentes Níveis de Confiança")
    print("=" * 70)
    
    lancamento = Lancamento(
        data=date.today(),
        valor=Decimal('100.00'),
        descricao='Pagamento teste',
        tipo='D'
    )
    
    # Match com alta confiança
    print("\n1. Match com ALTA confiança (>= 0.9):")
    match_alto = Match(
        lancamento=lancamento,
        comprovante=None,
        confianca=0.95,
        metodo='exato'
    )
    print(f"   Confiança: {match_alto.confianca:.0%}")
    print(f"   Nível: {match_alto.nivel_confianca}")
    print(f"   Cor: {match_alto.cor_confianca}")
    print(f"   Requer revisão? {match_alto.requer_revisao}")
    print(f"   Pode auto-aprovar? {match_alto.pode_auto_aprovar}")
    
    # Match com média confiança
    print("\n2. Match com MÉDIA confiança (0.7 - 0.9):")
    match_medio = Match(
        lancamento=lancamento,
        comprovante=None,
        confianca=0.80,
        metodo='fuzzy'
    )
    print(f"   Confiança: {match_medio.confianca:.0%}")
    print(f"   Nível: {match_medio.nivel_confianca}")
    print(f"   Cor: {match_medio.cor_confianca}")
    print(f"   Requer revisão? {match_medio.requer_revisao}")
    print(f"   Pode auto-aprovar? {match_medio.pode_auto_aprovar}")
    
    # Match com baixa confiança
    print("\n3. Match com BAIXA confiança (< 0.7):")
    match_baixo = Match(
        lancamento=lancamento,
        comprovante=None,
        confianca=0.60,
        metodo='fuzzy'
    )
    print(f"   Confiança: {match_baixo.confianca:.0%}")
    print(f"   Nível: {match_baixo.nivel_confianca}")
    print(f"   Cor: {match_baixo.cor_confianca}")
    print(f"   Requer revisão? {match_baixo.requer_revisao}")
    print(f"   Pode auto-aprovar? {match_baixo.pode_auto_aprovar}")


def exemplo_conciliacao_workflow():
    """Exemplo completo de workflow de conciliação."""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 4: Workflow Completo de Conciliação")
    print("=" * 70)
    
    # 1. Criar lançamento e comprovante
    print("\n1. Criando lançamento e comprovante...")
    lancamento = Lancamento(
        data=date(2025, 11, 2),
        valor=Decimal('250.00'),
        descricao='Pagamento Material Escritório',
        tipo='D'
    )
    
    comprovante = Comprovante(
        arquivo='nf_escritorio.pdf',
        data=date(2025, 11, 2),
        valor=Decimal('250.00'),
        beneficiario='Papelaria XPTO',
        confianca_ocr=0.92
    )
    
    print(f"   Lançamento conciliado? {lancamento.conciliado}")
    print(f"   Comprovante conciliado? {comprovante.conciliado}")
    
    # 2. Criar match
    print("\n2. Criando match...")
    match = Match(
        lancamento=lancamento,
        comprovante=comprovante,
        confianca=0.93,
        metodo='exato'
    )
    print(f"   Match criado com confiança de {match.confianca:.0%}")
    print(f"   Status: {match.nivel_confianca} confiança")
    
    # 3. Confirmar match
    print("\n3. Confirmando match...")
    match.confirmar(usuario='Pedro Luis')
    print(f"   ✓ Match confirmado por: {match.usuario}")
    print(f"   ✓ Lançamento conciliado? {lancamento.conciliado}")
    print(f"   ✓ Comprovante conciliado? {comprovante.conciliado}")
    
    # 4. Desfazer (se necessário)
    print("\n4. Desfazendo match (exemplo de correção)...")
    match.desfazer()
    print(f"   ✓ Match desfeito")
    print(f"   ✓ Lançamento conciliado? {lancamento.conciliado}")
    print(f"   ✓ Comprovante conciliado? {comprovante.conciliado}")


def exemplo_match_regra():
    """Exemplo de match por regra (sem comprovante)."""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 5: Match por Regra (Tarifa Bancária)")
    print("=" * 70)
    
    # Lançamento de tarifa bancária
    print("\n1. Lançamento de tarifa bancária detectado...")
    tarifa = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('15.90'),
        descricao='Tarifa pacote serviços',
        tipo='D'
    )
    print(f"   {tarifa}")
    
    # Match automático por regra (sem comprovante)
    print("\n2. Aplicando regra de auto-conciliação...")
    match_tarifa = Match(
        lancamento=tarifa,
        comprovante=None,  # Sem comprovante necessário
        confianca=1.0,     # 100% de confiança para regra
        metodo='regra',
        observacoes='Tarifa bancária identificada automaticamente'
    )
    
    print(f"   ✓ {match_tarifa}")
    print(f"   • Método: {match_tarifa.metodo}")
    print(f"   • Observação: {match_tarifa.observacoes}")
    print(f"   • Pode auto-aprovar? {match_tarifa.pode_auto_aprovar}")


def exemplo_conversao_dict():
    """Exemplo de conversão para dicionário."""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 6: Conversão para Dicionário (Serialização)")
    print("=" * 70)
    
    lancamento = Lancamento(
        data=date(2025, 11, 2),
        valor=Decimal('100.00'),
        descricao='Teste',
        tipo='D'
    )
    
    print("\n1. Convertendo lançamento para dicionário...")
    dados = lancamento.to_dict()
    print("   Chaves disponíveis:", list(dados.keys()))
    print(f"   Exemplo - valor_com_sinal: {dados['valor_com_sinal']}")
    print(f"   Exemplo - tipo_descritivo: {dados['tipo_descritivo']}")


def main():
    """Função principal que executa todos os exemplos."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  EXEMPLOS DE USO - MODELOS DE DADOS".center(68) + "*")
    print("*" + "  Sistema de Conciliação Bancária".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    try:
        exemplo_basico()
        exemplo_credito_debito()
        exemplo_niveis_confianca()
        exemplo_conciliacao_workflow()
        exemplo_match_regra()
        exemplo_conversao_dict()
        
        print("\n\n" + "=" * 70)
        print("✓ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("=" * 70)
        print("\nPróximos passos:")
        print("1. Execute os testes: pytest test_modelos.py -v")
        print("2. Explore os modelos criando seus próprios exemplos")
        print("3. Comece a implementar os leitores de arquivos (Sprint 1)")
        print()
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
