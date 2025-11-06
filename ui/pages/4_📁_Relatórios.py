"""
Página de Relatórios - Geração e Download.
"""

# Configurar PYTHONPATH
import sys
from pathlib import Path

# Detectar se está em pages/ ou em ui/
arquivo_atual = Path(__file__).resolve()
if 'pages' in str(arquivo_atual.parent):
    # Estamos em ui/pages/ - subir 2 níveis
    raiz = arquivo_atual.parent.parent.parent
else:
    # Estamos em ui/ - subir 1 nível
    raiz = arquivo_atual.parent.parent

# Adicionar raiz e src/ ao path
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))
if str(raiz / 'src') not in sys.path:
    sys.path.insert(0, str(raiz / 'src'))
import streamlit as st
from datetime import datetime
from pathlib import Path

from src.relatorios.gerador_excel import GeradorExcel
from src.relatorios.gerador_pdf import GeradorPDF

st.set_page_config(
    page_title="Relatórios",
    page_icon="📁",
    layout="wide"
)

st.title("📁 Relatórios de Conciliação")

# ============================================================================
# VERIFICAR SE HÁ DADOS PARA GERAR RELATÓRIO
# ============================================================================

if not st.session_state.get('matches'):
    st.warning("⚠️ Nenhuma conciliação realizada ainda!")
    st.info("👉 Vá para a página **🔄 Conciliar** para executar a conciliação primeiro.")
    st.stop()

# ============================================================================
# DADOS DISPONÍVEIS
# ============================================================================

matches = st.session_state.matches
lancamentos = st.session_state.lancamentos or []
comprovantes = st.session_state.comprovantes or []
stats = st.session_state.stats

# Separar matches por status
conciliados = [m for m in matches if m.aprovado]
nao_conciliados = [
    lanc for lanc in lancamentos 
    if not any(m.lancamento == lanc and m.aprovado for m in matches)
]

st.markdown("---")

# ============================================================================
# ESTATÍSTICAS
# ============================================================================

st.subheader("📊 Resumo dos Dados")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Lançamentos", len(lancamentos))

with col2:
    st.metric("Conciliados", len(conciliados))

with col3:
    st.metric("Não Conciliados", len(nao_conciliados))

with col4:
    st.metric("Taxa", f"{stats['taxa_conciliacao']:.1%}")

st.markdown("---")

# ============================================================================
# GERAÇÃO DE RELATÓRIOS
# ============================================================================

st.subheader("📥 Gerar e Baixar Relatórios")

col_excel, col_pdf = st.columns(2)

# ============================================================================
# RELATÓRIO EXCEL
# ============================================================================

with col_excel:
    st.markdown("### 📊 Relatório Excel")
    st.markdown("""
    **Inclui:**
    - Aba de Matches Conciliados
    - Aba de Lançamentos Não Conciliados
    - Formatação condicional por confiança
    - Estatísticas detalhadas
    """)
    
    if st.button("🔄 Gerar Excel", type="primary", use_container_width=True):
        with st.spinner("Gerando relatório Excel..."):
            try:
                # Configurar caminho de saída
                output_dir = Path("dados/saida")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                arquivo_excel = output_dir / f"relatorio_conciliacao_{timestamp}.xlsx"
                
                # Gerar Excel
                gerador = GeradorExcel()
                arquivo_gerado = gerador.gerar(
                    matches=conciliados,
                    lancamentos_nao_conciliados=nao_conciliados,
                    estatisticas=stats,
                    arquivo_saida=str(arquivo_excel)
                )
                
                # Ler arquivo para download
                with open(arquivo_gerado, 'rb') as f:
                    excel_data = f.read()
                
                st.success("✅ Relatório Excel gerado com sucesso!")
                
                # Botão de download
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"relatorio_conciliacao_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar Excel: {e}")

# ============================================================================
# RELATÓRIO PDF
# ============================================================================

with col_pdf:
    st.markdown("### 📄 Relatório PDF")
    st.markdown("""
    **Inclui:**
    - Cabeçalho profissional
    - Resumo executivo
    - Gráfico de distribuição
    - Tabelas formatadas
    """)
    
    if st.button("🔄 Gerar PDF", type="primary", use_container_width=True):
        with st.spinner("Gerando relatório PDF..."):
            try:
                # Configurar caminho de saída
                output_dir = Path("dados/saida")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                arquivo_pdf = output_dir / f"relatorio_conciliacao_{timestamp}.pdf"
                
                # Gerar PDF
                gerador = GeradorPDF()
                arquivo_gerado = gerador.gerar(
                    matches=conciliados,
                    lancamentos_nao_conciliados=nao_conciliados,
                    estatisticas=stats,
                    arquivo_saida=str(arquivo_pdf)
                )
                
                # Ler arquivo para download
                with open(arquivo_gerado, 'rb') as f:
                    pdf_data = f.read()
                
                st.success("✅ Relatório PDF gerado com sucesso!")
                
                # Botão de download
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_data,
                    file_name=f"relatorio_conciliacao_{timestamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF: {e}")

st.markdown("---")

# ============================================================================
# INFORMAÇÕES ADICIONAIS
# ============================================================================

with st.expander("ℹ️ Sobre os Relatórios"):
    st.markdown("""
    ### 📊 Relatório Excel
    
    O relatório Excel contém 3 abas:
    
    1. **Resumo**: Estatísticas gerais da conciliação
    2. **Conciliados**: Todos os matches aprovados com seus detalhes
    3. **Não Conciliados**: Lançamentos sem match encontrado
    
    **Formatação:**
    - 🟢 Verde: Confiança ≥ 90% (Auto-aprovado)
    - 🟡 Amarelo: Confiança 60-89% (Revisar)
    - 🔴 Vermelho: Não conciliado
    
    ---
    
    ### 📄 Relatório PDF
    
    O relatório PDF é ideal para apresentações e inclui:
    
    - Cabeçalho com logo e data
    - Resumo executivo com KPIs principais
    - Gráfico de pizza da distribuição
    - Tabelas formatadas e paginadas
    - Rodapé em todas as páginas
    
    **Formato:** A4 (210x297mm) com margens profissionais
    """)

with st.expander("💡 Dicas de Uso"):
    st.markdown("""
    - **Excel**: Melhor para análise detalhada e edição posterior
    - **PDF**: Melhor para enviar para clientes ou gestores
    - Os arquivos também ficam salvos em `dados/saida/`
    - Você pode gerar ambos os formatos
    - Cada geração cria um arquivo com timestamp único
    """)

# Footer
st.markdown("---")
st.caption("📁 Relatórios | Sistema de Conciliação Bancária v1.0")