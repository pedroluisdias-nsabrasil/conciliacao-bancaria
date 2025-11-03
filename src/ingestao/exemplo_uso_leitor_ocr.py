"""
Exemplos de Uso - LeitorOCR e Preprocessador.

Este mÃ³dulo demonstra como usar o LeitorOCR e o Preprocessador
para extrair dados de comprovantes de pagamento.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Date: 03/11/2025
Sprint: 2 - OCR
"""

from pathlib import Path
from src.ingestao.preprocessador import Preprocessador, preprocessar_para_ocr
from src.ingestao.leitor_ocr import LeitorOCR


def exemplo_1_preprocessador_basico():
    """
    Exemplo 1: Uso bÃ¡sico do Preprocessador.
    
    Mostra como preprocessar uma imagem para melhorar qualidade.
    """
    print("=" * 60)
    print("EXEMPLO 1: Preprocessador BÃ¡sico")
    print("=" * 60)
    
    # Criar preprocessador com configuraÃ§Ãµes padrÃ£o
    preprocessador = Preprocessador()
    
    # Processar imagem
    # NOTA: Substitua 'comprovante.jpg' por um arquivo real
    arquivo_entrada = 'comprovante.jpg'
    arquivo_saida = 'comprovante_processado.png'
    
    print(f"\nðŸ“· Processando: {arquivo_entrada}")
    print(f"âš™ï¸  ConfiguraÃ§Ãµes:")
    print(f"   - Escala de cinza: {preprocessador.escala_cinza}")
    print(f"   - Binarizar: {preprocessador.binarizar}")
    print(f"   - Contraste: {preprocessador.contraste}")
    print(f"   - Remover ruÃ­do: {preprocessador.remover_ruido}")
    
    try:
        # Processar e salvar
        resultado = preprocessador.processar_para_arquivo(
            arquivo_entrada,
            arquivo_saida,
            formato='PNG'
        )
        print(f"\nâœ… Imagem processada salva em: {resultado}")
    except Exception as e:
        print(f"\nâŒ Erro: {e}")
        print("ðŸ’¡ Dica: Crie um arquivo 'comprovante.jpg' para testar")


def exemplo_2_preprocessador_personalizado():
    """
    Exemplo 2: Preprocessador com configuraÃ§Ãµes personalizadas.
    
    Mostra como ajustar configuraÃ§Ãµes para diferentes tipos de imagens.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Preprocessador Personalizado")
    print("=" * 60)
    
    # ConfiguraÃ§Ã£o para imagens de baixa qualidade
    print("\nðŸ“· ConfiguraÃ§Ã£o para scan de baixa qualidade:")
    prep_baixa_qualidade = Preprocessador(
        escala_cinza=True,
        binarizar=True,
        contraste=2.5,        # Contraste alto
        remover_ruido=True,
        redimensionar=False
    )
    print("   âœ“ Contraste alto (2.5)")
    print("   âœ“ BinarizaÃ§Ã£o ativada")
    print("   âœ“ RemoÃ§Ã£o de ruÃ­do")
    
    # ConfiguraÃ§Ã£o para fotos de celular
    print("\nðŸ“± ConfiguraÃ§Ã£o para foto de celular:")
    prep_foto = Preprocessador(
        escala_cinza=True,
        binarizar=False,       # Sem binarizaÃ§Ã£o
        contraste=1.8,
        remover_ruido=True,
        redimensionar=True,    # Redimensionar para otimizar
        tamanho_alvo=(1200, 1800)
    )
    print("   âœ“ Sem binarizaÃ§Ã£o (manter tons)")
    print("   âœ“ Redimensionamento ativado")
    print("   âœ“ Contraste moderado (1.8)")


def exemplo_3_funcao_conveniencia():
    """
    Exemplo 3: FunÃ§Ã£o de conveniÃªncia preprocessar_para_ocr().
    
    Mostra como usar a funÃ§Ã£o simples para preprocessamento rÃ¡pido.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 3: FunÃ§Ã£o de ConveniÃªncia")
    print("=" * 60)
    
    print("\nâš¡ Uso rÃ¡pido com configuraÃ§Ãµes otimizadas:")
    print("   >>> from src.ingestao.preprocessador import preprocessar_para_ocr")
    print("   >>> imagem = preprocessar_para_ocr('comprovante.jpg')")
    print("   >>> imagem.save('processado.png')")
    
    print("\nâœ… AplicaÃ§Ãµes:")
    print("   - Preprocessamento rÃ¡pido")
    print("   - ConfiguraÃ§Ãµes otimizadas para OCR")
    print("   - Ideal para protÃ³tipos")


def exemplo_4_leitor_ocr_basico():
    """
    Exemplo 4: Uso bÃ¡sico do LeitorOCR.
    
    Mostra como extrair dados de um comprovante.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 4: LeitorOCR BÃ¡sico")
    print("=" * 60)
    
    try:
        # Criar leitor
        leitor = LeitorOCR()
        
        print("\nðŸ” LeitorOCR criado com sucesso!")
        print("âš™ï¸  ConfiguraÃ§Ãµes:")
        print(f"   - Idioma: {leitor.idioma}")
        print(f"   - ConfianÃ§a mÃ­nima: {leitor.confianca_minima:.0%}")
        print(f"   - Preprocessar: {leitor.preprocessar}")
        
        # Obter informaÃ§Ãµes do Tesseract
        info = leitor.obter_info_ocr()
        print(f"\nðŸ“‹ Tesseract:")
        print(f"   - VersÃ£o: {info['versao_tesseract']}")
        print(f"   - Comando: {info['tesseract_cmd']}")
        
        # Exemplo de uso (comentado pois precisa de arquivo real)
        print("\nðŸ’¡ Exemplo de uso:")
        print("   >>> comprovante = leitor.ler_arquivo('comprovante.pdf')")
        print("   >>> print(f'Valor: R$ {comprovante.valor}')")
        print("   >>> print(f'ConfianÃ§a: {comprovante.confianca_ocr:.0%}')")
        
    except Exception as e:
        print(f"\nâŒ Erro ao criar LeitorOCR: {e}")
        print("ðŸ’¡ Verifique se o Tesseract estÃ¡ instalado:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")


def exemplo_5_leitor_ocr_personalizado():
    """
    Exemplo 5: LeitorOCR com configuraÃ§Ãµes personalizadas.
    
    Mostra como ajustar configuraÃ§Ãµes do OCR.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 5: LeitorOCR Personalizado")
    print("=" * 60)
    
    try:
        # Alta precisÃ£o (mais conservador)
        print("\nðŸŽ¯ ConfiguraÃ§Ã£o de alta precisÃ£o:")
        leitor_preciso = LeitorOCR(
            confianca_minima=0.85,  # ConfianÃ§a alta
            preprocessar=True,
            idioma='por'
        )
        print(f"   âœ“ ConfianÃ§a mÃ­nima: {leitor_preciso.confianca_minima:.0%}")
        print("   âœ“ Preprocessamento ativado")
        print("   âœ“ Ideal para documentos crÃ­ticos")
        
        # RÃ¡pido (mais permissivo)
        print("\nâš¡ ConfiguraÃ§Ã£o rÃ¡pida:")
        leitor_rapido = LeitorOCR(
            confianca_minima=0.5,   # ConfianÃ§a baixa
            preprocessar=False,      # Sem preprocessamento
            idioma='por'
        )
        print(f"   âœ“ ConfianÃ§a mÃ­nima: {leitor_rapido.confianca_minima:.0%}")
        print("   âœ“ Sem preprocessamento")
        print("   âœ“ Ideal para processamento em lote")
        
    except Exception as e:
        print(f"\nâŒ Erro: {e}")


def exemplo_6_extrair_de_pdf():
    """
    Exemplo 6: Extrair dados de PDF.
    
    Mostra como processar PDFs com uma ou mÃºltiplas pÃ¡ginas.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 6: Extrair de PDF")
    print("=" * 60)
    
    print("\nðŸ“„ PDF com uma pÃ¡gina:")
    print("   >>> leitor = LeitorOCR()")
    print("   >>> comprovante = leitor.ler_arquivo('comprovante.pdf', pagina=1)")
    print("   >>> print(comprovante.valor)")
    
    print("\nðŸ“š PDF com mÃºltiplas pÃ¡ginas:")
    print("   >>> comprovantes = leitor.ler_arquivo('comprovantes.pdf')")
    print("   >>> print(f'{len(comprovantes)} comprovantes extraÃ­dos')")
    print("   >>> for comp in comprovantes:")
    print("   ...     print(f'PÃ¡gina {i+1}: R$ {comp.valor}')")
    
    print("\nâœ… Formatos suportados:")
    print("   - PDF (uma ou mÃºltiplas pÃ¡ginas)")
    print("   - PNG, JPG, JPEG")
    print("   - BMP, TIFF")


def exemplo_7_processar_lote():
    """
    Exemplo 7: Processar lote de comprovantes.
    
    Mostra como processar mÃºltiplos arquivos em lote.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 7: Processar Lote")
    print("=" * 60)
    
    print("\nðŸ“¦ Processar mÃºltiplos comprovantes:")
    print("""
from pathlib import Path
from src.ingestao.leitor_ocr import LeitorOCR

# Criar leitor
leitor = LeitorOCR()

# DiretÃ³rio com comprovantes
pasta = Path('dados/entrada/comprovantes/')

# Processar todos os PDFs
comprovantes = []
for arquivo in pasta.glob('*.pdf'):
    print(f'Processando: {arquivo.name}')
    try:
        comp = leitor.ler_arquivo(arquivo)
        comprovantes.append(comp)
        print(f'  âœ“ R$ {comp.valor} - ConfianÃ§a: {comp.confianca_ocr:.0%}')
    except Exception as e:
        print(f'  âœ— Erro: {e}')

# EstatÃ­sticas
total = sum(c.valor for c in comprovantes)
media_confianca = sum(c.confianca_ocr for c in comprovantes) / len(comprovantes)

print(f'\\nðŸ“Š Resumo:')
print(f'  - Total processado: {len(comprovantes)} comprovantes')
print(f'  - Valor total: R$ {total}')
print(f'  - ConfianÃ§a mÃ©dia: {media_confianca:.0%}')
    """)


def exemplo_8_tratamento_erros():
    """
    Exemplo 8: Tratamento de erros.
    
    Mostra como lidar com erros comuns.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 8: Tratamento de Erros")
    print("=" * 60)
    
    print("\nðŸ›¡ï¸ Tratamento robusto:")
    print("""
from src.ingestao.leitor_ocr import LeitorOCR, LeitorOCRError, TesseractNaoEncontradoError

try:
    # Criar leitor
    leitor = LeitorOCR(confianca_minima=0.7)
    
    # Processar arquivo
    comprovante = leitor.ler_arquivo('comprovante.pdf')
    
    # Verificar confianÃ§a
    if comprovante.confianca_ocr < 0.7:
        print('âš ï¸  ConfianÃ§a baixa - revisar manualmente')
    else:
        print(f'âœ… ExtraÃ­do: R$ {comprovante.valor}')
        
except TesseractNaoEncontradoError:
    print('âŒ Tesseract nÃ£o encontrado')
    print('Instale: https://github.com/UB-Mannheim/tesseract/wiki')
    
except LeitorOCRError as e:
    print(f'âŒ Erro no OCR: {e}')
    
except Exception as e:
    print(f'âŒ Erro inesperado: {e}')
    """)
    
    print("\nâœ… Boas prÃ¡ticas:")
    print("   - Sempre verificar confianÃ§a do OCR")
    print("   - Tratar erros especÃ­ficos")
    print("   - Logar falhas para anÃ¡lise")
    print("   - Ter fallback para revisÃ£o manual")


def exemplo_9_pipeline_completo():
    """
    Exemplo 9: Pipeline completo de processamento.
    
    Integra preprocessamento e OCR em um fluxo completo.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO 9: Pipeline Completo")
    print("=" * 60)
    
    print("\nðŸ”„ Fluxo completo de processamento:")
    print("""
from pathlib import Path
from src.ingestao.preprocessador import Preprocessador
from src.ingestao.leitor_ocr import LeitorOCR

def processar_comprovante(arquivo: Path):
    \"\"\"Pipeline completo: preprocessar + OCR.\"\"\"
    
    # 1. Preprocessar imagem
    print(f'1ï¸âƒ£ Preprocessando: {arquivo.name}')
    preprocessador = Preprocessador(
        contraste=2.0,
        binarizar=True,
        remover_ruido=True
    )
    
    temp_file = arquivo.parent / f'{arquivo.stem}_processado.png'
    preprocessador.processar_para_arquivo(arquivo, temp_file)
    
    # 2. Extrair com OCR
    print(f'2ï¸âƒ£ Extraindo dados via OCR...')
    leitor = LeitorOCR(confianca_minima=0.7)
    comprovante = leitor.ler_arquivo(temp_file)
    
    # 3. Limpar arquivo temporÃ¡rio
    temp_file.unlink()
    
    # 4. Validar resultado
    print(f'3ï¸âƒ£ Validando resultado...')
    if comprovante.confianca_ocr >= 0.8:
        status = 'âœ… Alta confianÃ§a'
    elif comprovante.confianca_ocr >= 0.6:
        status = 'âš ï¸  MÃ©dia confianÃ§a - revisar'
    else:
        status = 'âŒ Baixa confianÃ§a - revisar obrigatÃ³rio'
    
    print(f'\\n{status}')
    print(f'Valor: R$ {comprovante.valor}')
    print(f'Data: {comprovante.data_pagamento}')
    print(f'ConfianÃ§a: {comprovante.confianca_ocr:.0%}')
    
    return comprovante

# Usar
# comprovante = processar_comprovante(Path('comprovante.jpg'))
    """)


def main():
    """Executa todos os exemplos."""
    print("\n" + "ðŸŽ“ " * 30)
    print("ðŸ“š EXEMPLOS DE USO - LEITOR OCR E PREPROCESSADOR")
    print("ðŸŽ“ " * 30)
    
    print("\nâš ï¸  NOTA: Alguns exemplos precisam de arquivos reais para funcionar.")
    print("ðŸ’¡ Crie arquivos de teste ou ajuste os caminhos conforme necessÃ¡rio.")
    
    # Executar exemplos
    exemplo_1_preprocessador_basico()
    exemplo_2_preprocessador_personalizado()
    exemplo_3_funcao_conveniencia()
    exemplo_4_leitor_ocr_basico()
    exemplo_5_leitor_ocr_personalizado()
    exemplo_6_extrair_de_pdf()
    exemplo_7_processar_lote()
    exemplo_8_tratamento_erros()
    exemplo_9_pipeline_completo()
    
    print("\n" + "=" * 60)
    print("âœ… EXEMPLOS CONCLUÃDOS!")
    print("=" * 60)
    print("\nðŸ“– DocumentaÃ§Ã£o completa no cÃ³digo-fonte")
    print("ðŸ§ª Execute os testes: pytest src/ingestao/test_leitor_ocr.py")
    print("\n")


if __name__ == '__main__':
    main()

