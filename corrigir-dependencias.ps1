# ============================================================================
# SCRIPT DE CORREÇÃO - INSTALAÇÃO DE DEPENDÊNCIAS
# Windows PowerShell
# ============================================================================

Write-Host "=========================================="
Write-Host "Correção de Dependências - Pandas e NumPy"
Write-Host "=========================================="
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "venv")) {
    Write-Host "❌ Erro: Execute este script em C:\conciliacao-bancaria" -ForegroundColor Red
    Write-Host "Use: cd C:\conciliacao-bancaria" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit
}

# Ativar ambiente virtual
Write-Host "[1/4] Ativando ambiente virtual..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Ambiente virtual ativado" -ForegroundColor Green
Write-Host ""

# Atualizar pip
Write-Host "[2/4] Atualizando pip, setuptools e wheel..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "  ✓ Ferramentas atualizadas" -ForegroundColor Green
Write-Host ""

# Instalar bibliotecas core uma por uma
Write-Host "[3/4] Instalando bibliotecas principais..." -ForegroundColor Cyan
Write-Host "  (Isso pode levar 5-10 minutos)" -ForegroundColor Yellow
Write-Host ""

$corePackages = @(
    "numpy==1.26.3",
    "pandas==2.2.0",
    "pydantic==2.5.3",
    "python-dateutil==2.8.2",
    "pdfplumber==0.11.0",
    "openpyxl==3.1.2",
    "ofxparse==0.21",
    "pytesseract==0.3.10",
    "Pillow==10.2.0",
    "opencv-python==4.9.0.80",
    "pdf2image==1.17.0",
    "fuzzywuzzy==0.18.0",
    "python-Levenshtein==0.25.0",
    "regex==2023.12.25",
    "streamlit==1.30.0",
    "streamlit-aggrid==0.3.4.post3",
    "plotly==5.18.0",
    "reportlab==4.0.9",
    "jinja2==3.1.3",
    "pyyaml==6.0.1",
    "sqlalchemy==2.0.25",
    "alembic==1.13.1"
)

$instaladas = 0
$falhas = @()

foreach ($package in $corePackages) {
    $packageName = $package.Split("==")[0]
    Write-Host "  Instalando $packageName..." -NoNewline
    
    try {
        pip install $package --quiet 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            $instaladas++
        } else {
            Write-Host " ✗" -ForegroundColor Red
            $falhas += $packageName
        }
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        $falhas += $packageName
    }
}

Write-Host ""
Write-Host "  Resultado: $instaladas/$($corePackages.Count) pacotes instalados" -ForegroundColor Cyan
Write-Host ""

if ($falhas.Count -gt 0) {
    Write-Host "  ⚠ Pacotes que falharam: $($falhas -join ', ')" -ForegroundColor Yellow
    Write-Host ""
}

# Verificar instalação
Write-Host "[4/4] Verificando instalação..." -ForegroundColor Cyan
Write-Host ""

$verificacoes = @{
    "pandas" = "import pandas; print(pandas.__version__)"
    "numpy" = "import numpy; print(numpy.__version__)"
    "streamlit" = "import streamlit; print(streamlit.__version__)"
    "pytesseract" = "import pytesseract; print('OK')"
}

$sucessos = 0

foreach ($lib in $verificacoes.Keys) {
    Write-Host "  Testando $lib..." -NoNewline
    $cmd = $verificacoes[$lib]
    
    try {
        $result = python -c $cmd 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓ ($result)" -ForegroundColor Green
            $sucessos++
        } else {
            Write-Host " ✗" -ForegroundColor Red
        }
    } catch {
        Write-Host " ✗" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=========================================="

if ($sucessos -eq $verificacoes.Count) {
    Write-Host "✓ CORREÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Próximo passo:" -ForegroundColor Yellow
    Write-Host "python test_basico.py"
} else {
    Write-Host "⚠ CORREÇÃO PARCIAL" -ForegroundColor Yellow
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Algumas bibliotecas não foram instaladas." -ForegroundColor Yellow
    Write-Host "Veja a Opção 2 ou 3 nas instruções." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pressione Enter para continuar..."
Read-Host
