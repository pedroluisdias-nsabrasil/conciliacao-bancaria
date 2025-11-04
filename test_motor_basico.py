"""
Teste Básico do MotorConciliacao.

Script simples para validar que o MotorConciliacao está funcionando
corretamente após instalação no projeto.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Created: 04/11/2025
"""

from datetime import date
from decimal import Decimal

# Imports do projeto
from src.modelos import Lancamento, Comprovante
from src.conciliacao.motor import MotorConciliacao
from src.conciliacao.estrategias import EstrategiaExato


def criar_dados_teste():
    """Cria dados sintéticos para teste."""
    
    # Lançamentos bancários
    lancamentos = [
        Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal('150.00'),
            descricao="PAGAMENTO FORNECEDOR X",
            tipo="D",
            saldo=Decimal('5000.00')
        ),
        Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('250.50'),
            descricao="PAGAMENTO FORNECEDOR Y",
            tipo="D",
            saldo=Decimal('4749.50')
        ),
        Lancamento(
            data=date(2025, 11, 3),
            valor=Decimal('75.30'),
            descricao="TARIFA BANCARIA",
            tipo="D",
            saldo=Decimal('4674.20')
        ),
    ]
    
    # Comprovantes de pagamento
    comprovantes = [
        Comprovante(
            arquivo="comprovante_001.pdf",
            data=date(2025, 11, 1),  # Data exata
            valor=Decimal('150.00'),  # Valor exato
            beneficiario="FORNECEDOR X LTDA",
            
            confianca_ocr=0.95
        ),
        Comprovante(
            arquivo="comprovante_002.pdf",
            data=date(2025, 11, 3),  # Data +1 dia
            valor=Decimal('250.50'),  # Valor exato
            beneficiario="FORNECEDOR Y SA",
            
            confianca_ocr=0.88
        ),
    ]
    
    return lancamentos, comprovantes


def teste_1_criacao_motor():
    """Teste 1: Criação do motor."""
    print("\n" + "="*60)
    print("TESTE 1: Criação do MotorConciliacao")
    print("="*60)
    
    try:
        motor = MotorConciliacao()
        print("✅ Motor criado com sucesso")
        print(f"   Configurações: {motor.config}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar motor: {e}")
        return False


def teste_2_adicionar_estrategia():
    """Teste 2: Adicionar estratégia."""
    print("\n" + "="*60)
    print("TESTE 2: Adicionar Estratégia")
    print("="*60)
    
    try:
        motor = MotorConciliacao()
        estrategia = EstrategiaExato()
        
        motor.adicionar_estrategia(estrategia)
        
        estrategias = motor.listar_estrategias()
        print(f"✅ Estratégia adicionada: {estrategias}")
        print(f"   Total de estratégias: {len(estrategias)}")
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar estratégia: {e}")
        return False


def teste_3_conciliacao_basica():
    """Teste 3: Conciliação básica."""
    print("\n" + "="*60)
    print("TESTE 3: Conciliação Básica")
    print("="*60)
    
    try:
        # Criar motor e adicionar estratégia
        motor = MotorConciliacao()
        motor.adicionar_estrategia(EstrategiaExato())
        
        # Criar dados de teste
        lancamentos, comprovantes = criar_dados_teste()
        
        print(f"   Lançamentos: {len(lancamentos)}")
        print(f"   Comprovantes: {len(comprovantes)}")
        
        # Conciliar
        matches = motor.conciliar(lancamentos, comprovantes)
        
        print(f"✅ Conciliação executada com sucesso")
        print(f"   Matches encontrados: {len(matches)}")
        
        # Mostrar matches
        for i, match in enumerate(matches, 1):
            print(f"\n   Match {i}:")
            print(f"     • Lançamento: {match.lancamento.descricao}")
            print(f"     • Comprovante: {match.comprovante.arquivo}")
            print(f"     • Valor: R$ {match.lancamento.valor}")
            print(f"     • Confiança: {match.confianca:.1%}")
            print(f"     • Método: {match.metodo}")
            
            if match.confianca >= 0.90:
                print(f"     • Status: ✅ AUTO-APROVADO")
            else:
                print(f"     • Status: ⚠️  REQUER REVISÃO")
        
        return True
    except Exception as e:
        print(f"❌ Erro na conciliação: {e}")
        import traceback
        traceback.print_exc()
        return False


def teste_4_estatisticas():
    """Teste 4: Geração de estatísticas."""
    print("\n" + "="*60)
    print("TESTE 4: Estatísticas")
    print("="*60)
    
    try:
        # Criar motor e conciliar
        motor = MotorConciliacao()
        motor.adicionar_estrategia(EstrategiaExato())
        lancamentos, comprovantes = criar_dados_teste()
        matches = motor.conciliar(lancamentos, comprovantes)
        
        # Gerar estatísticas
        stats = motor.gerar_estatisticas(matches, lancamentos)
        
        print("✅ Estatísticas geradas com sucesso:")
        print(f"   • Total de lançamentos: {stats['total_lancamentos']}")
        print(f"   • Total de matches: {stats['total_matches']}")
        print(f"   • Taxa de conciliação: {stats['taxa_conciliacao']:.1%}")
        print(f"   • Confiança média: {stats['confianca_media']:.1%}")
        print(f"   • Auto-aprovados: {stats['auto_aprovados']}")
        print(f"   • Requerem revisão: {stats['requer_revisao']}")
        print(f"   • Valor total: R$ {stats['valor_total_conciliado']:,.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar estatísticas: {e}")
        return False


def teste_5_relatorio():
    """Teste 5: Geração de relatório."""
    print("\n" + "="*60)
    print("TESTE 5: Relatório")
    print("="*60)
    
    try:
        # Criar motor e conciliar
        motor = MotorConciliacao()
        motor.adicionar_estrategia(EstrategiaExato())
        lancamentos, comprovantes = criar_dados_teste()
        matches = motor.conciliar(lancamentos, comprovantes)
        
        # Gerar relatório
        relatorio = motor.gerar_relatorio(matches, lancamentos, formato="texto")
        
        print("✅ Relatório gerado com sucesso:")
        print(relatorio)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("\n")
    print("█" * 60)
    print("  TESTE BÁSICO DO MOTOR DE CONCILIAÇÃO")
    print("█" * 60)
    
    testes = [
        ("Criação do Motor", teste_1_criacao_motor),
        ("Adicionar Estratégia", teste_2_adicionar_estrategia),
        ("Conciliação Básica", teste_3_conciliacao_basica),
        ("Estatísticas", teste_4_estatisticas),
        ("Relatório", teste_5_relatorio),
    ]
    
    resultados = []
    
    for nome, teste in testes:
        resultado = teste()
        resultados.append((nome, resultado))
    
    # Resumo final
    print("\n")
    print("█" * 60)
    print("  RESUMO DOS TESTES")
    print("█" * 60)
    
    total = len(resultados)
    passou = sum(1 for _, r in resultados if r)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {status}  {nome}")
    
    print("\n" + "="*60)
    print(f"  RESULTADO: {passou}/{total} testes passaram")
    
    if passou == total:
        print("  🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("  ⚠️  ALGUNS TESTES FALHARAM")
    
    print("="*60 + "\n")
    
    return passou == total


if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
