# 🟣 CorpLang Advanced v2.7.0 - Logs Profissionais

## 🆕 **NOVIDADES DESTA VERSÃO:**

### 📊 **LOGS OTIMIZADAS E PROFISSIONAIS**
-  **95% redução** nas logs internas desnecessárias
-  **Saída limpa** focada no programa do usuário
-  **Resumo conciso** do carregamento do core
-  **4 níveis** de logging configuráveis

**ANTES (v2.6.0):**
```
[DEBUG] [core-loader] Diretório core: D:\users\...
[INFO] [core-loader] Arquivos core encontrados: ['embedlist.mp', ...]
[DEBUG] [core-loader] Iniciando carregamento do módulo core 'embedlist' -> ...
[DEBUG] [core-loader] AST parseada com sucesso para embedlist.mp
... (45+ linhas de logs internas) ...
```

**AGORA (v2.7.0):**
```
CorpLang Core: 11 modules loaded (embedlist, json, list, map, math, matrix, objects, requests, set, string, utils)
Running type checker...
Type checking completed with 0 error(s).
```

---

## 🛠️ **FERRAMENTAS DE LOGGING INCLUÍDAS:**

### **📝 Níveis Disponíveis:**
- **`prod`**  **PADRÃO** - Logs profissionais limpas
- **`dev`** - Desenvolvimento com logs úteis e concisas  
- **`quiet`** - Silencioso, apenas erros críticos
- **`summary`** - Resumo balanceado de startup

### **⚙️ Como Alternar Níveis:**
```bash
# Usar no diretório da linguagem CorpLang:
python switch_logging.py prod      # Produção (padrão)
python switch_logging.py dev       # Desenvolvimento  
python switch_logging.py quiet     # Silencioso
python switch_logging.py summary   # Resumo balanceado
```

---

## 🎯 **RECURSOS COMPLETOS:**

### **🎨 Syntax Highlighting Avançado:**
-  **87+ padrões** de sintaxe mapeados
-  **Cores únicas** (roxo/azul/laranja) 
-  **Diferenciação** de outras linguagens

### **💡 IntelliSense & Snippets:**
-  **25+ snippets** corporativos prontos
-  **Auto-complete** inteligente
-  **Documentação** integrada

### **🌈 Tema Visual:**
-  **CorpLang Dark Theme** exclusivo
-  **Paleta corporativa** profissional
-  **Contraste otimizado** para produtividade

### **📁 Ícones de Arquivo:**
-  **Ícones específicos** para arquivos `.mp`
-  **Identidade visual** da linguagem CorpLang
-  **Preserva ícones** de outros tipos de arquivo

---

## 📦 **INSTALAÇÃO:**

### **🚀 Método 1: Installer Automático (Recomendado)**
```bash
# Windows (Batch)
install_v2.7.0.bat

# Windows (PowerShell)  
install_v2.7.0.ps1
```

### **⚙️ Método 2: Manual**
```bash
code --install-extension corp-lang-2.7.0.vsix
```

### **🔄 Atualização de Versão Anterior:**
```bash
# Desinstalar versão anterior
code --uninstall-extension mf07.corp-lang

# Instalar nova versão
code --install-extension corp-lang-2.7.0.vsix
```

---

## 📋 **CHANGELOG v2.7.0:**

### **✨ Adicionado:**
- Sistema de logs profissionais com 4 níveis
- Script `switch_logging.py` para alternar níveis
- Documentação completa de logging
- Logs otimizadas no core da linguagem

### **🔧 Melhorado:**
- Redução de 95% nas logs internas
- Saída muito mais limpa e profissional
- Foco na saída do programa do usuário
- Performance visual melhorada

### **🐛 Corrigido:**
- Logs excessivamente verbosas removidas
- Informações desnecessárias filtradas
- Experiência de usuário mais profissional

---

## 🏢 **PARA DESENVOLVEDORES CORPORATIVOS:**

### **📊 Ambiente Produção:**
```bash
python switch_logging.py prod
```
- Saída limpa e profissional
- Apenas informações essenciais
- Ideal para apresentações e demos

### **🛠️ Ambiente Desenvolvimento:**  
```bash
python switch_logging.py dev
```
- Logs úteis sem verbosidade
- Balance entre debug e limpeza
- Ideal para development/testing

---

## 💜 **CorpLang Advanced v2.7.0**

**Uma experiência profissional completa para desenvolvimento corporativo!**

- 🎨 **Syntax highlighting** único e avançado
- 💡 **IntelliSense** completo com snippets
- 🌈 **Tema visual** corporativo exclusivo  
- 📁 **Ícones** específicos para arquivos CorpLang
- 📊 **Logs profissionais** otimizadas
- 🛠️ **Ferramentas** de configuração flexíveis

**Reinicie o VS Code após a instalação para ativar todos os recursos!** 🚀