"""
Router de Conciliação
Gerencia execução do motor de conciliação

Autor: Pedro Luis
Data: 06/11/2025
Versão: 1.2.0 (Corrigida - Melhoria #4)

Correções v1.2.0:
- Corrigido uso de 'arquivo' ao invés de 'arquivo_origem'
- Corrigido tracking de comprovantes usando id()
- Corrigido nome de variável 'comprovantes_usados_ids'
- Suporte completo a Comprovantes Não Conciliados
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import sys
import json
from datetime import datetime
from decimal import Decimal

# Adicionar src/ ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

# Imports do código core
from src.ingestao.leitor_csv import LeitorCSV
from src.ingestao.leitor_ocr import LeitorOCR
from src.conciliacao.motor import MotorConciliacao

logger = logging.getLogger(__name__)

# ==================== CONFIGURAÇÃO DO ROUTER ====================

router = APIRouter()

# ==================== CONFIGURAÇÃO DE DIRETÓRIOS ====================

RESULTADOS_DIR = BASE_DIR / "dados" / "saida"
RESULTADOS_FILE = RESULTADOS_DIR / "ultimo_resultado.json"

# Criar diretório de saída
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

# ==================== FUNÇÕES AUXILIARES ====================

def safe_float(valor: Optional[Decimal]) -> Optional[float]:
    """
    Converte Decimal para float com segurança
    
    Args:
        valor: Valor Decimal ou None
        
    Returns:
        Float ou None
    """
    if valor is None:
        return None
    try:
        return float(valor)
    except (ValueError, TypeError):
        return None

def hash_lancamento(lancamento) -> tuple:
    """
    Cria hash único para lançamento baseado em seus atributos
    
    Args:
        lancamento: Objeto Lancamento
        
    Returns:
        Tupla com (data, valor, descricao)
    """
    return (
        lancamento.data,
        lancamento.valor,
        lancamento.descricao
    )

def salvar_resultados(resultados: Dict[str, Any]) -> None:
    """
    Salva resultados em arquivo JSON
    
    Args:
        resultados: Dicionário com resultados da conciliação
    """
    try:
        with open(RESULTADOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Resultados salvos em {RESULTADOS_FILE}")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar resultados: {e}")

def carregar_resultados() -> Optional[Dict[str, Any]]:
    """
    Carrega últimos resultados do arquivo JSON
    
    Returns:
        Dicionário com resultados ou None
    """
    if not RESULTADOS_FILE.exists():
        return None
    
    try:
        with open(RESULTADOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Erro ao carregar resultados: {e}")
        return None

# ==================== ENDPOINT: EXECUTAR CONCILIAÇÃO ====================

@router.post("/executar")
async def executar_conciliacao():
    """
    Executa o processo de conciliação completo
    
    Returns:
        JSON com estatísticas e resultados
        
    Raises:
        HTTPException: Se ocorrer erro no processo
    """
    try:
        logger.info("=" * 60)
        logger.info("🚀 Iniciando processo de conciliação")
        logger.info("=" * 60)
        
        # ===== ETAPA 1: LER EXTRATO =====
        logger.info("📄 Etapa 1/4: Lendo extrato bancário...")
        
        extrato_dir = BASE_DIR / "dados" / "entrada" / "extratos"
        extratos = list(extrato_dir.glob("*.csv"))
        
        if not extratos:
            raise HTTPException(
                status_code=400,
                detail="Nenhum extrato CSV encontrado. Faça upload antes de conciliar."
            )
        
        # Usar o arquivo mais recente
        extratos_ordenados = sorted(
            extratos, 
            key=lambda p: p.stat().st_mtime, 
            reverse=True
        )
        extrato_path = extratos_ordenados[0]
        
        logger.info(f"  📌 Arquivo: {extrato_path.name}")
        
        leitor_csv = LeitorCSV()
        lancamentos = leitor_csv.ler_arquivo(str(extrato_path))
        
        logger.info(f"  ✅ {len(lancamentos)} lançamentos lidos")
        
        # ===== ETAPA 2: PROCESSAR COMPROVANTES =====
        logger.info("📑 Etapa 2/4: Processando comprovantes...")
        
        comprovantes_dir = BASE_DIR / "dados" / "entrada" / "comprovantes"
        pdfs = list(comprovantes_dir.glob("*.pdf"))
        
        logger.info(f"  📌 {len(pdfs)} arquivo(s) PDF encontrado(s)")
        
        comprovantes = []
        leitor_ocr = LeitorOCR()
        
        for pdf_path in pdfs:
            try:
                comps = leitor_ocr.ler_arquivo(str(pdf_path))
                if comps:
                    comprovantes.extend(comps)
                    logger.info(f"  ✅ Processado: {pdf_path.name}")
            except Exception as e:
                logger.warning(f"  ⚠️  Erro ao processar {pdf_path.name}: {e}")
        
        logger.info(f"  ✅ {len(comprovantes)} comprovante(s) extraído(s)")
        
        # ===== ETAPA 3: NORMALIZAR DADOS =====
        logger.info("🔄 Etapa 3/4: Normalizando dados...")
        # Dados já estão normalizados pelos leitores
        logger.info("  ✅ Dados já normalizados pelos leitores")
        
        # ===== ETAPA 4: EXECUTAR CONCILIAÇÃO =====
        logger.info("⚙️  Etapa 4/4: Executando conciliação...")
        
        motor = MotorConciliacao()
        matches = motor.conciliar(lancamentos, comprovantes)
        
        logger.info(f"  ✅ Conciliação concluída")
        
        # ===== CALCULAR ESTATÍSTICAS =====
        # Identificar lançamentos não conciliados
        lancamentos_com_match = {
            hash_lancamento(m.lancamento) for m in matches
        }
        nao_conciliados = [
            l for l in lancamentos
            if hash_lancamento(l) not in lancamentos_com_match
        ]
        
        # ===== CALCULAR COMPROVANTES NÃO CONCILIADOS =====
        # Identificar comprovantes que não foram usados em nenhum match
        # Usar id() do objeto Python como identificador único
        comprovantes_usados_ids = {
            id(m.comprovante) 
            for m in matches 
            if m.comprovante
        }
        comprovantes_nao_conciliados = [
            c for c in comprovantes 
            if id(c) not in comprovantes_usados_ids
        ]

        logger.info(f"  📊 Comprovantes usados: {len(comprovantes_usados_ids)}")
        logger.info(f"  📊 Comprovantes não conciliados: {len(comprovantes_nao_conciliados)}")
        
        total_lancamentos = len(lancamentos)
        total_comprovantes = len(comprovantes)
        total_matches = len(matches)
        
        # Calcular taxa de conciliação
        taxa_conciliacao = (
            (total_matches / total_lancamentos * 100) 
            if total_lancamentos > 0 
            else 0
        )
        
        # Calcular confiança média
        confianca_media = 0.0
        if matches:
            confiancas = [m.confianca for m in matches]
            confianca_media = sum(confiancas) / len(confiancas)
        
        # Contar auto-aprovados
        auto_aprovados = sum(1 for m in matches if m.pode_auto_aprovar)
        
        # Preparar estatísticas
        estatisticas = {
            "total_lancamentos": total_lancamentos,
            "total_comprovantes": total_comprovantes,
            "total_matches": total_matches,
            "taxa_conciliacao": round(taxa_conciliacao, 1),
            "confianca_media": round(confianca_media * 100, 1),
            "auto_aprovados": auto_aprovados,
            "nao_conciliados": len(nao_conciliados),
            "comprovantes_usados": len(comprovantes_usados_ids),
            "comprovantes_nao_conciliados": len(comprovantes_nao_conciliados)
        }
        
        # Converter matches para dict
        matches_dict = []
        for match in matches:
            match_dict = {
                "lancamento": {
                    "data": match.lancamento.data.isoformat(),
                    "valor": safe_float(match.lancamento.valor),
                    "descricao": match.lancamento.descricao
                },
                "confianca": round(match.confianca * 100, 1),
                "tipo": match.metodo,
                "observacoes": match.observacoes,
                "auto_aprovado": match.pode_auto_aprovar
            }
            
            # Adicionar comprovante se existir
            if match.comprovante:
                match_dict["comprovante"] = {
                    "arquivo": match.comprovante.arquivo,  # ✅ ADICIONAR ESTA LINHA
                    "numero": match.comprovante.numero_documento,
                    "valor": safe_float(match.comprovante.valor),
                    "data": match.comprovante.data.isoformat()
                }
            else:
                match_dict["comprovante"] = None
            
            matches_dict.append(match_dict)
        
        # Converter não conciliados para dict
        nao_conciliados_dict = []
        for lanc in nao_conciliados:
            nao_conciliados_dict.append({
                "data": lanc.data.isoformat(),
                "valor": safe_float(lanc.valor),
                "descricao": lanc.descricao
            })
        
        # Converter comprovantes não conciliados para dict
        comprovantes_nao_conciliados_dict = []
        for comp in comprovantes_nao_conciliados:
            comprovantes_nao_conciliados_dict.append({
                "arquivo": comp.arquivo,
                "valor": safe_float(comp.valor),
                "data": comp.data.isoformat() if comp.data else None,
                "numero": comp.numero_documento if hasattr(comp, 'numero_documento') else None,
                "beneficiario": comp.beneficiario if hasattr(comp, 'beneficiario') else None
            })
        
        # Preparar resultado completo
        resultado = {
            "estatisticas": estatisticas,
            "matches": matches_dict,
            "nao_conciliados": nao_conciliados_dict,
            "comprovantes_nao_conciliados": comprovantes_nao_conciliados_dict,
            "timestamp": datetime.now().isoformat(),
            "arquivo_extrato": extrato_path.name
        }
        
        # Salvar resultados em arquivo
        salvar_resultados(resultado)
        
        logger.info("=" * 60)
        logger.info(
            f"✅ Conciliação finalizada: "
            f"{total_matches}/{total_lancamentos} "
            f"({taxa_conciliacao:.1f}%)"
        )
        logger.info("=" * 60)
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na conciliação: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINT: OBTER RESULTADOS ====================

@router.get("/resultados")
async def obter_resultados():
    """
    Retorna os últimos resultados da conciliação
    
    Returns:
        JSON com resultados
        
    Raises:
        HTTPException: Se não houver resultados
    """
    resultado = carregar_resultados()
    
    if not resultado:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma conciliação foi executada ainda"
        )
    
    return resultado

# ==================== ENDPOINT: LIMPAR RESULTADOS ====================

@router.delete("/limpar")
async def limpar_resultados():
    """
    Limpa os resultados salvos
    
    Returns:
        JSON com mensagem de sucesso
    """
    try:
        if RESULTADOS_FILE.exists():
            RESULTADOS_FILE.unlink()
            logger.info("✅ Resultados limpos")
            return {"status": "ok", "message": "Resultados limpos com sucesso"}
        else:
            return {"status": "ok", "message": "Nenhum resultado para limpar"}
    except Exception as e:
        logger.error(f"❌ Erro ao limpar resultados: {e}")
        raise HTTPException(status_code=500, detail=str(e))