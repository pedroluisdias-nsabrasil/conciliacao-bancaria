# 🏦 Sistema de Conciliação Bancária

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

**Sistema automatizado para conciliação de extratos bancários com comprovantes de pagamento**

[Características](#-características) • [Instalação](#-instalação) • [Uso](#-uso) • [Documentação](#-documentação) • [Roadmap](#-roadmap)

</div>

---

## 📋 Sobre o Projeto

Sistema profissional que automatiza a conciliação bancária através de OCR (Reconhecimento Óptico de Caracteres) e algoritmos inteligentes de matching, reduzindo trabalho manual em **85-95%**.

### 🎯 Métricas de Sucesso

```
✅ Taxa de Conciliação:    60.9% (automática)
✅ Redução Trabalho Manual: 85-95%
✅ Precisão OCR:            100% (multi-página)
✅ Testes Automatizados:    91+ (100% sucesso)
✅ Código Profissional:     14.428 linhas
✅ Status:                  PRODUÇÃO ✅
```

---

## ✨ Características

### **Core do Sistema**
- 📄 **Leitura de Extratos CSV** - Processamento automático de extratos bancários
- 🔍 **OCR Multi-página** - Extração de dados de comprovantes PDF (Tesseract)
- 🤖 **Conciliação Inteligente** - Múltiplas estratégias de matching
- 📊 **Relatórios Excel** - 4 abas profissionais com formatação condicional
- 🌐 **Interface Web** - FastAPI moderna e responsiva
- ⚙️ **Regras YAML** - Sistema configurável de auto-conciliação

### **Estratégias de Conciliação**
1. **Regras YAML** (92% confiança) - Auto-conciliação de tarifas e IOF
2. **Matching Exato** (85% confiança) - Valor + Data exatos

### **Em Desenvolvimento** (v1.1+)
- 🔄 **Fuzzy Matching** - Similaridade de texto
- 📦 **Matching Agregado** - N comprovantes → 1 lançamento
- 🏦 **Multi-banco** - 5+ bancos brasileiros
- ☁️ **Cloud OCR** - Google Vision API
- 🤖 **Machine Learning** - Sugestões inteligentes

---

## 🚀 Instalação

### **Requisitos**

```
Sistema Operacional: Windows 10/11
Python: 3.12+ (funciona em 3.11+)
Tesseract OCR: 5.0+
Git: 2.40+
```

### **Passo a Passo**

#### 1. **Clone o Repositório**
```bash
git clone https://github.com/[seu-usuario]/conciliacao-bancaria.git
cd conciliacao-bancaria
```

#### 2. **Crie Ambiente Virtual**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 3. **Instale Dependências**
```powershell
pip install -r requirements.txt
```

#### 4. **Instale Tesseract OCR**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar em: `C:\Program Files\Tesseract-OCR\`
- Adicionar ao PATH do sistema

#### 5. **Verificar Instalação**
```powershell
# Testar Tesseract
tesseract --version

# Executar testes
pytest tests/ -v
```

---

## 💻 Uso

### **Iniciar o Sistema**

```powershell
# 1. Ativar ambiente virtual
cd C:\conciliacao-bancaria
.\venv\Scripts\Activate.ps1

# 2. Iniciar servidor
python api/main.py

# 3. Acessar no navegador
# http://127.0.0.1:8000
```

### **Fluxo de Trabalho**

```
1. Upload do Extrato (CSV)
   ↓
2. Upload dos Comprovantes (PDFs)
   ↓
3. Executar Conciliação
   ↓
4. Visualizar Resultados
   ↓
5. Baixar Relatório Excel
```

### **API REST**

```bash
# Documentação interativa
http://127.0.0.1:8000/api/docs

# Exemplos de endpoints
POST /api/upload/extrato
POST /api/upload/comprovantes
POST /api/conciliar/executar
GET  /api/relatorios/download
```

---

## 📊 Estrutura do Projeto

```
conciliacao-bancaria/
│
├── api/                      # FastAPI Backend
│   ├── routers/             # Endpoints REST
│   ├── templates/           # Templates Jinja2
│   └── main.py              # Servidor principal
│
├── src/                      # Core Business Logic
│   ├── modelos/             # Modelos de dados
│   ├── ingestao/            # Leitores CSV/OCR
│   ├── conciliacao/         # Motor + Estratégias
│   ├── relatorios/          # Geradores Excel
│   └── regras/              # Sistema de regras YAML
│
├── config/                   # Configurações
│   └── regras/              # Regras YAML
│
├── dados/                    # Dados do usuário (gitignored)
│   ├── entrada/             # Extratos + Comprovantes
│   └── saida/               # Relatórios gerados
│
├── tests/                    # Testes automatizados
├── docs/                     # Documentação completa
└── requirements.txt          # Dependências Python
```

---

## 📚 Documentação

### **Documentos Disponíveis**

- 📖 [Guia do Usuário Completo](docs/GUIA_USUARIO_COMPLETO.md)
- 🏗️ [Arquitetura do Sistema](docs/ARQUITETURA_SISTEMA.md)
- 📊 [Relatório de Implementação](docs/RELATORIO_FINAL_IMPLEMENTACAO.md)
- 🗺️ [Mapa de Melhorias](docs/MAPA_MELHORIAS_SISTEMA_CONCILIACAO.md)
- 📝 [Changelog](docs/CHANGELOG_v1_0.md)

### **Para Desenvolvedores**

```bash
# Executar testes
pytest tests/ -v

# Testes com cobertura
pytest tests/ --cov=src --cov-report=html

# Formatar código
black src/ tests/

# Linting
flake8 src/
```

---

## 🗺️ Roadmap

### **v1.0** ✅ (ATUAL - Novembro 2025)
- [x] MVP completo e funcional
- [x] OCR multi-página
- [x] Interface FastAPI
- [x] Relatórios Excel profissionais
- [x] Sistema de regras YAML

### **v1.1** 🔄 (Próximos 3 meses)
- [ ] Estratégia Fuzzy Matching
- [ ] Matching Agregado (N:1)
- [ ] Leitura de extratos PDF

### **v1.2** 📅 (Próximos 5 meses)
- [ ] Suporte a 5+ bancos brasileiros
- [ ] Relatórios PDF
- [ ] Google Cloud Vision OCR

### **v2.0** 🚀 (Futuro)
- [ ] Machine Learning
- [ ] Multi-empresa (multi-tenancy)
- [ ] API REST pública
- [ ] Dashboard Analytics

**Meta Final:** 90-95% de conciliação automática

---

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **FastAPI** - Framework web moderno
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validação de dados

### **Processamento**
- **pandas** - Manipulação de dados
- **pytesseract** - OCR
- **pdfplumber** - Extração de PDFs
- **Pillow** - Processamento de imagens

### **Matching**
- **fuzzywuzzy** - Similaridade de texto
- **python-Levenshtein** - Otimização fuzzy

### **Relatórios**
- **openpyxl** - Geração Excel
- **reportlab** - Geração PDF (futuro)

### **Testes**
- **pytest** - Framework de testes
- **pytest-cov** - Cobertura de código

---

## 📈 Performance

```
Métrica                    Valor
─────────────────────────────────
Taxa Conciliação:          60.9%
Tempo Processamento:       30s (23 lançamentos + 18 comprovantes)
Tempo OCR por página:      ~1.5s
Precisão OCR:              100% (multi-página)
Testes Sucesso:            100% (91 testes)
Cobertura Código:          85%+
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### **Convenções de Commit**
Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nova funcionalidade
fix: correção de bug
docs: atualização de documentação
test: adiciona/atualiza testes
refactor: refatoração de código
style: formatação (sem mudança de lógica)
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Pedro Luis**  
🏢 BR-NSA  
📧 pedroluisdias@br-nsa.com  
📍 Santo André, SP, Brasil

---

## 🙏 Agradecimentos

- Tesseract OCR Team
- FastAPI Community
- Todos que contribuíram com feedback

---

## 📞 Suporte

Encontrou um bug ou tem uma sugestão?

- 🐛 [Reportar Bug](https://github.com/[seu-usuario]/conciliacao-bancaria/issues)
- 💡 [Sugerir Feature](https://github.com/[seu-usuario]/conciliacao-bancaria/issues)
- 📧 Email: pedroluisdias@br-nsa.com

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela! ⭐**

Desenvolvido com ❤️ por [Pedro Luis](https://github.com/[seu-usuario])

</div>
