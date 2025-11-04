"""
Script de Teste da Estrutura - Sprint 3

Verifica se a estrutura base do motor de conciliação foi instalada corretamente.

Autor: Pedro Luis (pedroluisdias@br-nsa.com)
Data: 03/11/2025
"""

import sys
from pathlib import Path

# Garantir que src está no path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Testa se as importações funcionam."""
    print("\n" + "="*60)
    print("TESTE 1: Importações")
    print("="*60)
    
    try:
        from src.conciliacao import (
            EstrategiaBase,
            criar_match_com_confianca,
            validar_confianca,
            obter_config_padrao,
        )
        print("✅ Todas as importações funcionaram!")
        return True
    except ImportError as e:
        print(f"❌ Erro na importação: {e}")
        return False


def test_estrategia_abstrata():
    """Testa se EstrategiaBase é realmente abstrata."""
    print("\n" + "="*60)
    print("TESTE 2: EstrategiaBase é Abstrata")
    print("="*60)
    
    from src.conciliacao import EstrategiaBase
    
    try:
        # Tentar instanciar diretamente (deve falhar)
        estrategia = EstrategiaBase("teste", 10)
        print("❌ EstrategiaBase não deveria ser instanciável diretamente!")
        return False
    except TypeError as e:
        print(f"✅ EstrategiaBase é abstrata (correto): {e}")
        return True


def test_validacao_confianca():
    """Testa função de validação de confiança."""
    print("\n" + "="*60)
    print("TESTE 3: Validação de Confiança")
    print("="*60)
    
    from src.conciliacao import validar_confianca
    
    testes = [
        (0.0, True, "0.0 é válido"),
        (0.5, True, "0.5 é válido"),
        (1.0, True, "1.0 é válido"),
        (-0.1, False, "-0.1 é inválido"),
        (1.5, False, "1.5 é inválido"),
        ("texto", False, "string é inválida"),
    ]
    
    todos_passaram = True
    for valor, esperado, descricao in testes:
        resultado = validar_confianca(valor)
        if resultado == esperado:
            print(f"  ✅ {descricao}")
        else:
            print(f"  ❌ {descricao} - Esperado: {esperado}, Obtido: {resultado}")
            todos_passaram = False
    
    if todos_passaram:
        print("✅ Todas as validações passaram!")
    
    return todos_passaram


def test_config_padrao():
    """Testa configurações padrão."""
    print("\n" + "="*60)
    print("TESTE 4: Configurações Padrão")
    print("="*60)
    
    from src.conciliacao import obter_config_padrao
    
    config = obter_config_padrao()
    
    configs_esperadas = {
        "tolerancia_dias": 3,
        "tolerancia_valor": 0.50,
        "confianca_minima": 0.60,
        "confianca_auto_aprovar": 0.90,
        "max_matches_por_lancamento": 5,
        "usar_cache": True,
        "log_level": "INFO",
    }
    
    todos_passaram = True
    for chave, valor_esperado in configs_esperadas.items():
        if chave in config and config[chave] == valor_esperado:
            print(f"  ✅ {chave} = {valor_esperado}")
        else:
            print(f"  ❌ {chave} - Esperado: {valor_esperado}, Obtido: {config.get(chave, 'NÃO ENCONTRADO')}")
            todos_passaram = False
    
    if todos_passaram:
        print("✅ Todas as configurações estão corretas!")
    
    return todos_passaram


def test_info():
    """Testa função info()."""
    print("\n" + "="*60)
    print("TESTE 5: Função info()")
    print("="*60)
    
    from src.conciliacao import info
    
    try:
        info()
        print("✅ Função info() executou com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar info(): {e}")
        return False


def test_estrutura_arquivos():
    """Verifica se os arquivos existem."""
    print("\n" + "="*60)
    print("TESTE 6: Estrutura de Arquivos")
    print("="*60)
    
    arquivos_esperados = [
        "src/conciliacao/__init__.py",
        "src/conciliacao/estrategias/__init__.py",
        "src/conciliacao/estrategias/base.py",
    ]
    
    todos_existem = True
    for arquivo in arquivos_esperados:
        caminho = project_root / arquivo
        if caminho.exists():
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} - NÃO ENCONTRADO")
            todos_existem = False
    
    if todos_existem:
        print("✅ Todos os arquivos foram encontrados!")
    
    return todos_existem


def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🧪 TESTE DA ESTRUTURA - SPRINT 3")
    print("Sistema de Conciliação Bancária")
    print("="*60)
    
    resultados = []
    
    # Executar testes
    resultados.append(("Estrutura de Arquivos", test_estrutura_arquivos()))
    resultados.append(("Importações", test_imports()))
    resultados.append(("EstrategiaBase Abstrata", test_estrategia_abstrata()))
    resultados.append(("Validação de Confiança", test_validacao_confianca()))
    resultados.append(("Configurações Padrão", test_config_padrao()))
    resultados.append(("Função info()", test_info()))
    
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
        print("\n🎉 PARABÉNS! Estrutura instalada corretamente!")
        print("\nPróximos passos:")
        print("  1. Implementar EstrategiaExato")
        print("  2. Implementar MotorConciliacao")
        print("  3. Criar testes completos")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
