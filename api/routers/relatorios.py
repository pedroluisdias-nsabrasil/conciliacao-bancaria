"""
Router de Relatórios
Gerencia geração de relatórios Excel e PDF

Autor: Pedro Luis
Data: 06/11/2025
Versão: 2.0.0 (Refatorado)

Mudanças v2.0.0:
- Agora usa GeradorExcel do src/relatorios/
- Eliminado código duplicado
- Suporte a Comprovantes Não Conciliados (Melhoria #4)
- Melhor separação de responsabilidades
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import json
import sys
from datetime import datetime, date
from decimal import Decimal

# Adicionar src/ ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

# ===== IMPORTS DO CORE =====
from src.relatorios.gerador_excel import GeradorExcel
from src.modelos.lancamento import Lancamento
from src.modelos.comprovante import Comprovante
from src.modelos.match import Match

logger = logging.getLogger(__name__)

# ==================== CONFIGURAÇÃO DO ROUTER ====================

router = APIRouter()

# ==================== DIRETÓRIOS ====================

SAIDA_DIR = BASE_DIR / "dados" / "saida"
SAIDA_DIR.mkdir(parents=True, exist_ok=True)

RESULTADOS_FILE = SAIDA_DIR / "ultimo_resultado.json"

logger.info(f"📂 Diretório de saída: {SAIDA_DIR}")

# ==================== FUNÇÕES AUXILIARES ====================

def carregar_resultados() -> Optional[Dict[str, Any]]:
    """
    Carrega últimos resultados do arquivo JSON
    
    Returns:
        Dicionário com resultados ou None se não existir
    """
    if not RESULTADOS_FILE.exists():
        logger.warning(f"⚠️  Arquivo de resultados não encontrado: {RESULTADOS_FILE}")
        return None
    
    try:
        with open(RESULTADOS_FILE, 'r', encoding='utf-8') as f:
            resultados = json.load(f)
            logger.info(f"✅ Resultados carregados: {RESULTADOS_FILE}")
            return resultados
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro ao decodificar JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao carregar resultados: {e}")
        return None


def reconstruir_objetos(resultados: Dict[str, Any]) -> tuple:
    """
    Reconstrói objetos Match, Lancamento e Comprovante do JSON
    
    Args:
        resultados: Dicionário com resultados da conciliação
        
    Returns:
        Tupla (matches, lancamentos_nao_conciliados, comprovantes_nao_conciliados)
    """
    matches = []
    lancamentos_nao_conciliados = []
    comprovantes_nao_conciliados = []
    
    # ===== RECONSTRUIR MATCHES =====
    for match_dict in resultados.get('matches', []):
        try:
            # Reconstruir Lancamento
            lanc_data = match_dict['lancamento']
            lancamento = Lancamento(
                data=date.fromisoformat(lanc_data['data']),
                valor=Decimal(str(lanc_data['valor'])),
                descricao=lanc_data['descricao'],
                tipo='D'  # Placeholder
            )
            
            # Reconstruir Comprovante (se existir)
            comprovante = None
            if match_dict['comprovante']:
                comp_data = match_dict['comprovante']
                comprovante = Comprovante(
                    arquivo=match_dict.get('arquivo_comprovante', f"Comprovante {comp_data.get('numero', 'S/N')}"),  # ✅ CORRIGIDO
                    valor=Decimal(str(comp_data['valor'])),
                    data=date.fromisoformat(comp_data['data'])
                )
            
            # Reconstruir Match
            match = Match(
                lancamento=lancamento,
                comprovante=comprovante,
                confianca=float(match_dict['confianca']) / 100,  # % → decimal
                metodo=match_dict['tipo']
            )
            
            matches.append(match)
            
        except Exception as e:
            logger.warning(f"⚠️  Erro ao reconstruir match: {e}")
            continue
    
    # ===== RECONSTRUIR LANÇAMENTOS NÃO CONCILIADOS =====
    for lanc_dict in resultados.get('nao_conciliados', []):
        try:
            lancamento = Lancamento(
                data=date.fromisoformat(lanc_dict['data']),
                valor=Decimal(str(lanc_dict['valor'])),
                descricao=lanc_dict['descricao'],
                tipo='D'  # Placeholder
            )
            lancamentos_nao_conciliados.append(lancamento)
        except Exception as e:
            logger.warning(f"⚠️  Erro ao reconstruir lançamento não conciliado: {e}")
            continue
    
    # ===== MANTER COMPROVANTES NÃO CONCILIADOS COMO DICT =====
    # O GeradorExcel espera lista de dicts, não objetos Comprovante
    comprovantes_nao_conciliados = resultados.get('comprovantes_nao_conciliados', [])
    
    logger.debug(
        f"Objetos reconstruídos: {len(matches)} matches, "
        f"{len(lancamentos_nao_conciliados)} não conciliados, "
        f"{len(comprovantes_nao_conciliados)} comprovantes não conciliados"
    )
    
    return matches, lancamentos_nao_conciliados, comprovantes_nao_conciliados


# ==================== ENDPOINT: GERAR RELATÓRIO EXCEL ====================

@router.get("/download")
async def download_relatorio():
    """
    Gera e retorna relatório Excel da última conciliação
    
    Usa o GeradorExcel profissional do src/relatorios/ que inclui:
    - Aba Resumo com estatísticas
    - Aba Conciliados com formatação condicional
    - Aba Não Conciliados
    - Aba Comprovantes Não Conciliados (Melhoria #4)
    
    Returns:
        FileResponse com arquivo Excel
        
    Raises:
        HTTPException: Se não houver dados ou erro na geração
    """
    try:
        # Carregar resultados do arquivo JSON
        ultimos_resultados = carregar_resultados()
        
        if not ultimos_resultados:
            raise HTTPException(
                status_code=400,
                detail="Execute a conciliação antes de gerar o relatório"
            )
        
        logger.info("📊 Gerando relatório Excel com GeradorExcel...")
        
        # Reconstruir objetos a partir do JSON
        matches, lanc_nao_conc, comp_nao_conc = reconstruir_objetos(ultimos_resultados)
        
        # Criar nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_conciliacao_{timestamp}.xlsx"
        caminho_arquivo = SAIDA_DIR / nome_arquivo
        
        # ===== USAR GERADOR PROFISSIONAL =====
        gerador = GeradorExcel()
        
        arquivo_gerado = gerador.gerar(
            matches=matches,
            lancamentos_nao_conciliados=lanc_nao_conc,
            comprovantes_nao_conciliados=comp_nao_conc,  # ✅ MELHORIA #4
            estatisticas=ultimos_resultados['estatisticas'],
            arquivo_saida=str(caminho_arquivo)
        )
        
        logger.info(f"✅ Relatório gerado: {nome_arquivo}")
        logger.info(f"   📊 {len(matches)} matches")
        logger.info(f"   📊 {len(lanc_nao_conc)} não conciliados")
        logger.info(f"   📊 {len(comp_nao_conc)} comprovantes não conciliados")
        
        # Retornar arquivo para download
        return FileResponse(
            path=caminho_arquivo,
            filename=nome_arquivo,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ENDPOINT: LISTAR RELATÓRIOS ====================

@router.get("/listar")
async def listar_relatorios():
    """
    Lista todos os relatórios disponíveis
    
    Returns:
        JSON com lista de relatórios
    """
    try:
        relatorios = []
        
        for arquivo in SAIDA_DIR.glob("relatorio_*.xlsx"):
            stat = arquivo.stat()
            relatorios.append({
                "nome": arquivo.name,
                "tamanho": f"{stat.st_size / 1024:.1f} KB",
                "data_criacao": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S"),
                "caminho": str(arquivo)
            })
        
        # Ordenar por data (mais recente primeiro)
        relatorios.sort(key=lambda x: x['data_criacao'], reverse=True)
        
        return {
            "total": len(relatorios),
            "relatorios": relatorios
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar relatórios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))