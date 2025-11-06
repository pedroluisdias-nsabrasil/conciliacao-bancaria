"""
Pagina de Upload de Arquivos.

Permite upload de extratos bancarios (CSV) e comprovantes (PDF).
"""
import sys
from pathlib import Path

# Setup PYTHONPATH
arquivo_atual = Path(__file__).resolve()
raiz = arquivo_atual.parent.parent.parent
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))
if str(raiz / 'src') not in sys.path:
    sys.path.insert(0, str(raiz / 'src'))

import streamlit as st
from src.ingestao import LeitorCSV
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Upload - Conciliacao Bancaria",
    page_icon="💰",
    layout="wide"
)

def init_session_state():
    """Inicializa session state."""
    if 'lancamentos' not in st.session_state:
        st.session_state.lancamentos = []
    if 'comprovantes_paths' not in st.session_state:
        st.session_state.comprovantes_paths = []

def main():
    """Pagina principal de upload."""
    init_session_state()
    
    st.title("Upload de Arquivos")
    st.markdown("Faca upload do extrato bancario e dos comprovantes")
    st.markdown("---")
    
    # Upload Extrato
    st.subheader("1. Extrato Bancario (CSV)")
    
    arquivo_csv = st.file_uploader(
        "Selecione o arquivo CSV do extrato",
        type=['csv'],
        help="Arquivo CSV exportado do banco"
    )
    
    if arquivo_csv:
        try:
            # Salvar temporariamente
            caminho_temp = f"dados/entrada/extratos/{arquivo_csv.name}"
            Path("dados/entrada/extratos").mkdir(parents=True, exist_ok=True)
            
            with open(caminho_temp, 'wb') as f:
                f.write(arquivo_csv.getbuffer())
            
            # Ler com LeitorCSV
            leitor = LeitorCSV()
            lancamentos = leitor.ler_arquivo(caminho_temp)
            
            st.session_state.lancamentos = lancamentos
            
            st.success(f"Extrato carregado: {len(lancamentos)} lancamentos")
            
            # Preview
            if st.checkbox("Visualizar lancamentos"):
                import pandas as pd
                df = pd.DataFrame([
                    {
                        'Data': l.data.strftime('%d/%m/%Y'),
                        'Descricao': l.descricao[:50],
                        'Valor': f"R$ {l.valor:,.2f}",
                        'Tipo': l.tipo
                    }
                    for l in lancamentos[:10]
                ])
                st.dataframe(df, use_container_width=True)
                if len(lancamentos) > 10:
                    st.info(f"Mostrando 10 de {len(lancamentos)} lancamentos")
        
        except Exception as e:
            st.error(f"Erro ao processar extrato: {e}")
            logger.error(f"Erro: {e}", exc_info=True)
    
    st.markdown("---")
    
    # Upload Comprovantes
    st.subheader("2. Comprovantes de Pagamento (PDF)")
    
    arquivos_pdf = st.file_uploader(
        "Selecione os comprovantes (multiplos arquivos)",
        type=['pdf'],
        accept_multiple_files=True,
        help="Comprovantes em PDF (com texto ou escaneados)"
    )
    
    if arquivos_pdf:
        try:
            Path("dados/entrada/comprovantes").mkdir(parents=True, exist_ok=True)
            
            caminhos = []
            for arquivo in arquivos_pdf:
                caminho = f"dados/entrada/comprovantes/{arquivo.name}"
                with open(caminho, 'wb') as f:
                    f.write(arquivo.getbuffer())
                caminhos.append(caminho)
            
            st.session_state.comprovantes_paths = caminhos
            
            st.success(f"Comprovantes carregados: {len(caminhos)} arquivos")
            
            # Lista de arquivos
            if st.checkbox("Ver lista de comprovantes"):
                for i, caminho in enumerate(caminhos, 1):
                    st.text(f"{i}. {Path(caminho).name}")
        
        except Exception as e:
            st.error(f"Erro ao salvar comprovantes: {e}")
            logger.error(f"Erro: {e}", exc_info=True)
    
    st.markdown("---")
    
    # Resumo
    st.subheader("Resumo dos Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Lancamentos Carregados",
            len(st.session_state.lancamentos)
        )
    
    with col2:
        st.metric(
            "Comprovantes Enviados",
            len(st.session_state.comprovantes_paths)
        )
    
    with col3:
        cobertura = 0
        if st.session_state.lancamentos:
            cobertura = (len(st.session_state.comprovantes_paths) / 
                        len(st.session_state.lancamentos) * 100)
        st.metric(
            "Cobertura Potencial",
            f"{cobertura:.0f}%"
        )
    
    # Botao para proximo passo
    st.markdown("")
    if (st.session_state.lancamentos and 
        st.session_state.comprovantes_paths):
        if st.button("Proximo: Executar Conciliacao", 
                    type="primary", 
                    use_container_width=True):
            st.switch_page("pages/2_🔄_Conciliar.py")
    else:
        st.info("Carregue o extrato e os comprovantes para continuar")

if __name__ == "__main__":
    main()