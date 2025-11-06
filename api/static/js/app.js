// ==================== SISTEMA DE CONCILIAÇÃO BANCÁRIA ====================
// Arquivo: app.js
// Descrição: JavaScript principal da aplicação

console.log('🏦 Sistema de Conciliação Bancária v1.0');

// ==================== UTILITÁRIOS GLOBAIS ====================

/**
 * Formata valor monetário para BRL
 */
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

/**
 * Formata data para padrão brasileiro
 */
function formatarData(data) {
    return new Date(data).toLocaleDateString('pt-BR');
}

/**
 * Mostra toast de notificação
 */
function mostrarToast(mensagem, tipo = 'info') {
    // TODO: Implementar sistema de toasts com Bootstrap
    console.log(`[${tipo.toUpperCase()}] ${mensagem}`);
}

/**
 * Faz requisição HTTP com tratamento de erros
 */
async function requisicaoAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro na requisição');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// ==================== VALIDAÇÕES ====================

/**
 * Valida arquivo CSV
 */
function validarCSV(arquivo) {
    if (!arquivo.name.endsWith('.csv')) {
        throw new Error('Arquivo deve ser .csv');
    }
    
    if (arquivo.size === 0) {
        throw new Error('Arquivo vazio');
    }
    
    if (arquivo.size > 10 * 1024 * 1024) { // 10MB
        throw new Error('Arquivo muito grande (máx 10MB)');
    }
    
    return true;
}

/**
 * Valida arquivo PDF
 */
function validarPDF(arquivo) {
    if (!arquivo.name.endsWith('.pdf')) {
        throw new Error('Arquivo deve ser .pdf');
    }
    
    if (arquivo.size === 0) {
        throw new Error('Arquivo vazio');
    }
    
    if (arquivo.size > 5 * 1024 * 1024) { // 5MB
        throw new Error('Arquivo muito grande (máx 5MB)');
    }
    
    return true;
}

// ==================== HIGHLIGHT DE NAVEGAÇÃO ====================

/**
 * Destaca item ativo no menu
 */
function atualizarMenuAtivo() {
    const path = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === path) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Executar ao carregar página
document.addEventListener('DOMContentLoaded', atualizarMenuAtivo);

// ==================== CONFIRMAÇÕES ====================

/**
 * Confirma ação antes de executar
 */
function confirmarAcao(mensagem) {
    return confirm(mensagem);
}

// ==================== LOADING ====================

/**
 * Mostra/esconde spinner de loading
 */
function toggleLoading(elementId, mostrar = true) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (mostrar) {
        element.innerHTML = `
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `;
    }
}

// ==================== COPIAR PARA CLIPBOARD ====================

/**
 * Copia texto para área de transferência
 */
async function copiarParaClipboard(texto) {
    try {
        await navigator.clipboard.writeText(texto);
        mostrarToast('Copiado para área de transferência!', 'success');
        return true;
    } catch (error) {
        console.error('Erro ao copiar:', error);
        mostrarToast('Erro ao copiar', 'error');
        return false;
    }
}

// ==================== DEBUG ====================

/**
 * Ativa modo debug (apenas desenvolvimento)
 */
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🔧 Modo desenvolvimento ativado');
    
    // Expor utilitários no console
    window.conciliacao = {
        formatarMoeda,
        formatarData,
        mostrarToast,
        requisicaoAPI
    };
}

// ==================== EXPORTAR FUNÇÕES ====================
window.conciliacaoUtils = {
    formatarMoeda,
    formatarData,
    validarCSV,
    validarPDF,
    requisicaoAPI,
    mostrarToast,
    confirmarAcao,
    toggleLoading,
    copiarParaClipboard
};
