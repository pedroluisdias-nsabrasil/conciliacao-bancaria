$arquivos = @(
    "ui\app.py",
    "ui\pages\1_📤_Upload.py",
    "ui\pages\2_🔄_Conciliar.py",
    "ui\pages\3_📊_Resultados.py",
    "ui\pages\4_📁_Relatórios.py",
    "ui\pages\5_📋_Regras.py"
)

$codigo_correto = @"
# Configurar PYTHONPATH
import sys
from pathlib import Path

# Detectar se está em pages/ ou em ui/
arquivo_atual = Path(__file__).resolve()
if 'pages' in str(arquivo_atual.parent):
    # Estamos em ui/pages/ - subir 2 níveis
    raiz = arquivo_atual.parent.parent.parent
else:
    # Estamos em ui/ - subir 1 nível
    raiz = arquivo_atual.parent.parent

# Adicionar raiz e src/ ao path
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))
if str(raiz / 'src') not in sys.path:
    sys.path.insert(0, str(raiz / 'src'))
"@

foreach ($arquivo in $arquivos) {
    Write-Host "Corrigindo: $arquivo" -ForegroundColor Yellow
    
    $conteudo = Get-Content $arquivo -Raw -Encoding UTF8
    
    # Substituir "import setup_path..." por código inline
    $conteudo = $conteudo -replace 'import setup_path\s+#[^\r\n]*', $codigo_correto
    
    # Salvar
    [System.IO.File]::WriteAllText($arquivo, $conteudo, [System.Text.UTF8Encoding]::new($false))
    
    Write-Host "  ✓ Corrigido!" -ForegroundColor Green
}

Write-Host "`n✅ Todos arquivos corrigidos!" -ForegroundColor Green
