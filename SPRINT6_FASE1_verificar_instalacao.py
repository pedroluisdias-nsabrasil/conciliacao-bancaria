"""
Script de Verificação - Sprint 6 Fase 1

Verifica se todos os arquivos foram instalados corretamente
e se o parser está funcionando.
"""

import sys
from pathlib import Path


def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem."""
    print("=" * 60)
    print("🔍 VERIFICANDO ARQUIVOS DA FASE 1")
    print("=" * 60)
    
    arquivos_necessarios = [
        'src/regras/__init__.py',
        'src/regras/parser.py',
        'config/regras/tarifas.yaml',
        'tests/test_regras/__init__.py',
        'tests/test_regras/test_parser.py',
    ]
    
    todos_ok = True
    
    for arquivo in arquivos_necessarios:
        caminho = Path(arquivo)
        if caminho.exists():
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO!")
            todos_ok = False
    
    print()
    return todos_ok


def verificar_imports():
    """Verifica se os imports funcionam."""
    print("=" * 60)
    print("🔍 VERIFICANDO IMPORTS")
    print("=" * 60)
    
    try:
        from src.regras.parser import ParserRegras
        print("✅ Import de ParserRegras OK")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar ParserRegras: {e}")
        return False


def verificar_pyyaml():
    """Verifica se PyYAML está instalado."""
    print("=" * 60)
    print("🔍 VERIFICANDO PYYAML")
    print("=" * 60)
    
    try:
        import yaml
        print(f"✅ PyYAML instalado (versão {yaml.__version__})")
        return True
    except ImportError:
        print("❌ PyYAML não instalado!")
        print("   Execute: pip install pyyaml==6.0.1")
        return False


def verificar_carregamento_regras():
    """Verifica se consegue carregar as regras."""
    print("=" * 60)
    print("🔍 VERIFICANDO CARREGAMENTO DE REGRAS")
    print("=" * 60)
    
    try:
        from src.regras.parser import ParserRegras
        from pathlib import Path
        
        arquivo = Path('config/regras/tarifas.yaml')
        
        if not arquivo.exists():
            print("❌ Arquivo config/regras/tarifas.yaml não encontrado!")
            return False
        
        parser = ParserRegras(arquivo)
        regras = parser.carregar()
        
        print(f"✅ {len(regras)} regras carregadas com sucesso!")
        print(f"\nRegras ativas:")
        for regra in regras[:5]:  # Mostrar apenas 5 primeiras
            print(f"   • {regra['nome']} (ID: {regra['id']})")
        
        if len(regras) > 5:
            print(f"   ... e mais {len(regras) - 5} regras")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar regras: {e}")
        return False


def main():
    """Executa todas as verificações."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "VERIFICAÇÃO SPRINT 6 - FASE 1" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    resultados = []
    
    # Verificação 1: Arquivos
    resultados.append(("Arquivos", verificar_arquivos()))
    
    # Verificação 2: PyYAML
    resultados.append(("PyYAML", verificar_pyyaml()))
    
    # Verificação 3: Imports
    resultados.append(("Imports", verificar_imports()))
    
    # Verificação 4: Carregamento de regras
    resultados.append(("Regras", verificar_carregamento_regras()))
    
    # Resultado final
    print()
    print("=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    todos_ok = all(resultado for _, resultado in resultados)
    
    for nome, resultado in resultados:
        status = "✅ OK" if resultado else "❌ FALHOU"
        print(f"{nome:20s} {status}")
    
    print("=" * 60)
    
    if todos_ok:
        print()
        print("🎉 TUDO OK! FASE 1 INSTALADA COM SUCESSO!")
        print()
        print("Próximo passo: Retorne ao chat do Claude e digite 'FASE 1 OK'")
        print()
        return 0
    else:
        print()
        print("⚠️  ALGUNS PROBLEMAS ENCONTRADOS!")
        print()
        print("Revise o README_INSTALACAO.md e corrija os problemas.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
