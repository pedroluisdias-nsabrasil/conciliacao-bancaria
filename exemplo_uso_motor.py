"""
Exemplo de Uso do MotorConciliacao.

Demonstra casos de uso práticos do motor de conciliação bancária,
mostrando diferentes cenários e funcionalidades.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Created: 04/11/2025
"""

from datetime import date
from decimal import Decimal

from src.modelos import Lancamento, Comprovante
from src.conciliacao.motor import MotorConciliacao, criar_motor_padrao
from src.conciliacao.estrategias import EstrategiaExato


def exemplo_1_uso_basico():
    """
    Exemplo 1: Uso básico do motor.
    
    Demonstra o fluxo mais simples:
    1. Criar motor
    2. Adicionar estratégia
    3. Conciliar
    4. Ver resultados
    """
    print("="*70)
    print("EXEMPLO 1: USO BÁSICO")
    print("="*70)
    
    # 1. Criar motor
    motor = MotorConciliacao()
    
    # 2. Adicionar estratégia
    motor.adicionar_estrategia(EstrategiaExato())
    
    # 3. Criar dados de exemplo
    lancamentos = [
        Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal('1500.00'),
            descricao="PAGAMENTO FORNECEDOR ACME",
            tipo="D",
            saldo=Decimal('10000.00')
        ),
    ]
    
    comprovantes = [
        Comprovante(
            arquivo="comprovante_acme.pdf",
            data=date(2025, 11, 1),
            valor=Decimal('1500.00'),
            beneficiario="ACME LTDA",
            
            confianca_ocr=0.95
        ),
    ]
    
    # 4. Conciliar
    matches = motor.conciliar(lancamentos, comprovantes)
    
    # 5. Ver resultados
    print(f"\n✅ Encontrados {len(matches)} matches")
    
    for match in matches:
        print(f"\nMatch:")
        print(f"  Lançamento: {match.lancamento.descricao}")
        print(f"  Comprovante: {match.comprovante.arquivo}")
        print(f"  Confiança: {match.confianca:.1%}")
        print(f"  Auto-aprovado: {'Sim' if match.confianca >= 0.90 else 'Não'}")


def exemplo_2_multiplas_estrategias():
    """
    Exemplo 2: Múltiplas estratégias.
    
    Demonstra como usar múltiplas estratégias em ordem de prioridade.
    """
    print("\n" + "="*70)
    print("EXEMPLO 2: MÚLTIPLAS ESTRATÉGIAS")
    print("="*70)
    
    # Criar motor
    motor = MotorConciliacao()
    
    # Adicionar estratégias (em ordem de prioridade)
    motor.adicionar_estrategia(EstrategiaExato())
    # motor.adicionar_estrategia(EstrategiaFuzzy())  # Sprint 4
    # motor.adicionar_estrategia(EstrategiaAgregado())  # Sprint 4
    
    # Listar estratégias
    estrategias = motor.listar_estrategias()
    print(f"\n✅ Estratégias cadastradas: {len(estrategias)}")
    
    for e in estrategias:
        print(f"  • {e['nome']} (prioridade: {e['prioridade']})")


def exemplo_3_estatisticas():
    """
    Exemplo 3: Estatísticas detalhadas.
    
    Demonstra como gerar e interpretar estatísticas de conciliação.
    """
    print("\n" + "="*70)
    print("EXEMPLO 3: ESTATÍSTICAS DETALHADAS")
    print("="*70)
    
    # Criar motor e conciliar
    motor = MotorConciliacao()
    motor.adicionar_estrategia(EstrategiaExato())
    
    # Dados de exemplo
    lancamentos = [
        Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal('100.00'),
            descricao="PAGAMENTO A",
            tipo="D",
            saldo=Decimal('1000.00')
        ),
        Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('200.00'),
            descricao="PAGAMENTO B",
            tipo="D",
            saldo=Decimal('900.00')
        ),
        Lancamento(
            data=date(2025, 11, 3),
            valor=Decimal('300.00'),
            descricao="PAGAMENTO C",
            tipo="D",
            saldo=Decimal('700.00')
        ),
    ]
    
    comprovantes = [
        Comprovante(
            arquivo="comp_a.pdf",
            data=date(2025, 11, 1),
            valor=Decimal('100.00'),
            beneficiario="FORNECEDOR A",
            
            confianca_ocr=0.95
        ),
        Comprovante(
            arquivo="comp_b.pdf",
            data=date(2025, 11, 2),
            valor=Decimal('200.00'),
            beneficiario="FORNECEDOR B",
            
            confianca_ocr=0.88
        ),
    ]
    
    matches = motor.conciliar(lancamentos, comprovantes)
    
    # Gerar estatísticas
    stats = motor.gerar_estatisticas(matches, lancamentos)
    
    print(f"\n✅ Estatísticas:")
    print(f"  • Lançamentos processados: {stats['total_lancamentos']}")
    print(f"  • Matches encontrados: {stats['total_matches']}")
    print(f"  • Taxa de conciliação: {stats['taxa_conciliacao']:.1%}")
    print(f"  • Confiança média: {stats['confianca_media']:.1%}")
    print(f"  • Auto-aprovados: {stats['auto_aprovados']}")
    print(f"  • Requerem revisão: {stats['requer_revisao']}")
    print(f"  • Valor conciliado: R$ {stats['valor_total_conciliado']:,.2f}")
    
    if stats['por_metodo']:
        print(f"\n  Por método:")
        for metodo, count in stats['por_metodo'].items():
            print(f"    - {metodo}: {count}")
    
    print(f"\n  Por faixa de confiança:")
    print(f"    - Alta (≥90%): {stats['por_confianca']['alta']}")
    print(f"    - Média (70-90%): {stats['por_confianca']['media']}")
    print(f"    - Baixa (60-70%): {stats['por_confianca']['baixa']}")


def exemplo_4_relatorios():
    """
    Exemplo 4: Geração de relatórios.
    
    Demonstra como gerar relatórios em diferentes formatos.
    """
    print("\n" + "="*70)
    print("EXEMPLO 4: RELATÓRIOS")
    print("="*70)
    
    # Criar motor e conciliar
    motor = MotorConciliacao()
    motor.adicionar_estrategia(EstrategiaExato())
    
    # Dados de exemplo
    lancamentos = [
        Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal('500.00'),
            descricao="PAGAMENTO TESTE",
            tipo="D",
            saldo=Decimal('5000.00')
        ),
    ]
    
    comprovantes = [
        Comprovante(
            arquivo="comprovante.pdf",
            data=date(2025, 11, 1),
            valor=Decimal('500.00'),
            beneficiario="FORNECEDOR",
            
            confianca_ocr=0.95
        ),
    ]
    
    matches = motor.conciliar(lancamentos, comprovantes)
    
    # Relatório em texto
    print("\n📄 RELATÓRIO EM TEXTO:")
    print("-" * 70)
    relatorio_texto = motor.gerar_relatorio(matches, lancamentos, formato="texto")
    print(relatorio_texto)
    
    # Relatório em markdown
    print("\n📄 RELATÓRIO EM MARKDOWN:")
    print("-" * 70)
    relatorio_md = motor.gerar_relatorio(matches, lancamentos, formato="markdown")
    print(relatorio_md)


def exemplo_5_filtros():
    """
    Exemplo 5: Conciliação com filtros.
    
    Demonstra como usar filtros personalizados.
    """
    print("\n" + "="*70)
    print("EXEMPLO 5: FILTROS PERSONALIZADOS")
    print("="*70)
    
    # Criar motor
    motor = MotorConciliacao()
    motor.adicionar_estrategia(EstrategiaExato())
    
    # Dados de exemplo
    lancamentos = [
        Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal('50.00'),
            descricao="PAGAMENTO PEQUENO",
            tipo="D",
            saldo=Decimal('5000.00')
        ),
        Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('5000.00'),
            descricao="PAGAMENTO GRANDE",
            tipo="D",
            saldo=Decimal('4950.00')
        ),
    ]
    
    comprovantes = [
        Comprovante(
            arquivo="comp_pequeno.pdf",
            data=date(2025, 11, 1),
            valor=Decimal('50.00'),
            beneficiario="FORNECEDOR A",
            
            confianca_ocr=0.95
        ),
        Comprovante(
            arquivo="comp_grande.pdf",
            data=date(2025, 11, 2),
            valor=Decimal('5000.00'),
            beneficiario="FORNECEDOR B",
            
            confianca_ocr=0.95
        ),
    ]
    
    # Conciliar apenas lançamentos > R$ 1000
    print("\n🔍 Filtro: Apenas lançamentos > R$ 1.000,00")
    
    filtro_valor_alto = lambda l: l.valor > Decimal('1000')
    
    matches = motor.conciliar_com_filtros(
        lancamentos,
        comprovantes,
        filtro_lancamento=filtro_valor_alto
    )
    
    print(f"✅ Encontrados {len(matches)} matches")
    
    for match in matches:
        print(f"\nMatch:")
        print(f"  Valor: R$ {match.lancamento.valor:,.2f}")
        print(f"  Descrição: {match.lancamento.descricao}")


def exemplo_6_configuracao_customizada():
    """
    Exemplo 6: Configuração customizada.
    
    Demonstra como usar configurações personalizadas.
    """
    print("\n" + "="*70)
    print("EXEMPLO 6: CONFIGURAÇÃO CUSTOMIZADA")
    print("="*70)
    
    # Configuração customizada
    config = {
        "confianca_minima": 0.70,        # Aumentar mínimo para 70%
        "confianca_auto_aprovar": 0.95,  # Auto-aprovar apenas >95%
    }
    
    motor = MotorConciliacao(config=config)
    motor.adicionar_estrategia(EstrategiaExato())
    
    print(f"\n✅ Motor criado com configuração customizada:")
    print(f"  • Confiança mínima: {motor.config['confianca_minima']:.1%}")
    print(f"  • Auto-aprovar: {motor.config['confianca_auto_aprovar']:.1%}")


def exemplo_7_performance():
    """
    Exemplo 7: Monitoramento de performance.
    
    Demonstra como monitorar performance do motor.
    """
    print("\n" + "="*70)
    print("EXEMPLO 7: PERFORMANCE")
    print("="*70)
    
    motor = MotorConciliacao()
    motor.adicionar_estrategia(EstrategiaExato())
    
    # Criar dados de exemplo
    lancamentos = [
        Lancamento(
            data=date(2025, 11, 1),
            valor=Decimal('100.00'),
            descricao=f"PAGAMENTO {i}",
            tipo="D",
            saldo=Decimal('10000.00')
        )
        for i in range(10)  # 10 lançamentos
    ]
    
    comprovantes = [
        Comprovante(
            arquivo=f"comp_{i}.pdf",
            data=date(2025, 11, 1),
            valor=Decimal('100.00'),
            beneficiario=f"FORNECEDOR {i}",
            
            confianca_ocr=0.95
        )
        for i in range(10)  # 10 comprovantes
    ]
    
    # Conciliar
    matches = motor.conciliar(lancamentos, comprovantes)
    
    # Obter métricas de performance
    perf = motor.obter_performance()
    
    print(f"\n✅ Métricas de performance:")
    print(f"  • Total de conciliações: {perf['total_conciliacoes']}")
    print(f"  • Tempo total: {perf['tempo_total']:.3f}s")
    print(f"  • Tempo médio: {perf['tempo_medio']:.3f}s")
    print(f"  • Throughput: {len(lancamentos)/perf['tempo_total']:.1f} lançamentos/s")


def exemplo_8_factory():
    """
    Exemplo 8: Usando factory.
    
    Demonstra como usar a função factory para criar motor padrão.
    """
    print("\n" + "="*70)
    print("EXEMPLO 8: FACTORY (MOTOR PADRÃO)")
    print("="*70)
    
    # Criar motor padrão (já vem com EstrategiaExato)
    motor = criar_motor_padrao()
    
    estrategias = motor.listar_estrategias()
    
    print(f"\n✅ Motor padrão criado")
    print(f"  • Estratégias: {len(estrategias)}")
    
    for e in estrategias:
        print(f"    - {e['nome']}")


def main():
    """Executa todos os exemplos."""
    print("\n")
    print("█" * 70)
    print("  EXEMPLOS DE USO DO MOTOR DE CONCILIAÇÃO")
    print("█" * 70)
    
    exemplos = [
        exemplo_1_uso_basico,
        exemplo_2_multiplas_estrategias,
        exemplo_3_estatisticas,
        exemplo_4_relatorios,
        exemplo_5_filtros,
        exemplo_6_configuracao_customizada,
        exemplo_7_performance,
        exemplo_8_factory,
    ]
    
    for exemplo in exemplos:
        try:
            exemplo()
        except Exception as e:
            print(f"\n❌ Erro no exemplo: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "█" * 70)
    print("  FIM DOS EXEMPLOS")
    print("█" * 70 + "\n")


if __name__ == "__main__":
    main()
