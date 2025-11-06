# Script de Correção Automática - ImportError
# Sistema de Conciliação Bancária
# Versão: 1.0

Write-Host "🔧 CORREÇÃO DE IMPORTS - Sistema de Conciliação Bancária" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Verificar se está na pasta correta
if (!(Test-Path "src\conciliacao")) {
    Write-Host "❌ ERRO: Execute este script na pasta raiz do projeto!" -ForegroundColor Red
    Write-Host "   Pasta esperada: C:\conciliacao-bancaria" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Pasta correta detectada" -ForegroundColor Green
Write-Host ""

# 1. Fazer backup
Write-Host "📦 Criando backups..." -ForegroundColor Yellow

$backupFiles = @(
    "src\conciliacao\__init__.py",
    "src\conciliacao\estrategias\__init__.py",
    "src\ingestao\__init__.py",
    "src\modelos\__init__.py"
)

foreach ($file in $backupFiles) {
    if (Test-Path $file) {
        Copy-Item $file "$file.backup" -Force
        Write-Host "  ✓ Backup: $file" -ForegroundColor Gray
    }
}

Write-Host ""

# 2. Criar/Atualizar __init__.py de conciliacao
Write-Host "📝 Atualizando src\conciliacao\__init__.py..." -ForegroundColor Yellow

$conciliacaoInit = @'
"""
Módulo de conciliação bancária.

Contém o motor principal de conciliação e as estratégias de matching.
"""

from .motor import MotorConciliacao
from .estrategias import (
    EstrategiaBase,
    EstrategiaExato,
    EstrategiaRegras
)

__all__ = [
    'MotorConciliacao',
    'EstrategiaBase',
    'EstrategiaExato',
    'EstrategiaRegras'
]
'@

Set-Content -Path "src\conciliacao\__init__.py" -Value $conciliacaoInit -Encoding UTF8
Write-Host "  ✓ Arquivo atualizado" -ForegroundColor Green
Write-Host ""

# 3. Criar/Atualizar __init__.py de estrategias
Write-Host "📝 Atualizando src\conciliacao\estrategias\__init__.py..." -ForegroundColor Yellow

$estrategiasInit = @'
"""
Estratégias de conciliação bancária.

Cada estratégia implementa uma abordagem diferente para encontrar matches
entre lançamentos bancários e comprovantes de pagamento.
"""

from .base import EstrategiaBase
from .exato import EstrategiaExato
from .regras import EstrategiaRegras

__all__ = [
    'EstrategiaBase',
    'EstrategiaExato',
    'EstrategiaRegras'
]
'@

Set-Content -Path "src\conciliacao\estrategias\__init__.py" -Value $estrategiasInit -Encoding UTF8
Write-Host "  ✓ Arquivo atualizado" -ForegroundColor Green
Write-Host ""

# 4. Criar/Atualizar __init__.py de ingestao
Write-Host "📝 Atualizando src\ingestao\__init__.py..." -ForegroundColor Yellow

$ingestaoInit = @'
"""
Módulo de ingestão de dados.

Responsável por ler e processar arquivos de entrada:
- Extratos bancários (CSV, Excel, PDF)
- Comprovantes de pagamento (PDF com OCR)
"""

from .leitor_csv import LeitorCSV
from .leitor_pdf import LeitorPDF
from .leitor_ocr import LeitorOCR

__all__ = [
    'LeitorCSV',
    'LeitorPDF',
    'LeitorOCR'
]
'@

Set-Content -Path "src\ingestao\__init__.py" -Value $ingestaoInit -Encoding UTF8
Write-Host "  ✓ Arquivo atualizado" -ForegroundColor Green
Write-Host ""

# 5. Criar/Atualizar __init__.py de modelos
Write-Host "📝 Atualizando src\modelos\__init__.py..." -ForegroundColor Yellow

$modelosInit = @'
"""
Módulo de modelos de dados.

Define as estruturas de dados principais do sistema:
- Lancamento: Registro de movimentação bancária
- Comprovante: Documento de comprovação de pagamento
- Match: Resultado de conciliação entre lançamento e comprovante
"""

from .lancamento import Lancamento
from .comprovante import Comprovante
from .match import Match

__all__ = [
    'Lancamento',
    'Comprovante',
    'Match'
]
'@

Set-Content -Path "src\modelos\__init__.py" -Value $modelosInit -Encoding UTF8
Write-Host "  ✓ Arquivo atualizado" -ForegroundColor Green
Write-Host ""

# 6. Limpar cache Python
Write-Host "🧹 Limpando cache Python..." -ForegroundColor Yellow

$cacheFiles = Get-ChildItem -Path "src" -Recurse -Directory -Filter "__pycache__"
foreach ($cache in $cacheFiles) {
    Remove-Item -Recurse -Force $cache.FullName
    Write-Host "  ✓ Removido: $($cache.FullName)" -ForegroundColor Gray
}

Write-Host ""

# 7. Teste rápido
Write-Host "🧪 Testando imports..." -ForegroundColor Yellow
Write-Host ""

$testScript = @'
import sys
sys.path.insert(0, '.')

try:
    from src.conciliacao import MotorConciliacao
    print("✓ MotorConciliacao OK")
except Exception as e:
    print(f"✗ MotorConciliacao FALHOU: {e}")
    
try:
    from src.ingestao import LeitorOCR
    print("✓ LeitorOCR OK")
except Exception as e:
    print(f"✗ LeitorOCR FALHOU: {e}")
    
try:
    from src.modelos import Lancamento, Comprovante, Match
    print("✓ Modelos OK")
except Exception as e:
    print(f"✗ Modelos FALHARAM: {e}")
'@

Set-Content -Path "test_imports.py" -Value $testScript -Encoding UTF8
python test_imports.py
Remove-Item "test_imports.py" -Force

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ CORREÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Recarregue o Streamlit (Ctrl+C e rodar de novo)" -ForegroundColor White
Write-Host "2. Teste a navegação para 'Conciliar'" -ForegroundColor White
Write-Host "3. Se funcionar, faça commit:" -ForegroundColor White
Write-Host "   git add src/**/__init__.py" -ForegroundColor Gray
Write-Host "   git commit -m 'fix: corrigir exports em __init__.py'" -ForegroundColor Gray
Write-Host ""
Write-Host "Se ainda houver erro, verifique FIX_IMPORT_ERROR.md" -ForegroundColor Yellow
Write-Host ""
