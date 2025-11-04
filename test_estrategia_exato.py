"""
Teste Rápido da EstrategiaExato

Script para testar a instalação e funcionalidade da EstrategiaExato.
Execute após instalar o arquivo exato.py.

Autor: Pedro Luis (pedroluisdias@br-nsa.com)
Data: 03/11/2025
"""

import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

# Garantir que src está no path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def teste_importacao():
    """Testa se a EstrategiaExato pode ser importada."""
    print("\n" + "="*60)
    print("TESTE 1: Importação")
    print("="*60)
    
    try:
        from src.conciliacao.estrategias import EstrategiaExato
        print("✅ EstrategiaExato importada com sucesso!")
        return True, EstrategiaExato
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
        print("\nVerifique:")
        print("  1. Arquivo exato.py está em src/conciliacao/estrategias/")
        print("  2. __init__.py foi atualizado com 'from .exato import EstrategiaExato'")
        return False, None


def teste_criacao(EstrategiaExato):
    """Testa criação da estratégia com parâmetros padrão."""
    print("\n" + "="*60)
    print("TESTE 2: Criação da Estratégia")
    print("="*60)
    
    try:
        estrategia = EstrategiaExato()
        print(f"✅ Estratégia criada: {estrategia}")
        print(f"   Nome: {estrategia.nome}")
        print(f"   Prioridade: {estrategia.prioridade}")
        print(f"   Tolerância dias: {estrategia.tolerancia_dias}")
        print(f"   Tolerância valor: R$ {estrategia.tolerancia_valor}")
        return True, estrategia
    except Exception as e:
        print(f"❌ Erro ao criar estratégia: {e}")
        return False, None


def teste_validacoes(EstrategiaExato):
    """Testa validações de parâmetros."""
    print("\n" + "="*60)
    print("TESTE 3: Validações")
    print("="*60)
    
    testes_validacao = [
        ("Tolerância dias negativa", {"tolerancia_dias": -1}, True),
        ("Tolerância dias muito alta", {"tolerancia_dias": 15}, True),
        ("Tolerância valor negativa", {"tolerancia_valor": Decimal('-1.0')}, True),
        ("Similaridade inválida", {"min_similaridade_descricao": 1.5}, True),
        ("Parâmetros válidos", {"tolerancia_dias": 5}, False),
    ]
    
    todos_passaram = True
    for nome, params, deve_falhar in testes_validacao:
        try:
            estrategia = EstrategiaExato(**params)
            if deve_falhar:
                print(f"  ❌ {nome} - Deveria ter falhado mas não falhou")
                todos_passaram = False
            else:
                print(f"  ✅ {nome} - OK")
        except (ValueError, Exception) as e:
            if deve_falhar:
                print(f"  ✅ {nome} - Falhou como esperado")
            else:
                print(f"  ❌ {nome} - Falhou inesperadamente: {e}")
                todos_passaram = False
    
    if todos_passaram:
        print("✅ Todas as validações funcionaram corretamente!")
    
    return todos_passaram


def teste_matching_simples(estrategia):
    """Testa matching com casos simples."""
    print("\n" + "="*60)
    print("TESTE 4: Matching Simples")
    print("="*60)
    
    from src.modelos import Lancamento, Comprovante
    
    # Caso 1: Match perfeito
    print("\n📝 Caso 1: Match Perfeito")
    lancamento1 = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('150.00'),
        descricao="Pagamento Fornecedor",
        tipo='D'
    )
    
    comprovante1 = Comprovante(
        arquivo="comp1.pdf",
        data=date(2025, 11, 1),
        valor=Decimal('150.00'),
        beneficiario="Fornecedor ABC"
    )
    
    match1 = estrategia.encontrar_match(lancamento1, [comprovante1], set())
    
    if match1 and match1.confianca >= 0.80:
        print(f"  ✅ Match encontrado! Confiança: {match1.confianca:.0%}")
    else:
        print(f"  ❌ Match não encontrado ou confiança baixa")
        return False
    
    # Caso 2: Datas diferentes mas dentro da tolerância
    print("\n📝 Caso 2: Datas Diferentes (±2 dias)")
    lancamento2 = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('200.00'),
        descricao="Outro Pagamento",
        tipo='D'
    )
    
    comprovante2 = Comprovante(
        arquivo="comp2.pdf",
        data=date(2025, 11, 3),  # 2 dias depois
        valor=Decimal('200.00'),
        beneficiario="Outro Fornecedor"
    )
    
    match2 = estrategia.encontrar_match(lancamento2, [comprovante2], set())
    
    if match2 and 0.60 <= match2.confianca < 0.90:
        print(f"  ✅ Match encontrado! Confiança: {match2.confianca:.0%}")
    else:
        print(f"  ❌ Match não encontrado ou confiança fora do esperado")
        return False
    
    # Caso 3: Sem match (data fora da tolerância)
    print("\n📝 Caso 3: Sem Match (data muito distante)")
    lancamento3 = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('300.00'),
        descricao="Terceiro Pagamento",
        tipo='D'
    )
    
    comprovante3 = Comprovante(
        arquivo="comp3.pdf",
        data=date(2025, 11, 10),  # 9 dias depois
        valor=Decimal('300.00'),
        beneficiario="Terceiro Fornecedor"
    )
    
    match3 = estrategia.encontrar_match(lancamento3, [comprovante3], set())
    
    if match3 is None:
        print(f"  ✅ Nenhum match (correto - data fora da tolerância)")
    else:
        print(f"  ❌ Match encontrado mas não deveria (data muito distante)")
        return False
    
    # Caso 4: Valores diferentes
    print("\n📝 Caso 4: Sem Match (valores diferentes)")
    lancamento4 = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('100.00'),
        descricao="Quarto Pagamento",
        tipo='D'
    )
    
    comprovante4 = Comprovante(
        arquivo="comp4.pdf",
        data=date(2025, 11, 1),
        valor=Decimal('999.00'),  # Valor diferente
        beneficiario="Quarto Fornecedor"
    )
    
    match4 = estrategia.encontrar_match(lancamento4, [comprovante4], set())
    
    if match4 is None:
        print(f"  ✅ Nenhum match (correto - valores diferentes)")
    else:
        print(f"  ❌ Match encontrado mas não deveria (valores diferentes)")
        return False
    
    print("\n✅ Todos os casos de matching passaram!")
    return True


def teste_usados(estrategia):
    """Testa controle de comprovantes já usados."""
    print("\n" + "="*60)
    print("TESTE 5: Controle de Comprovantes Usados")
    print("="*60)
    
    from src.modelos import Lancamento, Comprovante
    
    lancamento = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('150.00'),
        descricao="Pagamento",
        tipo='D'
    )
    
    comprovante = Comprovante(
        arquivo="comp_teste.pdf",
        data=date(2025, 11, 1),
        valor=Decimal('150.00'),
        beneficiario="Fornecedor"
    )
    
    # Primeira vez: deve encontrar
    usados = set()
    match1 = estrategia.encontrar_match(lancamento, [comprovante], usados)
    
    if match1:
        print("  ✅ Primeira busca encontrou match")
        
        # Marcar como usado
        usados.add(id(match1.comprovante))
        
        # Segunda vez: não deve encontrar (já usado)
        match2 = estrategia.encontrar_match(lancamento, [comprovante], usados)
        
        if match2 is None:
            print("  ✅ Segunda busca não encontrou (comprovante já usado)")
            return True
        else:
            print("  ❌ Segunda busca encontrou mas não deveria")
            return False
    else:
        print("  ❌ Primeira busca não encontrou match")
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🧪 TESTE RÁPIDO - ESTRATÉGIA EXATO")
    print("Sistema de Conciliação Bancária - Sprint 3")
    print("="*60)
    
    resultados = []
    
    # Teste 1: Importação
    sucesso, EstrategiaExato = teste_importacao()
    resultados.append(("Importação", sucesso))
    
    if not sucesso:
        print("\n❌ Testes interrompidos - corrija a importação primeiro")
        return 1
    
    # Teste 2: Criação
    sucesso, estrategia = teste_criacao(EstrategiaExato)
    resultados.append(("Criação", sucesso))
    
    if not sucesso:
        print("\n❌ Testes interrompidos - corrija a criação primeiro")
        return 1
    
    # Teste 3: Validações
    sucesso = teste_validacoes(EstrategiaExato)
    resultados.append(("Validações", sucesso))
    
    # Teste 4: Matching
    sucesso = teste_matching_simples(estrategia)
    resultados.append(("Matching Simples", sucesso))
    
    # Teste 5: Usados
    sucesso = teste_usados(estrategia)
    resultados.append(("Controle de Usados", sucesso))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    total = len(resultados)
    passou = sum(1 for _, resultado in resultados if resultado)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {status} - {nome}")
    
    print("="*60)
    print(f"Resultado: {passou}/{total} testes passaram")
    print("="*60)
    
    if passou == total:
        print("\n🎉 PARABÉNS! EstrategiaExato funcionando perfeitamente!")
        print("\nPróximos passos:")
        print("  1. Implementar MotorConciliacao")
        print("  2. Criar testes completos")
        print("  3. Integrar com interface")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
