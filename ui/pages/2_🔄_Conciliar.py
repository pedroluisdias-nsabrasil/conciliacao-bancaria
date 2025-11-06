"""
Pagina de Conciliacao.

Executa o processo de conciliacao automatica.
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
from src.conciliacao import MotorConciliacao
from src.ingestao import LeitorOCR
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Conciliar - Conciliacao Bancaria",
    page_icon="💰",
    layout="wide"
)

def init_session_state():
    """Inicializa session state."""
    if 'lancamentos' not in st.session_state:
        st.session_state.lancamentos = []
    if 'comprovantes_paths' not in st.session_state:
        st.session_state.comprovantes_paths = []
    if 'matches' not in st.session_state:
        st.session_state.matches = []

def executar_conciliacao():
    """Executa o processo de conciliacao."""
    try:
        # Fase 1: Processar comprovantes com OCR
        st.info("Fase 1/2: Processando comprovantes PDF com OCR...")
        
        leitor_ocr = LeitorOCR(confianca_minima=0.6)
        logger.info("LeitorOCR inicializado com sucesso")
        
        comprovantes_objetos = []
        total = len(st.session_state.comprovantes_paths)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, caminho in enumerate(st.session_state.comprovantes_paths):
            status_text.text(f"Processando {idx+1}/{total}: {Path(caminho).name}")
            progress_bar.progress((idx + 1) / total)
            
            comp = leitor_ocr.ler_arquivo(str(caminho))
            if comp:
                comprovantes_objetos.append(comp)
                logger.info(f"Extraido: R$ {comp.valor} em {comp.data} (confianca: {comp.confianca_ocr:.0%})")
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"Comprovantes processados: {len(comprovantes_objetos)}/{total}")
        
        # Fase 2: Executar conciliacao
        st.info("Fase 2/2: Executando motor de conciliacao...")
        
        motor = MotorConciliacao()
        
        inicio = datetime.now()
        matches = motor.conciliar(
            st.session_state.lancamentos,
            comprovantes_objetos
        )
        tempo_exec = (datetime.now() - inicio).total_seconds()
        
        st.session_state.matches = matches
        
        # Estatisticas
        total_lanc = len(st.session_state.lancamentos)
        total_matches = len([m for m in matches if m.conciliado])
        taxa = (total_matches / total_lanc * 100) if total_lanc > 0 else 0
        
        st.success("Conciliacao concluida com sucesso!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Matches Encontrados", f"{total_matches}/{total_lanc}")
        with col2:
            st.metric("Taxa de Conciliacao", f"{taxa:.1f}%")
        with col3:
            st.metric("Tempo de Execucao", f"{tempo_exec:.1f}s")
        
        # Botao para ver resultados
        if st.button("Ver Resultados Detalhados", type="primary", use_container_width=True):
            st.switch_page("pages/3_📊_Resultados.py")
    
    except Exception as e:
        st.error(f"Erro durante conciliacao: {e}")
        logger.error(f"Erro: {e}", exc_info=True)

def main():
    """Pagina principal de conciliacao."""
    init_session_state()
    
    st.title("Executar Conciliacao")
    st.markdown("Configure e execute a conciliacao automatica")
    st.markdown("---")
    
    # Verificar dados
    if not st.session_state.lancamentos:
        st.warning("Nenhum lancamento carregado!")
        st.info("Va para a pagina Upload para carregar o extrato")
        if st.button("Ir para Upload"):
            st.switch_page("pages/1_📤_Upload.py")
        return
    
    if not st.session_state.comprovantes_paths:
        st.warning("Nenhum comprovante carregado!")
        st.info("Va para a pagina Upload para carregar os comprovantes")
        if st.button("Ir para Upload"):
            st.switch_page("pages/1_📤_Upload.py")
        return
    
    # Resumo dos dados
    st.subheader("Resumo dos Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Lancamentos Carregados", len(st.session_state.lancamentos))
    
    with col2:
        st.metric("Comprovantes Enviados", len(st.session_state.comprovantes_paths))
    
    with col3:
        cobertura = (len(st.session_state.comprovantes_paths) / 
                    len(st.session_state.lancamentos) * 100)
        st.metric("Cobertura Potencial", f"{cobertura:.0f}%")
    
    st.markdown("---")
    
    # Configuracoes
    st.subheader("Configuracoes da Conciliacao")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tolerancia_dias = st.number_input(
            "Tolerancia de Dias",
            min_value=0,
            max_value=30,
            value=3,
            help="Diferenca maxima de dias entre lancamento e comprovante"
        )
    
    with col2:
        tolerancia_valor = st.number_input(
            "Tolerancia de Valor (R$)",
            min_value=0.0,
            max_value=10.0,
            value=0.50,
            step=0.10,
            help="Diferenca maxima de valor"
        )
    
    with col3:
        confianca_minima = st.slider(
            "Confianca Minima (%)",
            min_value=0,
            max_value=100,
            value=60,
            help="Confianca minima para aceitar um match"
        )
    
    st.markdown("---")
    
    # Botao executar
    st.subheader("Executar Conciliacao")
    
    if st.button("Executar Conciliacao", type="primary", use_container_width=True):
        executar_conciliacao()

if __name__ == "__main__":
    main()