"""
Router de Upload de Arquivos
Gerencia upload de extratos bancários (CSV) e comprovantes (PDF)

Autor: Pedro Luis
Data: 06/11/2025
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import List
import logging
import shutil

logger = logging.getLogger(__name__)

# ==================== CONFIGURAÇÃO DO ROUTER ====================

router = APIRouter()

# ==================== DIRETÓRIOS DE UPLOAD ====================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "dados" / "entrada"
EXTRATO_DIR = UPLOAD_DIR / "extratos"
COMPROVANTES_DIR = UPLOAD_DIR / "comprovantes"

# Criar diretórios se não existirem
EXTRATO_DIR.mkdir(parents=True, exist_ok=True)
COMPROVANTES_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"📂 Diretório de extratos: {EXTRATO_DIR}")
logger.info(f"📂 Diretório de comprovantes: {COMPROVANTES_DIR}")

# ==================== ENDPOINT: UPLOAD DE EXTRATO ====================

@router.post("/extrato")
async def upload_extrato(arquivo: UploadFile = File(...)):
    """
    Upload de extrato bancário (CSV)
    
    Args:
        arquivo: Arquivo CSV do extrato
        
    Returns:
        JSON com informações do upload
        
    Raises:
        HTTPException: Se arquivo não for CSV
    """
    try:
        # Validar extensão
        if not arquivo.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Apenas arquivos CSV são aceitos para extratos"
            )
        
        # Salvar arquivo
        file_path = EXTRATO_DIR / arquivo.filename
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        
        logger.info(f"✅ Extrato salvo: {arquivo.filename}")
        
        return {
            "status": "ok",
            "mensagem": "Extrato enviado com sucesso",
            "arquivo": arquivo.filename,
            "tamanho": file_path.stat().st_size,
            "caminho": str(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao fazer upload de extrato: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINT: UPLOAD DE COMPROVANTES ====================

@router.post("/comprovantes")
async def upload_comprovantes(arquivos: List[UploadFile] = File(...)):
    """
    Upload de comprovantes de pagamento (PDF)
    
    Args:
        arquivos: Lista de arquivos PDF
        
    Returns:
        JSON com lista de arquivos enviados
        
    Raises:
        HTTPException: Se algum arquivo não for PDF
    """
    try:
        arquivos_salvos = []
        
        for arquivo in arquivos:
            # Validar extensão
            if not arquivo.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Arquivo '{arquivo.filename}' não é PDF"
                )
            
            # Salvar arquivo
            file_path = COMPROVANTES_DIR / arquivo.filename
            
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(arquivo.file, buffer)
            
            arquivos_salvos.append({
                "nome": arquivo.filename,
                "tamanho": file_path.stat().st_size,
                "caminho": str(file_path)
            })
            
            logger.info(f"✅ Comprovante salvo: {arquivo.filename}")
        
        return {
            "status": "ok",
            "mensagem": f"{len(arquivos_salvos)} comprovante(s) enviado(s) com sucesso",
            "arquivos": arquivos_salvos,
            "total": len(arquivos_salvos)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao fazer upload de comprovantes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINT: STATUS DOS UPLOADS ====================

@router.get("/status")
async def obter_status():
    """
    Retorna status dos arquivos enviados
    
    Returns:
        JSON com contagem de extratos e comprovantes
    """
    try:
        # Contar arquivos
        extratos = list(EXTRATO_DIR.glob("*.csv"))
        comprovantes = list(COMPROVANTES_DIR.glob("*.pdf"))
        
        return {
            "status": "ok",
            "extratos": {
                "total": len(extratos),
                "arquivos": [e.name for e in extratos]
            },
            "comprovantes": {
                "total": len(comprovantes),
                "arquivos": [c.name for c in comprovantes]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINT: LIMPAR UPLOADS ====================

@router.delete("/limpar")
async def limpar_uploads():
    """
    Remove todos os arquivos enviados
    
    Returns:
        JSON confirmando limpeza
    """
    try:
        # Remover extratos
        for arquivo in EXTRATO_DIR.glob("*.csv"):
            arquivo.unlink()
        
        # Remover comprovantes
        for arquivo in COMPROVANTES_DIR.glob("*.pdf"):
            arquivo.unlink()
        
        logger.info("🗑️  Arquivos limpos com sucesso")
        
        return {
            "status": "ok",
            "mensagem": "Todos os arquivos foram removidos"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
