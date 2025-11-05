"""
Página de Regras de Auto-Conciliação.

Mostra regras ativas, estatísticas e permite recarregar.
"""

import streamlit as st
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.conciliacao.estrategias.regras import EstrategiaRegras

st.set_page_config(
    page_title="Regras de Auto-Conciliação",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Regras de Auto-Conciliação")

# Descrição
st.markdown("""
Este sistema usa regras YAML para auto-conciliar lançamentos sem comprovante,
como tarifas bancárias, IOF, juros e outras despesas comuns.
""")

st.divider()

# ============================================================================
# INICIALIZAR ESTRATÉGIA
# ============================================================================

try:
    estrategia = EstrategiaRegras()
    stats = estrategia.obter_estatisticas()
    
except Exception as e:
    st.error(f"❌ Erro ao carregar estratégia: {e}")
    st.stop()

# ============================================================================
# ESTATÍSTICAS
# ============================================================================

st.subheader("📊 Estatísticas")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Regras", stats['total_regras'])

with col2:
    st.metric("Prioridade da Estratégia", stats['prioridade'])

with col3:
    arquivo_nome = Path(stats['arquivo']).name
    st.metric("Arquivo de Regras", arquivo_nome)

st.divider()

# ============================================================================
# BOTÃO RECARREGAR
# ============================================================================

col_btn, col_space = st.columns([1, 3])

with col_btn:
    if st.button("🔄 Recarregar Regras", use_container_width=True):
        try:
            estrategia.recarregar_regras()
            st.success("✅ Regras recarregadas com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao recarregar: {e}")

st.divider()

# ============================================================================
# LISTA DE REGRAS
# ============================================================================

st.subheader("📜 Regras Ativas")

if stats['total_regras'] == 0:
    st.warning("⚠️ Nenhuma regra carregada")
    st.stop()

# Ordenar regras por prioridade
regras_ordenadas = sorted(
    estrategia.engine.regras,
    key=lambda r: r.get('prioridade', 0),
    reverse=True
)

for regra in regras_ordenadas:
    # Status da regra
    ativo = regra.get('ativo', True)
    status_icon = "✅" if ativo else "❌"
    status_text = "Ativa" if ativo else "Inativa"
    
    # Prioridade
    prioridade = regra.get('prioridade', 0)
    
    # Título do expander
    titulo = f"{status_icon} **{regra['nome']}** (ID: {regra['id']}, Prioridade: {prioridade})"
    
    with st.expander(titulo):
        # Descrição
        descricao = regra.get('descricao', 'Sem descrição')
        st.markdown(f"**Descrição:** {descricao}")
        
        # Status
        st.markdown(f"**Status:** {status_text}")
        
        # Confiança
        confianca = regra.get('confianca', 0.95)
        st.markdown(f"**Confiança:** {confianca:.0%}")
        
        st.markdown("---")
        
        # Condições
        st.markdown("**Condições:**")
        condicoes = regra.get('condicoes', [])
        
        if not condicoes:
            st.info("ℹ️ Nenhuma condição definida")
        else:
            for i, cond in enumerate(condicoes, 1):
                campo = cond.get('campo', '?')
                operador = cond.get('operador', '?')
                valor = cond.get('valor', '?')
                
                # Formatar valor se for lista
                if isinstance(valor, list):
                    valor_str = f"[{', '.join(map(str, valor))}]"
                else:
                    valor_str = str(valor)
                
                st.markdown(f"{i}. `{campo}` **{operador}** `{valor_str}`")
        
        st.markdown("---")
        
        # Ação
        st.markdown("**Ação:**")
        acao = regra.get('acao', {})
        tipo = acao.get('tipo', 'auto_conciliar')
        categoria = acao.get('categoria', 'Não especificada')
        motivo = acao.get('motivo', 'Não especificado')
        
        st.markdown(f"- **Tipo:** {tipo}")
        st.markdown(f"- **Categoria:** {categoria}")
        st.markdown(f"- **Motivo:** {motivo}")

st.divider()

# ============================================================================
# INFORMAÇÕES ADICIONAIS
# ============================================================================

with st.expander("ℹ️ Como Funcionam as Regras"):
    st.markdown("""
    ### Como Adicionar/Editar Regras
    
    1. **Localização:** As regras estão em `config/regras/tarifas.yaml`
    
    2. **Estrutura de uma regra:**
```yaml
    - id: nome_unico
      nome: Nome Legível
      descricao: O que esta regra faz
      prioridade: 100
      ativo: true
      confianca: 0.95
      condicoes:
        - campo: descricao
          operador: contains
          valor: "PALAVRA CHAVE"
      acao:
        tipo: auto_conciliar
        categoria: Tarifa Bancária
        motivo: "Motivo da conciliação"
```
    
    3. **Operadores Disponíveis:**
    - `equals`: Igualdade exata
    - `contains`: Contém texto (case-insensitive)
    - `starts_with`: Começa com
    - `ends_with`: Termina com
    - `regex`: Expressão regular
    - `in_list`: Está na lista
    - `between`: Entre dois valores
    - `greater_than`: Maior que
    - `less_than`: Menor que
    - `range`: Dentro de range
    
    4. **Após editar:** Clique em "🔄 Recarregar Regras"
    """)

with st.expander("💡 Dicas"):
    st.markdown("""
    - Regras com **maior prioridade** são aplicadas **primeiro**
    - Use **prioridade 100+** para regras muito específicas
    - Use **prioridade 50-99** para regras gerais
    - Use **prioridade <50** para regras de fallback
    - Desative regras temporariamente com `ativo: false`
    - Teste sempre após adicionar novas regras
    """)

# Rodapé
st.divider()
st.caption(f"📁 Arquivo: {stats['arquivo']}")
st.caption("💡 Edite o arquivo YAML e clique em 'Recarregar' para aplicar mudanças")