from decimal import Decimal
from datetime import date
from dataclasses import dataclass
from src.relatorios import GeradorExcel

@dataclass
class Lancamento:
    data: date
    tipo: str
    valor: Decimal
    descricao: str

@dataclass
class Comprovante:
    arquivo: str

@dataclass
class Match:
    lancamento: object
    comprovante: object
    confianca: float
    metodo: str

# Criar dados de teste
print('📝 Criando dados de teste...')
lanc1 = Lancamento(date(2025, 11, 4), 'D', Decimal('150.00'), 'COMPRA MERCADO EXTRA')
lanc2 = Lancamento(date(2025, 11, 4), 'C', Decimal('500.00'), 'PIX RECEBIDO CLIENTE')
lanc3 = Lancamento(date(2025, 11, 4), 'D', Decimal('75.50'), 'TARIFA BANCARIA')

comp1 = Comprovante('comprovante_mercado.pdf')
comp2 = Comprovante('comprovante_pix.pdf')

match1 = Match(lanc1, comp1, 0.95, 'exato')  # Verde (auto-aprovado)
match2 = Match(lanc2, comp2, 0.75, 'fuzzy')  # Amarelo (revisar)

stats = {
    'total_lancamentos': 3,
    'auto_aprovados': 1,
    'revisar': 1,
    'nao_conciliados': 1,
    'taxa_conciliacao': 66.7,
    'tempo_execucao': 0.5
}

# Gerar relatório
print('📊 Gerando relatório Excel...')
gerador = GeradorExcel()
arquivo = gerador.gerar(
    matches=[match1, match2],
    lancamentos_nao_conciliados=[lanc3],
    estatisticas=stats,
    arquivo_saida='dados/saida/relatorio_sprint5_teste.xlsx'
)

print('')
print('✅ SUCESSO! Relatório gerado:')
print(f'📂 {arquivo}')
print('')
print('🎨 O relatório tem:')
print('   ✅ 3 abas (Resumo, Conciliados, Não Conciliados)')
print('   🟢 Linha VERDE: Auto-aprovado (95% confiança)')
print('   🟡 Linha AMARELA: Revisar (75% confiança)')
print('   🔴 Linha VERMELHA: Não conciliado')
print('')
print('📊 ABRA O ARQUIVO NO EXCEL AGORA!')
