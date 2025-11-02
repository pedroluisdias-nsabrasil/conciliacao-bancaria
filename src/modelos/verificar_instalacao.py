"""
Script de Verificação - Modelos de Dados

Este script verifica se todos os modelos foram instalados corretamente
e estão funcionando conforme esperado.

Para executar:
    python verificar_instalacao.py

Author: Pedro Luis
Date: 02/11/2025
"""

import sys
from decimal import Decimal
from datetime import date


def verificar_imports():
    """Verifica se todos os imports estão funcionando."""
    print("1. Verificando imports...", end=" ")
    
    try:
        from src.modelos.lancamento import Lancamento, LancamentoError
        from src.modelos.comprovante import Comprovante, ComprovanteError, OCRError
        from src.modelos.match import Match, MatchError
        print("✅ OK")
        return True
    except ImportError as e:
        print(f"❌ ERRO: {e}")
        print("\n💡 Solução:")
        print("   1. Certifique-se de que está na pasta src/modelos/")
        print("   2. Execute: cd C:\\conciliacao-bancaria\\src\\modelos")
        print("   3. Execute novamente: python verificar_instalacao.py")
        return False


def verificar_lancamento():
    """Verifica se o modelo Lancamento está funcionando."""
    print("2. Verificando modelo Lancamento...", end=" ")
    
    try:
        from src.modelos.lancamento import Lancamento
        
        # Criar lançamento de teste
        lanc = Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('100.00'),
            descricao='Teste',
            tipo='D'
        )
        
        # Verificar propriedades
        assert lanc.valor_com_sinal == Decimal('-100.00')
        assert lanc.tipo_descritivo == 'Débito'
        assert lanc.conciliado == False
        
        # Verificar métodos
        lanc.marcar_como_conciliado()
        assert lanc.conciliado == True
        
        print("✅ OK")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def verificar_comprovante():
    """Verifica se o modelo Comprovante está funcionando."""
    print("3. Verificando modelo Comprovante...", end=" ")
    
    try:
        from src.modelos.comprovante import Comprovante
        
        # Criar comprovante de teste
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date(2025, 11, 2),
            valor=Decimal('100.00'),
            confianca_ocr=0.95
        )
        
        # Verificar propriedades
        assert comp.nome_arquivo == 'teste.pdf'
        assert comp.nivel_confianca_ocr == 'Alta'
        assert comp.tem_boa_qualidade() == True
        
        print("✅ OK")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def verificar_match():
    """Verifica se o modelo Match está funcionando."""
    print("4. Verificando modelo Match...", end=" ")
    
    try:
        from src.modelos.lancamento import Lancamento
        from src.modelos.comprovante import Comprovante
        from src.modelos.match import Match
        
        # Criar lançamento e comprovante
        lanc = Lancamento(
            data=date(2025, 11, 2),
            valor=Decimal('100.00'),
            descricao='Teste',
            tipo='D'
        )
        
        comp = Comprovante(
            arquivo='teste.pdf',
            data=date(2025, 11, 2),
            valor=Decimal('100.00')
        )
        
        # Criar match
        match = Match(
            lancamento=lanc,
            comprovante=comp,
            confianca=0.95,
            metodo='exato'
        )
        
        # Verificar propriedades
        assert match.nivel_confianca == 'Alta'
        assert match.pode_auto_aprovar == True
        assert match.requer_revisao == False
        
        # Verificar confirmação
        match.confirmar(usuario='Teste')
        assert match.confirmado == True
        assert lanc.conciliado == True
        assert comp.conciliado == True
        
        print("✅ OK")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def verificar_validacoes():
    """Verifica se as validações estão funcionando."""
    print("5. Verificando validações...", end=" ")
    
    try:
        from src.modelos.lancamento import Lancamento
        from src.modelos.comprovante import Comprovante
        from src.modelos.match import Match
        
        # Testar validação de tipo inválido
        try:
            Lancamento(date.today(), Decimal('100'), 'Teste', 'X')
            print("❌ ERRO: Validação de tipo não funcionou")
            return False
        except ValueError:
            pass  # Esperado
        
        # Testar validação de valor zero
        try:
            Lancamento(date.today(), Decimal('0'), 'Teste', 'D')
            print("❌ ERRO: Validação de valor não funcionou")
            return False
        except ValueError:
            pass  # Esperado
        
        # Testar validação de confiança OCR
        try:
            Comprovante('teste.pdf', date.today(), Decimal('100'), confianca_ocr=1.5)
            print("❌ ERRO: Validação de confiança OCR não funcionou")
            return False
        except ValueError:
            pass  # Esperado
        
        print("✅ OK")
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def verificar_testes():
    """Verifica se pytest está instalado e os testes podem ser executados."""
    print("6. Verificando pytest...", end=" ")
    
    try:
        import pytest
        print("✅ OK")
        return True
    except ImportError:
        print("⚠️  AVISO: pytest não instalado")
        print("\n💡 Para instalar:")
        print("   pip install pytest --break-system-packages")
        return False


def main():
    """Função principal que executa todas as verificações."""
    print("\n" + "=" * 70)
    print("VERIFICAÇÃO DE INSTALAÇÃO - MODELOS DE DADOS")
    print("=" * 70 + "\n")
    
    resultados = []
    
    # Executar verificações
    resultados.append(verificar_imports())
    
    if resultados[0]:  # Só continua se imports funcionaram
        resultados.append(verificar_lancamento())
        resultados.append(verificar_comprovante())
        resultados.append(verificar_match())
        resultados.append(verificar_validacoes())
        resultados.append(verificar_testes())
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    
    total = len(resultados)
    sucessos = sum(resultados)
    
    print(f"\n✅ {sucessos}/{total} verificações passaram")
    
    if sucessos == total:
        print("\n🎉 PARABÉNS! Todos os modelos estão instalados e funcionando!")
        print("\nPróximos passos:")
        print("1. Execute os testes completos: pytest test_modelos.py -v")
        print("2. Execute os exemplos: python exemplo_uso_modelos.py")
        print("3. Comece a implementar o leitor CSV!")
        
    elif sucessos == 0:
        print("\n❌ Nenhuma verificação passou. Possíveis problemas:")
        print("1. Arquivos não foram copiados para a pasta correta")
        print("2. Você não está na pasta src/modelos/")
        print("3. Ambiente virtual não está ativado")
        print("\n💡 Consulte INSTALACAO_RAPIDA.md para instruções detalhadas")
        
    else:
        print(f"\n⚠️  Algumas verificações falharam ({total - sucessos}/{total})")
        print("Revise os erros acima e tente corrigir.")
    
    print("\n" + "=" * 70 + "\n")
    
    # Retornar código de saída apropriado
    sys.exit(0 if sucessos == total else 1)


if __name__ == '__main__':
    main()
