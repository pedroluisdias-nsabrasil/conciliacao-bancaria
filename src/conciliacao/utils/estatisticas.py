"""Utilitários para conciliação."""

def gerar_estatisticas(matches, lancamentos, comprovantes=None):
    """
    Gera estatísticas da conciliação.
    
    Args:
        matches: Lista de matches encontrados
        lancamentos: Lista de lançamentos
        comprovantes: Lista de comprovantes (opcional)
        
    Returns:
        dict: Estatísticas da conciliação
    """
    total_lancamentos = len(lancamentos)
    total_conciliados = len([m for m in matches if m.conciliado])
    total_comprovantes = len(comprovantes) if comprovantes else 0
    
    return {
        'total_lancamentos': total_lancamentos,
        'total_conciliados': total_conciliados,
        'total_comprovantes': total_comprovantes,
        'taxa_conciliacao': (total_conciliados / total_lancamentos * 100) if total_lancamentos > 0 else 0,
        'total_pendentes': total_lancamentos - total_conciliados
    }
