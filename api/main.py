"""
Sistema de Conciliação Bancária - API FastAPI
Arquivo principal da aplicação

Autor: Pedro Luis
Data: 06/11/2025
Versão: 1.1.0 (Corrigida)

Correções aplicadas:
- Removido código fora de contexto (linha 185)
- Consolidado imports
- Substituído @app.on_event por lifespan moderno
- Adicionado criação automática de diretórios
- Error handlers com fallback robusto
- Favicon integrado corretamente
- PYTHONPATH configurado
- Imports absolutos
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import Response, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
import sys
from datetime import datetime

# ==================== CONFIGURAÇÃO DE PATHS ====================

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "api" / "static"
TEMPLATES_DIR = BASE_DIR / "api" / "templates"
LOG_DIR = BASE_DIR / "logs"

# Criar diretórios necessários
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==================== CONFIGURAÇÃO DE LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'api.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ==================== LIFESPAN (STARTUP/SHUTDOWN) ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação"""
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 Sistema de Conciliação Bancária - Iniciando")
    logger.info(f"📂 Base Dir: {BASE_DIR}")
    logger.info(f"📁 Static Dir: {STATIC_DIR}")
    logger.info(f"📄 Templates Dir: {TEMPLATES_DIR}")
    logger.info(f"📝 Log Dir: {LOG_DIR}")
    logger.info("=" * 60)
    
    yield  # Servidor roda aqui
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Sistema de Conciliação Bancária - Encerrando")
    logger.info("=" * 60)

# ==================== INSTÂNCIA DO FASTAPI ====================

app = FastAPI(
    title="Sistema de Conciliação Bancária",
    description="API para conciliação automática de extratos bancários",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# ==================== STATIC FILES E TEMPLATES ====================

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configurar templates Jinja2
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ==================== CONFIGURAR PYTHONPATH ====================

# Adicionar diretórios ao path para imports funcionarem
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "api") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "api"))

# ==================== INCLUIR ROUTERS ====================

try:
    # Import absoluto para evitar problemas
    from api.routers import upload, conciliar, relatorios
    
    app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
    app.include_router(conciliar.router, prefix="/api/conciliar", tags=["Conciliação"])
    app.include_router(relatorios.router, prefix="/api/relatorios", tags=["Relatórios"])
    
    logger.info("✅ Routers carregados com sucesso")
    
except ImportError as e:
    logger.critical(f"❌ ERRO CRÍTICO: Não foi possível carregar routers: {e}")
    logger.critical(f"❌ PATH atual: {sys.path}")
    logger.critical("❌ Servidor não pode iniciar sem routers!")
    sys.exit(1)

# ==================== MIDDLEWARE DE LOGGING ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logar todas as requisições"""
    start_time = datetime.now()
    
    try:
        # Processar requisição
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = (datetime.now() - start_time).total_seconds()
        
        # Logar
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Tempo: {process_time:.3f}s"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro no middleware: {e}")
        raise

# ==================== ROTAS PRINCIPAIS ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial do sistema"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "titulo": "Sistema de Conciliação Bancária",
            "versao": "1.1.0"
        }
    )

@app.get("/upload", response_class=HTMLResponse)
async def pagina_upload(request: Request):
    """Página de upload de arquivos"""
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )

@app.get("/conciliar", response_class=HTMLResponse)
async def pagina_conciliar(request: Request):
    """Página de conciliação"""
    return templates.TemplateResponse(
        "conciliar.html",
        {"request": request}
    )

# ==================== FAVICON ====================

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Retorna 204 para evitar erro de favicon"""
    return Response(status_code=204)

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0",
        "base_dir": str(BASE_DIR)
    }

# ==================== HANDLERS DE ERRO ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler para erro 404 com fallback"""
    logger.warning(f"Página não encontrada: {request.url.path}")
    
    # Verificar se template existe
    template_404 = TEMPLATES_DIR / "404.html"
    if template_404.exists():
        try:
            return templates.TemplateResponse(
                "404.html",
                {"request": request},
                status_code=404
            )
        except Exception as e:
            logger.error(f"Erro ao renderizar 404.html: {e}")
    
    # Fallback para JSON
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Página não encontrada",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler para erro 500 com fallback"""
    logger.error(f"Erro interno: {exc}", exc_info=True)
    
    # Verificar se template existe
    template_500 = TEMPLATES_DIR / "500.html"
    if template_500.exists():
        try:
            return templates.TemplateResponse(
                "500.html",
                {"request": request, "erro": str(exc)},
                status_code=500
            )
        except Exception as e:
            logger.error(f"Erro ao renderizar 500.html: {e}")
    
    # Fallback para JSON
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "error": str(exc)
        }
    )

# ==================== EXECUTAR SERVIDOR ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🌟 Iniciando servidor de desenvolvimento...")
    
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
