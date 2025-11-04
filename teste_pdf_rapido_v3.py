"""
teste_pdf_rapido_v3.py - Teste do GeradorPDF (VERSÃO FINAL CORRIGIDA)

Execute: python teste_pdf_rapido_v3.py
"""

from datetime import date
from decimal import Decimal
from src.modelos.lancamento import Lancamento
from src.modelos.comprovante import Comprovante
from src.modelos.match import Match
from src.relatorios.gerador_pdf import GeradorPDF


def criar_dados_teste():
    """Cria dados de teste com estrutura CORRETA."""
    
    # ========================================
    # LANÇAMENTOS
    # ========================================
    
    lanc1 = Lancamento(
        data=date(2025, 11, 1),
        valor=Decimal('100.00'),
        descricao="PIX RECEBIDO - TESTE 1",
        tipo='C',  # Crédito
        saldo=Decimal('1000.00')
    )
    
    lanc2 = Lancamento(
        data=date(2025, 11, 2),
        valor=Decimal('50.00'),
        descricao="PAGAMENTO TED - TESTE 2",
        tipo='D',  # Débito
        saldo=Decimal('950.00')
    )
    
    lanc3 = Lancamento(
        data=date(2025, 11, 3),
        valor=Decimal('200.00'),
        descricao="TARIFA BANCARIA",
        tipo='D',
        saldo=Decimal('750.00')
    )
    
    # ========================================
    # COMPROVANTES (estrutura correta!)
    # ========================================
    
    # Comprovante 1 - PIX
    comp1 = Comprovante(
        arquivo="comprovantes/pix_001.pdf",
        data=date(2025, 11, 1),
        valor=Decimal('100.00'),
        beneficiario="João Silva",
        descricao="Pagamento via PIX",
        tipo_documento="PIX",
        confianca_ocr=0.95
    )
    
    # Comprovante 2 - TED
    comp2 = Comprovante(
        arquivo="comprovantes/ted_002.pdf",
        data=date(2025, 11, 2),
        valor=Decimal('50.00'),
        beneficiario="Maria Santos",
        descricao="Transferência TED",
        tipo_documento="TED",
        numero_documento="TED-123456",
        confianca_ocr=0.78
    )
    
    # ========================================
    # MATCHES
    # ========================================
    
    # Match 1 - Auto-aprovado (≥0.90)
    match1 = Match(
        lancamento=lanc1,
        comprovante=comp1,
        confianca=0.95,
        metodo="exato",
        observacoes="Match exato: valor R$ 100.00, data 01/11/2025 e tipo PIX"
    )
    
    # Match 2 - Para revisar (0.60-0.89)
    match2 = Match(
        lancamento=lanc2,
        comprovante=comp2,
        confianca=0.75,
        metodo="exato",
        observacoes="Match por valor e data, diferença na descrição"
    )
    
    # ========================================
    # ESTATÍSTICAS
    # ========================================
    
    stats = {
        'total_lancamentos': 10,
        'auto_aprovados': 6,
        'revisar': 2,
        'nao_conciliados': 2,
        'taxa_conciliacao': 80.0,
        'tempo_execucao': 1.5
    }
    
    return [match1, match2], [lanc3], stats


def main():
    """Executa teste do GeradorPDF."""
    print("🧪 Testando GeradorPDF...")
    print("=" * 60)
    
    try:
        # Criar dados de teste
        matches, nao_conc, stats = criar_dados_teste()
        
        print(f"📊 Dados de teste criados:")
        print(f"   - {len(matches)} matches conciliados")
        print(f"   - {len(nao_conc)} não conciliados")
        print(f"   - Taxa de conciliação: {stats['taxa_conciliacao']}%")
        print()
        
        # Mostrar detalhes dos matches
        print("🔍 Detalhes dos matches:")
        for i, match in enumerate(matches, 1):
            conf_pct = match.confianca * 100
            status = "🟢 AUTO-APROVADO" if match.confianca >= 0.90 else "🟡 REVISAR"
            print(f"   {i}. {status} ({conf_pct:.0f}%)")
            print(f"      Lançamento: {match.lancamento.descricao}")
            print(f"      Comprovante: {match.comprovante.beneficiario}")
        print()
        
        # Gerar PDF
        print("📄 Gerando PDF...")
        gerador = GeradorPDF()
        arquivo = gerador.gerar(
            matches=matches,
            lancamentos_nao_conciliados=nao_conc,
            estatisticas=stats,
            arquivo_saida="dados/saida/teste_pdf.pdf"
        )
        
        print("=" * 60)
        print(f"✅ PDF gerado com sucesso!")
        print(f"📂 Arquivo: {arquivo}")
        print()
        print("🎨 Conteúdo do PDF:")
        print("   ✅ Cabeçalho: Título + Data geração")
        print("   ✅ Resumo Executivo: Tabela de KPIs")
        print("   ✅ Gráfico de Pizza: Distribuição por status")
        print("   ✅ Tabela Matches: 2 conciliados")
        print("      • 1 auto-aprovado (verde)")
        print("      • 1 para revisar (amarelo)")
        print("   ✅ Tabela Não Conciliados: 1 lançamento (fundo vermelho)")
        print()
        print("💡 Abra o PDF para visualizar!")
        print(f"   → start {arquivo}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
