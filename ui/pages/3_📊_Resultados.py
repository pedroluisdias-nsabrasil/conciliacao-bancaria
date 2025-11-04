"""
Página de Resultados da Conciliação.

Exibe matches encontrados, estatísticas e permite download de relatórios.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Created: 04/11/2025
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.conciliacao.motor import MotorConciliacao


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

st.set_page_config(
    page_title="Resultados - Conciliação Bancária",
    page_icon="📊",
    layout="wide"
)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def criar_df_matches(matches, status_filter=None):
    """Cria DataFrame com os matches para exibição."""
    if not matches:
        return pd.DataFrame()
    
    # Filtrar por status se necessário
    if status_filter == 'auto_aprovado':
        config = st.session_state.motor_config
        matches = [m for m in matches if m.confianca >= config['confianca_auto_aprovar']]
    elif status_filter == 'revisar':
        config = st.session_state.motor_config
        matches = [m for m in matches if config['confianca_minima'] <= m.confianca < config['confianca_auto_aprovar']]
    
    data = []
    for match in matches:
        data.append({
            'Data Lanç.': match.lancamento.data.strftime('%d/%m/%Y'),
            'Descrição': match.lancamento.descricao[:50] + '...' if len(match.lancamento.descricao) > 50 else match.lancamento.descricao,
            'Valor': f"R$ {match.lancamento.valor:,.2f}",
            'Comprovante': match.comprovante.arquivo if match.comprovante else "N/A",
            'Confiança': f"{match.confianca:.1%}",
            'Método': match.metodo,
            'Status': get_status_icon(match.confianca)
        })
    
    return pd.DataFrame(data)


def criar_df_nao_conciliados(lancamentos, matches):
    """Cria DataFrame com lançamentos não conciliados."""
    # IDs dos lançamentos conciliados
    ids_conciliados = {id(m.lancamento) for m in matches}
    
    # Filtrar não conciliados
    nao_conciliados = [l for l in lancamentos if id(l) not in ids_conciliados]
    
    if not nao_conciliados:
        return pd.DataFrame()
    
    data = []
    for lanc in nao_conciliados:
        data.append({
            'Data': lanc.data.strftime('%d/%m/%Y'),
            'Tipo': 'Débito' if lanc.tipo == 'D' else 'Crédito',
            'Valor': f"R$ {lanc.valor:,.2f}",
            'Descrição': lanc.descricao[:60] + '...' if len(lanc.descricao) > 60 else lanc.descricao,
            'Saldo': f"R$ {lanc.saldo:,.2f}" if lanc.saldo else "N/A"
        })
    
    return pd.DataFrame(data)


def get_status_icon(confianca):
    """Retorna ícone de status baseado na confiança."""
    config = st.session_state.motor_config
    
    if confianca >= config['confianca_auto_aprovar']:
        return "✅ Auto-aprovado"
    elif confianca >= config['confianca_minima']:
        return "⚠️ Revisar"
    else:
        return "❌ Baixa"


def criar_grafico_distribuicao(stats):
    """Cria gráfico de distribuição de confiança."""
    if stats['total_matches'] == 0:
        return None
    
    # Dados
    labels = ['Alta (≥90%)', 'Média (70-90%)', 'Baixa (60-70%)']
    values = [
        stats['por_confianca']['alta'],
        stats['por_confianca']['media'],
        stats['por_confianca']['baixa']
    ]
    colors = ['#28a745', '#ffc107', '#dc3545']
    
    # Criar gráfico de pizza
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo='label+percent+value'
    )])
    
    fig.update_layout(
        title="Distribuição por Faixa de Confiança",
        height=400
    )
    
    return fig


def criar_grafico_taxa(stats):
    """Cria gráfico de taxa de conciliação."""
    conciliados = stats['total_matches']
    nao_conciliados = stats['total_lancamentos'] - stats['total_matches']
    
    fig = go.Figure(data=[go.Bar(
        x=['Conciliados', 'Não Conciliados'],
        y=[conciliados, nao_conciliados],
        marker=dict(color=['#28a745', '#dc3545']),
        text=[conciliados, nao_conciliados],
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Taxa de Conciliação",
        xaxis_title="Status",
        yaxis_title="Quantidade",
        height=400
    )
    
    return fig


# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

def main():
    """Página de resultados."""
    
    st.title("📊 Resultados da Conciliação")
    st.markdown("### Visualize os matches encontrados e estatísticas")
    
    st.markdown("---")
    
    # Verificar se tem resultados
    if st.session_state.matches is None or st.session_state.stats is None:
        st.warning("⚠️ Nenhuma conciliação executada ainda!")
        st.info("Por favor, execute a conciliação primeiro.")
        
        if st.button("🔄 Ir para Conciliação"):
            st.switch_page("pages/2_🔄_Conciliar.py")
        
        return
    
    matches = st.session_state.matches
    stats = st.session_state.stats
    lancamentos = st.session_state.lancamentos
    
    # ========================================================================
    # MÉTRICAS PRINCIPAIS
    # ========================================================================
    
    st.subheader("📈 Métricas Principais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total de Lançamentos",
            stats['total_lancamentos'],
            help="Total de lançamentos processados"
        )
    
    with col2:
        st.metric(
            "Matches Encontrados",
            stats['total_matches'],
            help="Total de matches encontrados"
        )
    
    with col3:
        st.metric(
            "Taxa de Conciliação",
            f"{stats['taxa_conciliacao']:.1%}",
            delta=f"{stats['taxa_conciliacao'] - 0.60:.1%}" if stats['taxa_conciliacao'] >= 0.60 else None,
            help="Percentual de lançamentos conciliados (meta: 60-70%)"
        )
    
    with col4:
        confianca_media = stats['confianca_media'] if stats['total_matches'] > 0 else 0
        st.metric(
            "Confiança Média",
            f"{confianca_media:.1%}",
            help="Confiança média dos matches"
        )
    
    with col5:
        st.metric(
            "Valor Conciliado",
            f"R$ {stats['valor_total_conciliado']:,.2f}",
            help="Valor total dos matches"
        )
    
    st.markdown("---")
    
    # ========================================================================
    # DISTRIBUIÇÃO
    # ========================================================================
    
    st.subheader("📊 Distribuição dos Resultados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "✅ Auto-aprovados",
            stats['auto_aprovados'],
            help="Matches com alta confiança (≥90%)"
        )
    
    with col2:
        st.metric(
            "⚠️ Requerem Revisão",
            stats['requer_revisao'],
            help="Matches com confiança média (60-90%)"
        )
    
    with col3:
        nao_conciliados = stats['total_lancamentos'] - stats['total_matches']
        st.metric(
            "❌ Não Conciliados",
            nao_conciliados,
            help="Lançamentos sem match"
        )
    
    st.markdown("---")
    
    # ========================================================================
    # GRÁFICOS
    # ========================================================================
    
    if stats['total_matches'] > 0:
        st.subheader("📈 Gráficos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_distribuicao = criar_grafico_distribuicao(stats)
            if fig_distribuicao:
                st.plotly_chart(fig_distribuicao, use_container_width=True)
        
        with col2:
            fig_taxa = criar_grafico_taxa(stats)
            st.plotly_chart(fig_taxa, use_container_width=True)
        
        st.markdown("---")
    
    # ========================================================================
    # TABS DE RESULTADOS
    # ========================================================================
    
    st.subheader("📋 Detalhamento dos Matches")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "✅ Auto-aprovados",
        "⚠️ Requerem Revisão",
        "❌ Não Conciliados",
        "📄 Todos os Matches"
    ])
    
    # TAB 1: Auto-aprovados
    with tab1:
        df_auto = criar_df_matches(matches, status_filter='auto_aprovado')
        
        if len(df_auto) > 0:
            st.success(f"✅ {len(df_auto)} match(es) com alta confiança (auto-aprovado)")
            st.dataframe(df_auto, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Nenhum match com confiança alta o suficiente para auto-aprovar")
    
    # TAB 2: Requerem Revisão
    with tab2:
        df_revisar = criar_df_matches(matches, status_filter='revisar')
        
        if len(df_revisar) > 0:
            st.warning(f"⚠️ {len(df_revisar)} match(es) requerem revisão manual")
            st.dataframe(df_revisar, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Nenhum match requer revisão")
    
    # TAB 3: Não Conciliados
    with tab3:
        df_nao_conc = criar_df_nao_conciliados(lancamentos, matches)
        
        if len(df_nao_conc) > 0:
            st.error(f"❌ {len(df_nao_conc)} lançamento(s) não conciliado(s)")
            st.dataframe(df_nao_conc, use_container_width=True, hide_index=True)
            
            st.info("""
            💡 **Possíveis motivos:**
            - Comprovante não encontrado
            - Diferença de valor
            - Diferença de data além da tolerância
            - Comprovante já usado em outro match
            """)
        else:
            st.success("🎉 Todos os lançamentos foram conciliados!")
    
    # TAB 4: Todos os Matches
    with tab4:
        df_todos = criar_df_matches(matches)
        
        if len(df_todos) > 0:
            st.info(f"📄 {len(df_todos)} match(es) no total")
            st.dataframe(df_todos, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Nenhum match encontrado")
    
    st.markdown("---")
    
    # ========================================================================
    # AÇÕES
    # ========================================================================
    
    st.subheader("📥 Ações")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download relatório
        if st.button("📄 Baixar Relatório (TXT)", use_container_width=True):
            motor = MotorConciliacao()
            relatorio = motor.gerar_relatorio(matches, lancamentos, formato="texto")
            
            st.download_button(
                label="💾 Download TXT",
                data=relatorio,
                file_name="relatorio_conciliacao.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    with col2:
        # Download relatório markdown
        if st.button("📝 Baixar Relatório (MD)", use_container_width=True):
            motor = MotorConciliacao()
            relatorio = motor.gerar_relatorio(matches, lancamentos, formato="markdown")
            
            st.download_button(
                label="💾 Download MD",
                data=relatorio,
                file_name="relatorio_conciliacao.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    with col3:
        # Nova conciliação
        if st.button("🔄 Nova Conciliação", type="primary", use_container_width=True):
            st.switch_page("pages/2_🔄_Conciliar.py")


if __name__ == "__main__":
    main()
