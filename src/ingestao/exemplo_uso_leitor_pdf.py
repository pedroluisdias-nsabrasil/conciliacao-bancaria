"""
Exemplo de uso do Leitor PDF.

Este script demonstra como usar o LeitorPDF para ler extratos bancários em PDF.
"""

from src.ingestao import LeitorPDF
from src.ingestao.leitor_pdf import PDFPLUMBER_DISPONIVEL


def exemplo_verificar_dependencia():
    """Exemplo 1: Verificar se pdfplumber está instalado."""
    print("=" * 60)
    print("EXEMPLO 1: Verificar Dependência")
    print("=" * 60)

    if PDFPLUMBER_DISPONIVEL:
        print("\n✓ pdfplumber está instalado e pronto para usar!")
    else:
        print("\n❌ pdfplumber NÃO está instalado")
        print("\nPara instalar:")
        print("  pip install pdfplumber")
        return False

    return True


def exemplo_basico():
    """Exemplo 2: Leitura básica de PDF."""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Leitura Básica")
    print("=" * 60)

    # Criar leitor
    leitor = LeitorPDF()

    # Nota: Este exemplo requer um PDF real
    # Para testar, crie um PDF com uma tabela de extrato

    print("\n⚠ Este exemplo requer um arquivo PDF real.")
    print("\nPara testar:")
    print("1. Coloque um extrato PDF em: dados/entrada/extratos/")
    print("2. Descomente o código abaixo:")
    print()
    print("# arquivo = 'dados/entrada/extratos/seu_extrato.pdf'")
    print("# lancamentos = leitor.ler_arquivo(arquivo)")
    print("# print(f'✓ {len(lancamentos)} lançamentos lidos!')")


def exemplo_multiplas_paginas():
    """Exemplo 3: Ler PDF com múltiplas páginas."""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Múltiplas Páginas")
    print("=" * 60)

    print("\nPara ler todas as páginas:")
    print("  leitor = LeitorPDF()")
    print("  lancamentos = leitor.ler_arquivo('extrato.pdf')")

    print("\nPara ler apenas páginas 2-5:")
    print("  leitor = LeitorPDF(primeira_pagina=2, ultima_pagina=5)")
    print("  lancamentos = leitor.ler_arquivo('extrato.pdf')")


def exemplo_indices_personalizados():
    """Exemplo 4: Configurar índices de colunas personalizados."""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Índices Personalizados")
    print("=" * 60)

    print("\nSe seu PDF tem colunas em ordem diferente:")
    print()
    print("# Exemplo: Valor na coluna 0, Data na 1, Descrição na 2")
    print("indices = {")
    print("    'valor': 0,")
    print("    'data': 1,")
    print("    'descricao': 2,")
    print("    'tipo': 3")
    print("}")
    print()
    print("leitor = LeitorPDF(indices_colunas=indices)")
    print("lancamentos = leitor.ler_arquivo('extrato_personalizado.pdf')")


def exemplo_informacoes_pdf():
    """Exemplo 5: Obter informações do PDF."""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Informações do PDF")
    print("=" * 60)

    print("\nPara ver informações sobre o PDF:")
    print()
    print("leitor = LeitorPDF()")
    print("info = leitor.obter_info_pdf('extrato.pdf')")
    print()
    print("print(f'Total de páginas: {info[\"total_paginas\"]}')")
    print("print(f'Tem tabelas: {info[\"tem_tabelas\"]}')")
    print('print(f\'Autor: {info["metadata"].get("Author")}\')')


def exemplo_texto_vs_tabela():
    """Exemplo 6: Escolher modo de extração."""
    print("\n" + "=" * 60)
    print("EXEMPLO 6: Texto vs Tabela")
    print("=" * 60)

    print("\nPor padrão, tenta extrair como tabela primeiro:")
    print("  lancamentos = leitor.ler_arquivo('extrato.pdf')")

    print("\nPara forçar extração como texto livre:")
    print("  lancamentos = leitor.ler_arquivo('extrato.pdf', usar_tabelas=False)")

    print("\n💡 Use texto livre se:")
    print("  - PDF não tem tabelas bem definidas")
    print("  - Extração de tabela falha")
    print("  - Formato do PDF é irregular")


def exemplo_tratamento_erro():
    """Exemplo 7: Tratamento de erros."""
    print("\n" + "=" * 60)
    print("EXEMPLO 7: Tratamento de Erros")
    print("=" * 60)

    from src.ingestao.leitor_pdf import PDFNaoSuportadoError, PDFSemConteudoError

    print("\nTratamento de erros comuns:")
    print()
    print("try:")
    print("    leitor = LeitorPDF()")
    print("    lancamentos = leitor.ler_arquivo('extrato.pdf')")
    print()
    print("except PDFNaoSuportadoError as e:")
    print("    print(f'PDF inválido: {e}')")
    print()
    print("except PDFSemConteudoError as e:")
    print("    print(f'PDF sem conteúdo: {e}')")
    print("    print('Talvez seja um PDF escaneado (imagem)?')")


def exemplo_comparacao_csv_pdf():
    """Exemplo 8: Diferenças entre CSV e PDF."""
    print("\n" + "=" * 60)
    print("EXEMPLO 8: CSV vs PDF")
    print("=" * 60)

    print("\n📊 Quando usar CSV:")
    print("  ✓ Arquivo já está em formato CSV")
    print("  ✓ Dados bem estruturados")
    print("  ✓ Processamento mais rápido")

    print("\n📄 Quando usar PDF:")
    print("  ✓ Banco só fornece PDF")
    print("  ✓ PDF tem texto nativo (não escaneado)")
    print("  ✓ Necessário extrair de documento oficial")

    print("\n⚠ Limitações do PDF:")
    print("  ✗ PDFs escaneados (só imagem) → use OCR")
    print("  ✗ Formatação irregular → resultados variáveis")
    print("  ✗ Mais lento que CSV")


def exemplo_instalacao_pdfplumber():
    """Exemplo 9: Como instalar pdfplumber."""
    print("\n" + "=" * 60)
    print("EXEMPLO 9: Instalar pdfplumber")
    print("=" * 60)

    print("\n📦 Para instalar pdfplumber:")
    print()
    print("# No terminal/PowerShell:")
    print("pip install pdfplumber")
    print()
    print("# Ou adicionar ao requirements.txt:")
    print("pdfplumber>=0.9.0")
    print()
    print("# Depois instalar:")
    print("pip install -r requirements.txt")


if __name__ == "__main__":
    print("\n")
    print("📄" * 30)
    print("  EXEMPLOS DE USO DO LEITOR PDF")
    print("📄" * 30)

    try:
        # Verificar dependência primeiro
        if not exemplo_verificar_dependencia():
            exemplo_instalacao_pdfplumber()
        else:
            exemplo_basico()
            exemplo_multiplas_paginas()
            exemplo_indices_personalizados()
            exemplo_informacoes_pdf()
            exemplo_texto_vs_tabela()
            exemplo_tratamento_erro()
            exemplo_comparacao_csv_pdf()

        print("\n" + "=" * 60)
        print("✅ EXEMPLOS CONCLUÍDOS!")
        print("=" * 60)
        print()

        print("💡 PRÓXIMOS PASSOS:")
        print("1. Instalar pdfplumber (se necessário)")
        print("2. Testar com um PDF real")
        print("3. Ajustar índices se necessário")
        print()

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
