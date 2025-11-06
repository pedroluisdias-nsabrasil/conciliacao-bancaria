"""
Pagina de Resultados.

Exibe os resultados da conciliacao.
"""
import sys
from pathlib import Path

arquivo_atual = Path(__file__).resolve()
raiz = arquivo_atual.parent.parent.parent
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))
if str(raiz / 'src') not in sys.path:
    sys.path.insert(0, str(raiz / 'src'))

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Resultados - Conciliacao Bancaria",
    page_icon="💰",
    layout="wide"
)

def init_session_state():
    """Inicializa session state."""
    if 'matches' not in st.session_state:
        st.session_state.matches = []
    if 'lancamentos' not in st.session_state:
        st.session_state.lancamentos = []

def main():
    """Pagina principal de resultados."""
    init_session_state()
    
    st.title("Resultados da Conciliacao")
    st.markdown("Visualize os matches encontrados e estatisticas")
    st.markdown("---")
    
    # Verificar se tem resultados
    if not st.session_state.matches:
        st.info("Nenhuma conciliacao realizada ainda!")
        st.markdown("Execute a conciliacao primeiro na pagina Conciliar")
        if st.button("Ir para Conciliar"):
            st.switch_page("pages/2_🔄_Conciliar.py")
        return
    
    # Estatisticas
    matches = st.session_state.matches
    total_lanc = len(st.session_state.lancamentos)
    conciliados = [m for m in matches if m.conciliado]
    
    st.subheader("Estatisticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Lancamentos", total_lanc)
    
    with col2:
        st.metric("Conciliados", len(conciliados))
    
    with col3:
        taxa = (len(conciliados) / total_lanc * 100) if total_lanc > 0 else 0
        st.metric("Taxa de Conciliacao", f"{taxa:.1f}%")
    
    with col4:
        if conciliados:
            conf_media = sum(m.confianca for m in conciliados) / len(conciliados)
            st.metric("Confianca Media", f"{conf_media:.0%}")
        else:
            st.metric("Confianca Media", "N/A")
    
    st.markdown("---")
    
    # Tabs de resultados
    tab1, tab2 = st.tabs(["Conciliados", "Nao Conciliados"])
    
    with tab1:
        st.subheader(f"Lancamentos Conciliados ({len(conciliados)})")
        
        if conciliados:
            dados = []
            for m in conciliados:
                lanc = next((l for l in st.session_state.lancamentos if l.id == m.lancamento_id), None)
                if lanc:
                    dados.append({
                        'Data': lanc.data.strftime('%d/%m/%Y'),
                        'Descricao': lanc.descricao[:40],
                        'Valor': f"R$ {lanc.valor:,.2f}",
                        'Confianca': f"{m.confianca:.0%}",
                        'Metodo': m.metodo,
                        'Comprovante': Path(m.comprovante_arquivo).name if m.comprovante_arquivo else 'N/A'
                    })
            
            df = pd.DataFrame(dados)
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info("Nenhum lancamento conciliado")
    
    with tab2:
        nao_conciliados = [l for l in st.session_state.lancamentos 
                          if not any(m.lancamento_id == l.id and m.conciliado for m in matches)]
        
        st.subheader(f"Lancamentos Nao Conciliados ({len(nao_conciliados)})")
        
        if nao_conciliados:
            dados = []
            for lanc in nao_conciliados:
                dados.append({
                    'Data': lanc.data.strftime('%d/%m/%Y'),
                    'Descricao': lanc.descricao[:50],
                    'Valor': f"R$ {lanc.valor:,.2f}",
                    'Tipo': lanc.tipo
                })
            
            df = pd.DataFrame(dados)
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.success("Todos os lancamentos foram conciliados!")
    
    st.markdown("---")
    
    # Botao relatorios
    if st.button("Gerar Relatorio Completo", type="primary", use_container_width=True):
        st.switch_page("pages/4_📄_Relatorios.py")

if __name__ == "__main__":
    main()