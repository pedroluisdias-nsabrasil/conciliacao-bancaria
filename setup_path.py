"""
Configura o PYTHONPATH para importar módulos do src/

Uso:
    import setup_path
    setup_path.setup()
"""
import sys
from pathlib import Path


def setup():
    """Adiciona src/ ao Python path"""
    root = Path(__file__).parent.absolute()
    
    # Adicionar raiz do projeto
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    
    # Adicionar diretório src
    src_path = root / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

# Executar automaticamente ao importar
setup()