"""
Exemplo de uso do Leitor CSV.

Este script demonstra como usar o LeitorCSV para ler extratos bancários.
"""

from src.ingestao import LeitorCSV
from decimal import Decimal


def exemplo_basico():
    """Exemplo básico de leitura de extrato."""
    print("=" * 60)
    print("EXEMPLO 1: Leitura Básica")
    print("=" * 60)

    # Criar leitor
    leitor = LeitorCSV()

    # Ler arquivo
    arquivo = "tests/fixtures/extratos_exemplo/extrato_itau.csv"
    lancamentos = leitor.ler_arquivo(arquivo)

    # Exibir resumo
    print(f"\n✓ Arquivo lido com sucesso!")
    print(f"✓ {len(lancamentos)} lançamentos extraídos\n")

    # Exibir primeiros 3 lançamentos
    print("Primeiros 3 lançamentos:")
    print("-" * 60)
    for i, lanc in enumerate(lancamentos[:3], 1):
        print(f"\n{i}. {lanc.data.strftime('%d/%m/%Y')}")
        print(f"   Valor: R$ {lanc.valor:,.2f}")
        print(f"   Tipo: {'Débito' if lanc.tipo == 'D' else 'Crédito'}")
        print(f"   Descrição: {lanc.descricao}")


def exemplo_resumo():
    """Exemplo de obtenção de resumo do arquivo."""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Resumo do Arquivo")
    print("=" * 60)

    leitor = LeitorCSV()
    arquivo = "tests/fixtures/extratos_exemplo/extrato_itau.csv"
    lancamentos = leitor.ler_arquivo(arquivo)

    resumo = leitor.obter_resumo()

    print(f"\nBanco detectado: {resumo['banco_detectado'].upper()}")
    print(f"Total de linhas: {resumo['total_linhas']}")
    print(f"Colunas encontradas: {', '.join(resumo['colunas'])}")


def exemplo_estatisticas():
    """Exemplo de cálculo de estatísticas."""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Estatísticas")
    print("=" * 60)

    leitor = LeitorCSV()
    arquivo = "tests/fixtures/extratos_exemplo/extrato_itau.csv"
    lancamentos = leitor.ler_arquivo(arquivo)

    # Separar por tipo
    debitos = [l for l in lancamentos if l.tipo == "D"]
    creditos = [l for l in lancamentos if l.tipo == "C"]

    # Calcular totais
    total_debitos = sum(l.valor for l in debitos)
    total_creditos = sum(l.valor for l in creditos)
    saldo = total_creditos - total_debitos

    print(f"\n{'Débitos:':<20} {len(debitos):>3} lançamentos")
    print(f"{'Total Débitos:':<20} R$ {total_debitos:>12,.2f}")
    print()
    print(f"{'Créditos:':<20} {len(creditos):>3} lançamentos")
    print(f"{'Total Créditos:':<20} R$ {total_creditos:>12,.2f}")
    print("-" * 40)
    print(f"{'Saldo Líquido:':<20} R$ {saldo:>12,.2f}")


def exemplo_banco_especifico():
    """Exemplo forçando banco específico."""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Forçar Banco Específico")
    print("=" * 60)

    # Forçar formato Itaú
    leitor = LeitorCSV(banco="itau")
    arquivo = "tests/fixtures/extratos_exemplo/extrato_itau.csv"
    lancamentos = leitor.ler_arquivo(arquivo)

    print(f"\n✓ Formato forçado: {leitor.banco.upper()}")
    print(f"✓ {len(lancamentos)} lançamentos lidos")


def exemplo_tratamento_erro():
    """Exemplo de tratamento de erros."""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Tratamento de Erros")
    print("=" * 60)

    from src.ingestao.leitor_csv import ArquivoInvalidoError

    leitor = LeitorCSV()

    # Tentar ler arquivo inexistente
    try:
        leitor.ler_arquivo("arquivo_que_nao_existe.csv")
    except ArquivoInvalidoError as e:
        print(f"\n✓ Erro capturado corretamente:")
        print(f"  {e}")


def exemplo_extrato_generico():
    """Exemplo com extrato genérico."""
    print("\n" + "=" * 60)
    print("EXEMPLO 6: Extrato Genérico (sem coluna tipo)")
    print("=" * 60)

    leitor = LeitorCSV()
    arquivo = "tests/fixtures/extratos_exemplo/extrato_generico.csv"
    lancamentos = leitor.ler_arquivo(arquivo)

    print(f"\n✓ {len(lancamentos)} lançamentos lidos")
    print("\nTipos identificados automaticamente:")
    print("-" * 60)

    for lanc in lancamentos:
        tipo_desc = "Débito" if lanc.tipo == "D" else "Crédito"
        print(f"{lanc.data.strftime('%d/%m/%Y')} | {tipo_desc:8} | {lanc.descricao}")


if __name__ == "__main__":
    print("\n")
    print("🏦" * 30)
    print("  EXEMPLOS DE USO DO LEITOR CSV")
    print("🏦" * 30)

    try:
        exemplo_basico()
        exemplo_resumo()
        exemplo_estatisticas()
        exemplo_banco_especifico()
        exemplo_tratamento_erro()
        exemplo_extrato_generico()

        print("\n" + "=" * 60)
        print("✅ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("=" * 60)
        print()

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
