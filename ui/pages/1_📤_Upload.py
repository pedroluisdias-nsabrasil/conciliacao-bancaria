"""
Página de Upload de Arquivos.

Permite upload de extratos bancários (CSV) e comprovantes (PDF)
para o sistema de conciliação.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Created: 04/11/2025
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import date

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.ingestao import LeitorCSV, LeitorPDF


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

st.set_page_config(
    page_title="Upload - Conciliação Bancária",
    page_icon="📤",
    layout="wide"
)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def processar_extrato_csv(arquivo):
    """Processa arquivo CSV de extrato bancário."""
    try:
        # Salvar arquivo temporariamente
        temp_path = Path("dados/entrada/extratos") / arquivo.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(arquivo.getbuffer())
        
        # Ler com LeitorCSV
        leitor = LeitorCSV()
        lancamentos = leitor.ler_arquivo(str(temp_path))
        
        return lancamentos, None
    
    except Exception as e:
        return None, str(e)


def processar_comprovante_pdf(arquivo):
    """Processa arquivo PDF de comprovante."""
    try:
        # Salvar arquivo temporariamente
        temp_path = Path("dados/entrada/comprovantes") / arquivo.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(arquivo.getbuffer())
        
        # Por enquanto, apenas salva
        # OCR será implementado depois
        return str(temp_path), None
    
    except Exception as e:
        return None, str(e)


def criar_dataframe_lancamentos(lancamentos):
    """Converte lista de lançamentos em DataFrame para exibição."""
    if not lancamentos:
        return pd.DataFrame()
    
    data = []
    for lanc in lancamentos:
        data.append({
            'Data': lanc.data.strftime('%d/%m/%Y'),
            'Tipo': 'Débito' if lanc.tipo == 'D' else 'Crédito',
            'Valor': f"R$ {lanc.valor:,.2f}",
            'Descrição': lanc.descricao,
            'Saldo': f"R$ {lanc.saldo:,.2f}" if lanc.saldo else "-"
        })
    
    return pd.DataFrame(data)


# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

def main():
    """Página de upload de arquivos."""
    
    st.title("📤 Upload de Arquivos")
    st.markdown("### Faça upload do extrato bancário e dos comprovantes")
    
    st.markdown("---")
    
    # Tabs para Upload
    tab1, tab2 = st.tabs(["🏦 Extrato Bancário", "📄 Comprovantes"])
    
    # ========================================================================
    # TAB 1: EXTRATO BANCÁRIO
    # ========================================================================
    
    with tab1:
        st.subheader("Upload de Extrato Bancário")
        
        st.info("""
        **Formatos aceitos:** CSV, Excel (XLSX)
        
        **Bancos suportados:** Itaú, Bradesco, Santander, Banco do Brasil, formato genérico
        """)
        
        arquivo_extrato = st.file_uploader(
            "Selecione o arquivo do extrato",
            type=['csv', 'xlsx'],
            accept_multiple_files=False,
            help="Arquivo CSV ou Excel com os lançamentos bancários"
        )
        
        if arquivo_extrato:
            with st.spinner("Processando extrato..."):
                lancamentos, erro = processar_extrato_csv(arquivo_extrato)
                
                if erro:
                    st.error(f"❌ Erro ao processar extrato: {erro}")
                else:
                    st.success(f"✅ Extrato processado com sucesso!")
                    
                    # Salvar em session state
                    st.session_state.lancamentos = lancamentos
                    
                    # Estatísticas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total de Lançamentos", len(lancamentos))
                    
                    with col2:
                        debitos = sum(1 for l in lancamentos if l.tipo == 'D')
                        st.metric("Débitos", debitos)
                    
                    with col3:
                        creditos = sum(1 for l in lancamentos if l.tipo == 'C')
                        st.metric("Créditos", creditos)
                    
                    with col4:
                        valor_total = sum(l.valor for l in lancamentos if l.tipo == 'D')
                        st.metric("Valor Total Débitos", f"R$ {valor_total:,.2f}")
                    
                    # Preview dos dados
                    st.markdown("---")
                    st.subheader("📋 Preview dos Lançamentos")
                    
                    df = criar_dataframe_lancamentos(lancamentos)
                    
                    # Mostrar apenas primeiros e últimos 5
                    if len(df) > 10:
                        st.dataframe(
                            df.head(10),
                            use_container_width=True,
                            hide_index=True
                        )
                        st.caption(f"Mostrando 10 de {len(df)} lançamentos")
                    else:
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )
        
        # Se já tem lançamentos carregados
        elif st.session_state.lancamentos:
            st.info(f"✅ Extrato já carregado: {len(st.session_state.lancamentos)} lançamentos")
            
            if st.button("🔄 Carregar Novo Extrato"):
                st.session_state.lancamentos = None
                st.rerun()
    
    # ========================================================================
    # TAB 2: COMPROVANTES
    # ========================================================================
    
    with tab2:
        st.subheader("Upload de Comprovantes")
        
        st.info("""
        **Formatos aceitos:** PDF
        
        **Observação:** Você pode fazer upload de múltiplos comprovantes de uma vez.
        """)
        
        arquivos_comprovantes = st.file_uploader(
            "Selecione os comprovantes",
            type=['pdf'],
            accept_multiple_files=True,
            help="Arquivos PDF dos comprovantes de pagamento"
        )
        
        if arquivos_comprovantes:
            st.success(f"✅ {len(arquivos_comprovantes)} arquivo(s) selecionado(s)")
            
            # Processar cada arquivo
            comprovantes_paths = []
            
            with st.spinner("Salvando comprovantes..."):
                for arquivo in arquivos_comprovantes:
                    path, erro = processar_comprovante_pdf(arquivo)
                    
                    if erro:
                        st.warning(f"⚠️ Erro em {arquivo.name}: {erro}")
                    else:
                        comprovantes_paths.append(path)
            
            if comprovantes_paths:
                st.success(f"✅ {len(comprovantes_paths)} comprovante(s) salvo(s)")
                
                # Salvar em session state
                st.session_state.comprovantes_paths = comprovantes_paths
                
                # Lista de arquivos
                st.markdown("---")
                st.subheader("📄 Comprovantes Carregados")
                
                for i, path in enumerate(comprovantes_paths, 1):
                    nome = Path(path).name
                    st.text(f"{i}. {nome}")
        
        # Se já tem comprovantes carregados
        elif hasattr(st.session_state, 'comprovantes_paths'):
            st.info(f"✅ {len(st.session_state.comprovantes_paths)} comprovante(s) já carregado(s)")
            
            if st.button("🔄 Carregar Novos Comprovantes"):
                st.session_state.comprovantes_paths = None
                st.rerun()
    
    # ========================================================================
    # BOTÕES DE AÇÃO
    # ========================================================================
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Verificar se tem dados carregados
        tem_lancamentos = st.session_state.lancamentos is not None
        tem_comprovantes = hasattr(st.session_state, 'comprovantes_paths') and st.session_state.comprovantes_paths
        
        if tem_lancamentos and tem_comprovantes:
            st.success("✅ Dados carregados! Pronto para conciliar.")
            
            if st.button("🔄 Ir para Conciliação", type="primary", use_container_width=True):
                st.switch_page("pages/2_🔄_Conciliar.py")
        
        elif tem_lancamentos and not tem_comprovantes:
            st.warning("⚠️ Falta carregar os comprovantes")
        
        elif not tem_lancamentos and tem_comprovantes:
            st.warning("⚠️ Falta carregar o extrato bancário")
        
        else:
            st.info("ℹ️ Carregue o extrato e os comprovantes para continuar")


if __name__ == "__main__":
    main()
