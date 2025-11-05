"""
Sistema de Conciliação Bancária - Interface Web.

Aplicação principal Streamlit que serve como página inicial
do sistema de conciliação bancária.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Created: 04/11/2025
Version: 1.0.0
"""

import streamlit as st
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Conciliação Bancária",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/seu-usuario/conciliacao-bancaria',
        'Report a bug': 'https://github.com/seu-usuario/conciliacao-bancaria/issues',
        'About': '''
        # Sistema de Conciliação Bancária v1.0
        
        Sistema automatizado para conciliar extratos bancários
        com comprovantes de pagamento.
        
        **Desenvolvido por:** Pedro Luis
        '''
    }
)


# ============================================================================
# INICIALIZAR SESSION STATE
# ============================================================================

def init_session_state():
    """Inicializa variáveis de sessão."""
    if 'lancamentos' not in st.session_state:
        st.session_state.lancamentos = None
    
    if 'comprovantes' not in st.session_state:
        st.session_state.comprovantes = None
    
    if 'matches' not in st.session_state:
        st.session_state.matches = None
    
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    
    if 'motor_config' not in st.session_state:
        st.session_state.motor_config = {
            'confianca_minima': 0.60,
            'confianca_auto_aprovar': 0.90,
            'tolerancia_dias': 3,
        }


# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Renderiza sidebar com navegação e estatísticas."""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/0066cc/ffffff?text=Sistema+de+Conciliação", 
                 use_column_width=True)
        
        st.title("🏦 Conciliação Bancária")
        st.markdown("---")
        
        # Navegação
        st.subheader("📍 Navegação")
        st.page_link("app.py", label="🏠 Home", icon="🏠")
        st.page_link("pages/1_📤_Upload.py", label="Upload de Arquivos", icon="📤")
        st.page_link("pages/2_🔄_Conciliar.py", label="Executar Conciliação", icon="🔄")
        st.page_link("pages/3_📊_Resultados.py", label="Ver Resultados", icon="📊")
        st.page_link("pages/5_📋_Regras.py", label="📋 Regras de Auto-Conciliação")
        
        st.markdown("---")
        
        # Estatísticas rápidas
        st.subheader("📈 Status Atual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.lancamentos:
                st.metric("Lançamentos", len(st.session_state.lancamentos))
            else:
                st.metric("Lançamentos", "0")
        
        with col2:
            if st.session_state.comprovantes:
                st.metric("Comprovantes", len(st.session_state.comprovantes))
            else:
                st.metric("Comprovantes", "0")
        
        if st.session_state.stats:
            st.metric(
                "Taxa de Conciliação",
                f"{st.session_state.stats['taxa_conciliacao']:.1%}",
                delta=None
            )
            st.metric(
                "Confiança Média",
                f"{st.session_state.stats['confianca_media']:.1%}",
                delta=None
            )
        
        st.markdown("---")
        
        # Configurações rápidas
        with st.expander("⚙️ Configurações"):
            st.session_state.motor_config['confianca_minima'] = st.slider(
                "Confiança Mínima",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.motor_config['confianca_minima'],
                step=0.05,
                help="Confiança mínima para aceitar um match"
            )
            
            st.session_state.motor_config['confianca_auto_aprovar'] = st.slider(
                "Auto-aprovar Acima de",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.motor_config['confianca_auto_aprovar'],
                step=0.05,
                help="Confiança mínima para auto-aprovar match"
            )
            
            st.session_state.motor_config['tolerancia_dias'] = st.number_input(
                "Tolerância de Dias",
                min_value=0,
                max_value=30,
                value=st.session_state.motor_config['tolerancia_dias'],
                help="Diferença máxima de dias entre lançamento e comprovante"
            )
        
        st.markdown("---")
        st.caption("v1.0.0 | Pedro Luis")


# ============================================================================
# PÁGINA PRINCIPAL (HOME)
# ============================================================================

def main():
    """Página principal da aplicação."""
    
    # Inicializar session state
    init_session_state()
    
    # Renderizar sidebar
    render_sidebar()
    
    # Conteúdo principal
    st.title("🏦 Sistema de Conciliação Bancária")
    st.markdown("### Automatize a conciliação de extratos bancários com comprovantes")
    
    st.markdown("---")
    
    # Cards informativos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📤 1. Upload
        
        Faça upload do seu extrato bancário (CSV) e dos 
        comprovantes de pagamento (PDF).
        
        [Ir para Upload →](./pages/1_📤_Upload.py)
        """)
    
    with col2:
        st.markdown("""
        ### 🔄 2. Conciliar
        
        Execute a conciliação automática com configurações
        personalizadas.
        
        [Ir para Conciliação →](./pages/2_🔄_Conciliar.py)
        """)
    
    with col3:
        st.markdown("""
        ### 📊 3. Resultados
        
        Visualize os matches encontrados, estatísticas
        e exporte relatórios.
        
        [Ver Resultados →](./pages/3_📊_Resultados.py)
        """)
    
    st.markdown("---")
    
    # Informações sobre o sistema
    st.subheader("ℹ️ Sobre o Sistema")
    
    with st.expander("Como funciona?", expanded=False):
        st.markdown("""
        O sistema realiza a conciliação em 3 etapas:
        
        1. **Leitura de Dados**
           - Extrato bancário (CSV)
           - Comprovantes de pagamento (PDF com OCR)
        
        2. **Matching Inteligente**
           - Compara valores e datas
           - Calcula confiança do match (0% a 100%)
           - Aplica múltiplas estratégias
        
        3. **Classificação**
           - ✅ Auto-aprovados (confiança ≥ 90%)
           - ⚠️ Revisar (confiança 60-90%)
           - ❌ Sem match (confiança < 60%)
        """)
    
    with st.expander("Métricas de Sucesso", expanded=False):
        st.markdown("""
        ### 🎯 Metas do Sistema
        
        - **Taxa de Conciliação:** 60-70% automática
        - **Precisão:** >95% de matches corretos
        - **Performance:** <5 segundos para 100 lançamentos
        - **Redução de Tempo:** 70% menos trabalho manual
        """)
    
    with st.expander("Formatos Suportados", expanded=False):
        st.markdown("""
        ### 📄 Arquivos Aceitos
        
        **Extratos Bancários:**
        - CSV (Itaú, Bradesco, Santander, Banco do Brasil, genérico)
        - Excel (XLSX)
        - PDF com texto extraível
        
        **Comprovantes:**
        - PDF com texto
        - PDF escaneado (com OCR)
        - Imagens PNG/JPG (com OCR)
        """)
    
    # Estatísticas do projeto
    st.markdown("---")
    st.subheader("📊 Estatísticas do Projeto")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Linhas de Código", "5.906")
    
    with col2:
        st.metric("Testes Automatizados", "99")
    
    with col3:
        st.metric("Taxa de Sucesso", "100%")
    
    with col4:
        st.metric("Progresso MVP", "50%")
    
    st.markdown("---")
    
    # Início rápido
    st.subheader("🚀 Início Rápido")
    
    st.markdown("""
    1. Clique em **📤 Upload de Arquivos** no menu lateral
    2. Faça upload do seu extrato bancário (CSV)
    3. Faça upload dos comprovantes (PDF)
    4. Clique em **🔄 Executar Conciliação**
    5. Veja os resultados em **📊 Ver Resultados**
    """)
    
    # Botão de ação
    st.markdown("")
    if st.button("🚀 Começar Agora", type="primary", use_container_width=True):
        st.switch_page("pages/1_📤_Upload.py")
    
    # Footer
    st.markdown("---")
    st.caption("""
    Sistema de Conciliação Bancária v1.0.0 | 
    Desenvolvido por Pedro Luis | 
    Sprint 4 - Interface Web
    """)


if __name__ == "__main__":
    main()
