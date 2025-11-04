"""
Página de Execução da Conciliação.

Permite configurar e executar o motor de conciliação bancária.

Author: Pedro Luis (pedroluisdias@br-nsa.com)
Created: 04/11/2025
"""

import streamlit as st
from pathlib import Path
import sys
import time

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.conciliacao.motor import MotorConciliacao
from src.conciliacao.estrategias import EstrategiaExato


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

st.set_page_config(
    page_title="Conciliação - Sistema Bancário",
    page_icon="🔄",
    layout="wide"
)


# ============================================================================
# FUNÇÕES
# ============================================================================

def executar_conciliacao(lancamentos, comprovantes, config):
    """Executa a conciliação com configurações fornecidas."""
    try:
        # Criar motor
        motor = MotorConciliacao(config=config)
        
        # Adicionar estratégias
        estrategia_exato = EstrategiaExato(
            tolerancia_dias=config.get('tolerancia_dias', 3)
        )
        motor.adicionar_estrategia(estrategia_exato)
        
        # TODO: Processar comprovantes quando OCR estiver pronto
        # Por enquanto, usar lista vazia
        comprovantes_objetos = []
        
        # Conciliar
        matches = motor.conciliar(lancamentos, comprovantes_objetos)
        
        # Gerar estatísticas
        stats = motor.gerar_estatisticas(matches, lancamentos)
        
        return matches, stats, None
    
    except Exception as e:
        return None, None, str(e)


# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================

def main():
    """Página de conciliação."""
    
    st.title("🔄 Executar Conciliação")
    st.markdown("### Configure e execute a conciliação automática")
    
    st.markdown("---")
    
    # Verificar se tem dados carregados
    if not st.session_state.lancamentos:
        st.warning("⚠️ Nenhum extrato carregado!")
        st.info("Por favor, faça upload do extrato bancário primeiro.")
        
        if st.button("📤 Ir para Upload"):
            st.switch_page("pages/1_📤_Upload.py")
        
        return
    
    # Verificar se tem comprovantes
    tem_comprovantes = hasattr(st.session_state, 'comprovantes_paths') and st.session_state.comprovantes_paths
    
    if not tem_comprovantes:
        st.warning("⚠️ Nenhum comprovante carregado!")
        st.info("Por favor, faça upload dos comprovantes primeiro.")
        
        if st.button("📤 Ir para Upload"):
            st.switch_page("pages/1_📤_Upload.py")
        
        return
    
    # ========================================================================
    # CONFIGURAÇÕES
    # ========================================================================
    
    st.subheader("⚙️ Configurações da Conciliação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Parâmetros de Matching")
        
        tolerancia_dias = st.slider(
            "Tolerância de Dias",
            min_value=0,
            max_value=30,
            value=st.session_state.motor_config.get('tolerancia_dias', 3),
            help="Diferença máxima de dias entre lançamento e comprovante"
        )
        
        confianca_minima = st.slider(
            "Confiança Mínima",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.motor_config.get('confianca_minima', 0.60),
            step=0.05,
            format="%.0f%%",
            help="Confiança mínima para aceitar um match"
        )
    
    with col2:
        st.markdown("#### Classificação Automática")
        
        confianca_auto_aprovar = st.slider(
            "Auto-aprovar Acima de",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.motor_config.get('confianca_auto_aprovar', 0.90),
            step=0.05,
            format="%.0f%%",
            help="Confiança mínima para auto-aprovar match"
        )
        
        st.markdown(f"""
        **Classificação:**
        - ✅ Auto-aprovado: ≥ {confianca_auto_aprovar:.0%}
        - ⚠️ Revisar: {confianca_minima:.0%} - {confianca_auto_aprovar:.0%}
        - ❌ Rejeitar: < {confianca_minima:.0%}
        """)
    
    # Atualizar configurações
    config = {
        'tolerancia_dias': tolerancia_dias,
        'confianca_minima': confianca_minima,
        'confianca_auto_aprovar': confianca_auto_aprovar,
    }
    
    st.session_state.motor_config = config
    
    st.markdown("---")
    
    # ========================================================================
    # RESUMO DOS DADOS
    # ========================================================================
    
    st.subheader("📊 Resumo dos Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Lançamentos",
            len(st.session_state.lancamentos),
            help="Total de lançamentos no extrato"
        )
    
    with col2:
        num_comprovantes = len(st.session_state.comprovantes_paths) if tem_comprovantes else 0
        st.metric(
            "Comprovantes",
            num_comprovantes,
            help="Total de comprovantes carregados"
        )
    
    with col3:
        st.metric(
            "Estratégias",
            1,  # Por enquanto só EstrategiaExato
            help="Estratégias de matching ativas"
        )
    
    st.markdown("---")
    
    # ========================================================================
    # BOTÃO DE EXECUÇÃO
    # ========================================================================
    
    st.subheader("🚀 Executar Conciliação")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            "🔄 EXECUTAR CONCILIAÇÃO",
            type="primary",
            use_container_width=True
        ):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Etapa 1: Preparação
            status_text.text("📋 Preparando dados...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            # Etapa 2: Carregando comprovantes
            status_text.text("📄 Processando comprovantes...")
            progress_bar.progress(40)
            time.sleep(0.5)
            
            # Nota: OCR será implementado na Sprint 5
            # Por enquanto, usar lista vazia
            comprovantes_objetos = []
            
            # Etapa 3: Executando conciliação
            status_text.text("🔄 Executando conciliação...")
            progress_bar.progress(60)
            
            matches, stats, erro = executar_conciliacao(
                st.session_state.lancamentos,
                comprovantes_objetos,
                config
            )
            
            progress_bar.progress(80)
            
            if erro:
                status_text.empty()
                progress_bar.empty()
                st.error(f"❌ Erro na conciliação: {erro}")
                return
            
            # Etapa 4: Gerando relatórios
            status_text.text("📊 Gerando estatísticas...")
            progress_bar.progress(90)
            time.sleep(0.5)
            
            # Salvar resultados
            st.session_state.matches = matches
            st.session_state.stats = stats
            
            # Finalizado
            progress_bar.progress(100)
            status_text.text("✅ Conciliação concluída!")
            time.sleep(1)
            
            # Limpar
            progress_bar.empty()
            status_text.empty()
            
            # Mostrar resultados
            st.success("🎉 Conciliação executada com sucesso!")
            
            st.markdown("---")
            
            # Resultados rápidos
            st.subheader("📈 Resultados")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Taxa de Conciliação",
                    f"{stats['taxa_conciliacao']:.1%}",
                    help="Percentual de lançamentos conciliados"
                )
            
            with col2:
                st.metric(
                    "Matches Encontrados",
                    stats['total_matches'],
                    help="Total de matches encontrados"
                )
            
            with col3:
                st.metric(
                    "Confiança Média",
                    f"{stats['confianca_media']:.1%}" if stats['total_matches'] > 0 else "N/A",
                    help="Confiança média dos matches"
                )
            
            with col4:
                st.metric(
                    "Valor Conciliado",
                    f"R$ {stats['valor_total_conciliado']:,.2f}",
                    help="Valor total dos matches"
                )
            
            st.markdown("---")
            
            # Distribuição
            if stats['total_matches'] > 0:
                st.subheader("📊 Distribuição dos Matches")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "✅ Auto-aprovados",
                        stats['auto_aprovados'],
                        delta=None,
                        help=f"Confiança ≥ {confianca_auto_aprovar:.0%}"
                    )
                
                with col2:
                    st.metric(
                        "⚠️ Requerem Revisão",
                        stats['requer_revisao'],
                        delta=None,
                        help=f"Confiança entre {confianca_minima:.0%} e {confianca_auto_aprovar:.0%}"
                    )
                
                with col3:
                    nao_conciliados = stats['total_lancamentos'] - stats['total_matches']
                    st.metric(
                        "❌ Não Conciliados",
                        nao_conciliados,
                        delta=None,
                        help="Lançamentos sem match"
                    )
            
            st.markdown("---")
            
            # Botão para ver resultados
            if st.button("📊 Ver Resultados Detalhados", type="primary", use_container_width=True):
                st.switch_page("pages/3_📊_Resultados.py")
    
    # ========================================================================
    # RESULTADOS ANTERIORES
    # ========================================================================
    
    if st.session_state.matches is not None:
        st.markdown("---")
        st.info("""
        ℹ️ **Conciliação anterior encontrada**
        
        Você já executou uma conciliação. Clique em "Ver Resultados Detalhados" 
        para visualizar os matches ou execute uma nova conciliação acima.
        """)
        
        if st.button("📊 Ver Última Conciliação"):
            st.switch_page("pages/3_📊_Resultados.py")


if __name__ == "__main__":
    main()
