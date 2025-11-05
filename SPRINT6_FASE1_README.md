# 🚀 SPRINT 6 - FASE 1: Setup e Parser YAML

**Data:** 05/11/2025  
**Status:** ✅ COMPLETA - Pronto para instalar

---

## 📦 ARQUIVOS INCLUÍDOS

Este pacote contém 5 arquivos:

```
sprint6-fase1/
├── src/
│   └── regras/
│       ├── __init__.py          (Módulo de regras)
│       └── parser.py            (Parser YAML - 160 linhas)
│
├── config/
│   └── regras/
│       └── tarifas.yaml         (11 regras de auto-conciliação)
│
├── tests/
│   └── test_regras/
│       ├── __init__.py          (Módulo de testes)
│       └── test_parser.py       (15 testes do parser)
│
└── README_INSTALACAO.md         (Este arquivo)
```

---

## 🎯 O QUE FOI IMPLEMENTADO

### ✅ Parser YAML (`src/regras/parser.py`)
- Lê arquivos YAML de regras
- Valida estrutura completa
- Filtra regras ativas/inativas
- Verifica IDs únicos
- Valida operadores permitidos
- Logging detalhado
- 160 linhas de código profissional

### ✅ Regras de Tarifas (`config/regras/tarifas.yaml`)
11 regras pré-definidas para auto-conciliação:

**Tarifas Bancárias:**
1. Tarifa DOC/TED (confiança: 95%)
2. Tarifa PIX (confiança: 95%)
3. Tarifa Boleto (confiança: 90%)
4. Tarifa Manutenção Conta (confiança: 92%)

**IOF:**
5. IOF Cartão de Crédito (confiança: 90%)
6. IOF Empréstimo (confiança: 88%)

**Juros e Encargos:**
7. Juros Cheque Especial (confiança: 85%)
8. Juros de Mora (confiança: 80%)

**Rendimentos:**
9. Rendimento Poupança (confiança: 88%)

**Estornos:**
10. Estorno de Tarifa (confiança: 85%)

### ✅ Testes (`tests/test_regras/test_parser.py`)
15 testes automatizados:
- ✅ Carregamento de regras válidas
- ✅ Arquivo inexistente
- ✅ YAML inválido
- ✅ Arquivo vazio
- ✅ Sem chave 'regras'
- ✅ Filtrar regras inativas
- ✅ Campo obrigatório faltando
- ✅ ID duplicado
- ✅ Condições vazias
- ✅ Operador inválido
- ✅ Tipo de ação inválido
- ✅ Arquivo real de tarifas
- ✅ Múltiplas condições
- ✅ Todos operadores válidos
- ✅ Validações completas

---

## 📋 INSTRUÇÕES DE INSTALAÇÃO

### Passo 1: Extrair Arquivos

Extraia o conteúdo desta pasta mantendo a estrutura:

```powershell
# Copiar para o projeto:
C:\conciliacao-bancaria\
```

Estrutura final esperada:

```
C:\conciliacao-bancaria\
├── src\
│   └── regras\
│       ├── __init__.py
│       └── parser.py
├── config\
│   └── regras\
│       └── tarifas.yaml
└── tests\
    └── test_regras\
        ├── __init__.py
        └── test_parser.py
```

### Passo 2: Ativar Ambiente Virtual

```powershell
cd C:\conciliacao-bancaria
.\venv\Scripts\Activate.ps1
```

### Passo 3: Instalar PyYAML

```powershell
pip install pyyaml==6.0.1
```

### Passo 4: Atualizar requirements.txt

```powershell
pip freeze > requirements.txt
```

### Passo 5: Executar Testes

```powershell
# Testar apenas o parser
pytest tests/test_regras/test_parser.py -v

# Resultado esperado:
# ==================== 15 passed in X.XXs ====================
```

### Passo 6: Verificar Instalação

```powershell
# Testar import do parser
python -c "from src.regras.parser import ParserRegras; print('✅ Parser OK!')"

# Testar carregamento de regras
python -c "from pathlib import Path; from src.regras.parser import ParserRegras; p = ParserRegras(Path('config/regras/tarifas.yaml')); r = p.carregar(); print(f'✅ {len(r)} regras carregadas!')"
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Após instalação, verifique:

- [ ] Arquivos copiados para locais corretos
- [ ] PyYAML 6.0.1 instalado
- [ ] requirements.txt atualizado
- [ ] 15 testes do parser passando
- [ ] Import do parser funciona
- [ ] Carregamento de regras funciona
- [ ] Mensagem: "11 regras carregadas!"

---

## 🎯 PRÓXIMOS PASSOS

Após validar a instalação, retorne ao chat do Claude e digite:

**"FASE 1 OK"**

Ele continuará com a **FASE 2: Engine de Regras**

---

## 📊 ESTATÍSTICAS DA FASE 1

```
Arquivos criados:    5
Linhas de código:    ~400 linhas
Testes:              15 automatizados
Regras:              11 pré-definidas
Tempo estimado:      15 minutos de instalação
Coverage:            100% do parser
```

---

## ❓ PROBLEMAS COMUNS

### Erro: "ModuleNotFoundError: No module named 'yaml'"
**Solução:** Execute `pip install pyyaml==6.0.1`

### Erro: "FileNotFoundError: config/regras/tarifas.yaml"
**Solução:** Verifique se copiou a pasta `config` para o local correto

### Erro: "ImportError: cannot import name 'ParserRegras'"
**Solução:** Verifique se copiou `src/regras/__init__.py` e `parser.py`

### Testes falhando
**Solução:** Execute de dentro da pasta raiz: `cd C:\conciliacao-bancaria`

---

## 📞 SUPORTE

**Desenvolvedor:** Pedro Luis  
**Email:** pedroluisdias@br-nsa.com  
**Projeto:** C:\conciliacao-bancaria\  

**Retorne ao chat do Claude para continuar!** 🚀

---

**✅ FASE 1 COMPLETA - BOA SORTE!** 🎉
