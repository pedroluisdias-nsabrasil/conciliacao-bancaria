"""
Página de Resultados - Sistema de Conciliação Bancária
Versão atualizada com suporte a download de PDF

Modificações:
- Adicionado checkbox para PDF
- Implementado botão de download PDF
- Integração com GeradorPDF
"""

import setup_path  # Configurar path para imports
import streamlit as st
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from typing import List, Dict, Optional
import logging

# Imports do sistema
from src.relatorios import GeradorExcel, GeradorPDF
from src.modelos import Match, Lancamento

logger = logging.getLogger(__name__)


def configurar_pagina():
    """Configura a página de resultados."""
    st.set_page_config(
        page_title="Resultados - Conciliação Bancária",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Resultados da Conciliação")


def render_metricas(stats: Dict):
    """Renderiza as métricas principais."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Lançamentos",
            stats.get('total_lancamentos', 0),
            help="Número total de lançamentos no extrato"
        )
    
    with col2:
        auto_aprovados = stats.get('auto_aprovados', 0)
        st.metric(
            "Auto-Aprovados",
            auto_aprovados,
            help="Matches com confiança ≥90%"
        )
    
    with col3:
        revisar = stats.get('revisar', 0)
        st.metric(
            "A Revisar",
            revisar,
            help="Matches com confiança 60-89%"
        )
    
    with col4:
        nao_conciliados = stats.get('nao_conciliados', 0)
        st.metric(
            "Não Conciliados",
            nao_conciliados,
            help="Lançamentos sem match"
        )
    
    # Taxa de conciliação
    taxa = stats.get('taxa_conciliacao', 0) * 100
    st.progress(taxa / 100, text=f"Taxa de Conciliação: {taxa:.1f}%")


def render_matches(matches: List[Match]):
    """Renderiza a tabela de matches."""
    if not matches:
        st.info("Nenhum match encontrado.")
        return
    
    st.subheader(f"✅ Matches Encontrados ({len(matches)})")
    
    # Preparar dados para tabela
    dados_tabela = []
    for match in matches:
        dados_tabela.append({
            "Data": match.lancamento.data.strftime("%d/%m/%Y"),
            "Valor": f"R$ {match.lancamento.valor:,.2f}",
            "Descrição": match.lancamento.descricao,
            "Comprovante": match.comprovante.arquivo,
            "Confiança": f"{match.confianca * 100:.1f}%",
            "Método": match.metodo,
            "Status": "🟢 Auto-aprovar" if match.confianca >= 0.9 else "🟡 Revisar"
        })
    
    st.dataframe(
        dados_tabela,
        use_container_width=True,
        hide_index=True
    )


def render_nao_conciliados(lancamentos: List[Lancamento]):
    """Renderiza lançamentos não conciliados."""
    if not lancamentos:
        st.success("🎉 Todos os lançamentos foram conciliados!")
        return
    
    st.subheader(f"🔴 Não Conciliados ({len(lancamentos)})")
    
    dados_tabela = []
    for lanc in lancamentos:
        dados_tabela.append({
            "Data": lanc.data.strftime("%d/%m/%Y"),
            "Tipo": "Débito" if lanc.tipo == 'D' else "Crédito",
            "Valor": f"R$ {lanc.valor:,.2f}",
            "Descrição": lanc.descricao,
            "Saldo": f"R$ {lanc.saldo:,.2f}" if lanc.saldo else "-"
        })
    
    st.dataframe(
        dados_tabela,
        use_container_width=True,
        hide_index=True
    )


def render_exportar_relatorios(
    matches: List[Match],
    lancamentos_nao_conciliados: List[Lancamento],
    estatisticas: Dict
):
    """
    Renderiza a seção de exportação de relatórios.
    
    NOVA FUNCIONALIDADE: Agora com suporte a PDF!
    """
    st.markdown("---")
    st.subheader("📥 Exportar Relatórios")
    
    st.write("Escolha os formatos desejados:")
    
    # Opções de formato
    col1, col2 = st.columns(2)
    
    with col1:
        formato_excel = st.checkbox(
            "📊 Excel (.xlsx)",
            value=True,
            help="Relatório Excel com 3 abas: Resumo, Conciliados e Não Conciliados"
        )
    
    with col2:
        formato_pdf = st.checkbox(
            "📄 PDF (.pdf)",
            value=True,
            help="Relatório PDF profissional com gráficos e tabelas"
        )
    
    # Nome do arquivo
    nome_padrao = f"conciliacao_{datetime.now().strftime('%Y%m%d_%H%M')}"
    nome_base = st.text_input(
        "Nome do arquivo (sem extensão)",
        value=nome_padrao,
        help="O sistema adiciona automaticamente a extensão (.xlsx ou .pdf)"
    )
    
    # Validar nome
    if not nome_base:
        st.warning("⚠️ Por favor, informe um nome para o arquivo.")
        return
    
    # Botão de geração
    if st.button("🚀 Gerar Relatórios", type="primary", use_container_width=True):
        
        if not formato_excel and not formato_pdf:
            st.warning("⚠️ Selecione pelo menos um formato!")
            return
        
        try:
            # Garantir que o diretório existe
            pasta_saida = Path("dados/saida")
            pasta_saida.mkdir(parents=True, exist_ok=True)
            
            arquivos_gerados = []
            
            with st.spinner("Gerando relatórios... ⏳"):
                
                # ========================================
                # GERAR EXCEL
                # ========================================
                if formato_excel:
                    try:
                        arquivo_excel = pasta_saida / f"{nome_base}.xlsx"
                        
                        gerador_excel = GeradorExcel()
                        gerador_excel.gerar(
                            matches=matches,
                            lancamentos_nao_conciliados=lancamentos_nao_conciliados,
                            estatisticas=estatisticas,
                            arquivo_saida=str(arquivo_excel)
                        )
                        
                        arquivos_gerados.append(("Excel", arquivo_excel))
                        st.success(f"✅ Excel gerado: {arquivo_excel.name}")
                        
                    except Exception as e:
                        logger.error(f"Erro ao gerar Excel: {e}")
                        st.error(f"❌ Erro ao gerar Excel: {e}")
                
                # ========================================
                # GERAR PDF - NOVA FUNCIONALIDADE! 🎉
                # ========================================
                if formato_pdf:
                    try:
                        arquivo_pdf = pasta_saida / f"{nome_base}.pdf"
                        
                        gerador_pdf = GeradorPDF()
                        gerador_pdf.gerar(
                            matches=matches,
                            lancamentos_nao_conciliados=lancamentos_nao_conciliados,
                            estatisticas=estatisticas,
                            arquivo_saida=str(arquivo_pdf)
                        )
                        
                        arquivos_gerados.append(("PDF", arquivo_pdf))
                        st.success(f"✅ PDF gerado: {arquivo_pdf.name}")
                        
                    except Exception as e:
                        logger.error(f"Erro ao gerar PDF: {e}")
                        st.error(f"❌ Erro ao gerar PDF: {e}")
            
            # ========================================
            # BOTÕES DE DOWNLOAD
            # ========================================
            if arquivos_gerados:
                st.markdown("---")
                st.write("**📥 Baixar Relatórios:**")
                
                cols = st.columns(len(arquivos_gerados))
                
                for idx, (tipo, arquivo) in enumerate(arquivos_gerados):
                    with cols[idx]:
                        with open(arquivo, 'rb') as f:
                            conteudo = f.read()
                        
                        # Definir MIME type
                        if tipo == "Excel":
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            icone = "📊"
                        else:  # PDF
                            mime_type = "application/pdf"
                            icone = "📄"
                        
                        st.download_button(
                            label=f"{icone} Baixar {tipo}",
                            data=conteudo,
                            file_name=arquivo.name,
                            mime=mime_type,
                            use_container_width=True
                        )
                
                st.success("✅ Relatórios prontos para download!")
                
        except Exception as e:
            logger.error(f"Erro ao gerar relatórios: {e}")
            st.error(f"❌ Erro ao gerar relatórios: {e}")


def main():
    """Função principal da página."""
    configurar_pagina()
    
    # Verificar se há resultados em session_state
    if 'resultado_conciliacao' not in st.session_state:
        st.info("ℹ️ Nenhum resultado disponível. Execute a conciliação primeiro na página Upload.")
        st.page_link("pages/1_📤_Upload.py", label="Ir para Upload", icon="📤")
        return
    
    resultado = st.session_state.resultado_conciliacao
    
    # Preparar dados
    matches = resultado.get('matches', [])
    matches_automaticos = [m for m in matches if m.confianca >= 0.9]
    matches_revisar = [m for m in matches if 0.6 <= m.confianca < 0.9]
    todos_matches = matches_automaticos + matches_revisar
    
    lancamentos_nao_conciliados = resultado.get('lancamentos_nao_conciliados', [])
    
    # Estatísticas
    total_lancamentos = len(todos_matches) + len(lancamentos_nao_conciliados)
    
    estatisticas = {
        'total_lancamentos': total_lancamentos,
        'auto_aprovados': len(matches_automaticos),
        'revisar': len(matches_revisar),
        'nao_conciliados': len(lancamentos_nao_conciliados),
        'taxa_conciliacao': len(todos_matches) / total_lancamentos if total_lancamentos > 0 else 0,
        'tempo_execucao': resultado.get('tempo_execucao', 0)
    }
    
    # Renderizar seções
    render_metricas(estatisticas)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2 = st.tabs(["✅ Conciliados", "🔴 Não Conciliados"])
    
    with tab1:
        render_matches(todos_matches)
    
    with tab2:
        render_nao_conciliados(lancamentos_nao_conciliados)
    
    # ========================================
    # SEÇÃO DE EXPORTAÇÃO - ATUALIZADA COM PDF!
    # ========================================
    render_exportar_relatorios(
        matches=todos_matches,
        lancamentos_nao_conciliados=lancamentos_nao_conciliados,
        estatisticas=estatisticas
    )


if __name__ == "__main__":
    main()
