# ========================================================================
# DEMONSTRAÇÃO INTERATIVA - CorpLang v1.0
# Linguagem de Programação Corporativa
# ========================================================================

intent banner(titulo) {
    print("╔══════════════════════════════════════════════════════════════════════╗");
    print("║                          {titulo}                           ║");
    print("╚══════════════════════════════════════════════════════════════════════╝");
    waitSeconds(1);
}

intent secao(nome) {
    print("");
    print("┌─────────────────────────────────────────────────────────────────────┐");
    print("│ {nome}");
    print("└─────────────────────────────────────────────────────────────────────┘");
    waitSeconds(1);
}

intent aguardar(segundos) {
    print("⏱️  Aguardando {segundos} segundos...");
    waitSeconds(segundos);
}

intent separador() {
    print("─────────────────────────────────────────────────────────────────────");
    waitSeconds(0.5);
}

# ========================================================================
# INÍCIO DA DEMONSTRAÇÃO
# ========================================================================

banner("CORPLANG DEMO");

print("🚀 Bem-vindo à demonstração interativa da CorpLang!");
print("    Uma linguagem de programação voltada para ambientes corporativos");
print("");
aguardar(2);

# ========================================================================
# SEÇÃO 1: DECLARAÇÃO DE VARIÁVEIS
# ========================================================================

secao("1. DECLARAÇÃO DE VARIÁVEIS E TIPOS");

print("📝 Declarando variáveis básicas...");
var nome = "Lucas";
var idade = 28;
var salario = 5500.50;
var ativo = true;

print("   • Nome: {nome}");
print("   • Idade: {idade}");
print("   • Salário: R$ {salario}");
print("   • Ativo: {ativo}");
aguardar(2);

# ========================================================================
# SEÇÃO 2: ESTRUTURAS DE DADOS JSON
# ========================================================================

secao("2. ESTRUTURAS DE DADOS JSON NATIVAS");

print("📊 Criando objeto JSON de funcionário...");
var funcionario = {
    "nome": "João Silva",
    "idade": 32,
    "departamento": "TI",
    "cargo": "Desenvolvedor Senior",
    "salario": 8500.00,
    "ativo": true,
    "projetos": ["Sistema ERP", "API Gateway", "Dashboard Analytics"]
};

print("   Funcionário cadastrado:");
print("   • Nome: {funcionario.nome}");
print("   • Cargo: {funcionario.cargo}");
print("   • Departamento: {funcionario.departamento}");
aguardar(2);

print("📋 Criando array de dados corporativos...");
var metricas = [
    {"mes": "Janeiro", "vendas": 150000, "meta": 140000},
    {"mes": "Fevereiro", "vendas": 165000, "meta": 160000},
    {"mes": "Março", "vendas": 142000, "meta": 150000}
];

print("   Métricas mensais carregadas: {metricas}");
aguardar(2);

# ========================================================================
# SEÇÃO 3: FUNÇÕES E LÓGICA DE NEGÓCIO
# ========================================================================

secao("3. FUNÇÕES E LÓGICA DE NEGÓCIO");

print("⚙️ Definindo funções corporativas...");

intent calcularBonus(salario_base, performance) {
    var bonus = 0;
    if (performance >= 90) {
        bonus = salario_base * 0.15;
        print("   💰 Performance excelente! Bônus de 15%");
    }
    if (performance >= 70) {
        bonus = salario_base * 0.10;
        print("   💼 Performance boa! Bônus de 10%");
    } else {
        bonus = salario_base * 0.05;
        print("   📈 Performance regular. Bônus de 5%");
    }
    return bonus;
}

print("   Calculando bônus para diferentes performances...");
aguardar(1);

var bonus_excelente = calcularBonus(8500, 95);
print("   • Bônus (95% performance): R$ {bonus_excelente}");

var bonus_bom = calcularBonus(8500, 80);
print("   • Bônus (80% performance): R$ {bonus_bom}");

var bonus_regular = calcularBonus(8500, 60);
print("   • Bônus (60% performance): R$ {bonus_regular}");
aguardar(2);

# ========================================================================
# SEÇÃO 4: LOOPS E PROCESSAMENTO DE DADOS
# ========================================================================

secao("4. PROCESSAMENTO DE DADOS EM LOTE");

print("🔄 Processando dados em loop...");
var contador = 1;
var total_vendas = 0;

while (contador <= 3) {
    print("   📊 Processando mês {contador}...");
    
    if (contador == 1) {
        total_vendas = total_vendas + 150000;
        print("      Janeiro: R$ 150.000");
    }
    if (contador == 2) {
        total_vendas = total_vendas + 165000;
        print("      Fevereiro: R$ 165.000");
    } else {
        total_vendas = total_vendas + 142000;
        print("      Março: R$ 142.000");
    }
    
    contador = contador + 1;
    waitSeconds(1);
}

print("   💹 Total de vendas no trimestre: R$ {total_vendas}");
var media_vendas = total_vendas / 3;
print("   📈 Média mensal: R$ {media_vendas}");
aguardar(2);

# ========================================================================
# SEÇÃO 7: FUNÇÕES BUILT-IN E UTILIDADES
# ========================================================================

secao("7. FUNÇÕES BUILT-IN E UTILIDADES");

print("🛠️ Demonstrando funções utilitárias...");

var empresa = "TechCorp Solutions";
var tamanho_nome = len(empresa);
var tipo_salario = type(salario);

print("   • Empresa: {empresa}");
print("   • Tamanho do nome: {tamanho_nome} caracteres");
print("   • Tipo da variável salário: {tipo_salario}");
aguardar(1);

print("🔧 Manipulando dados JSON...");
var dados_json = '{"produto": "Software ERP", "versao": "2.1", "licencas": 500}';
var dados_objeto = parseJson(dados_json);
var chaves = getKeys(dados_objeto);
var valores = getValues(dados_objeto);

print("   • Chaves do objeto: {chaves}");
print("   • Valores do objeto: {valores}");
aguardar(2);

# ========================================================================
# SEÇÃO 8: RELATÓRIO FINAL
# ========================================================================

secao("8. RELATÓRIO FINAL DE DEMONSTRAÇÃO");

print("📋 Gerando relatório final...");
aguardar(1);

var relatorio = {"sistema": "CorpLang Demo", "versao": "1.0", "desenvolvedor": "test", "funcionarios_processados": 3, "total_vendas": "total_vendas", "modelos_treinados": 0, "datasets_analisados": 0};

print("   ╔═══════════════════════════════════════════════════╗");
print("   ║                 RELATÓRIO FINAL                   ║");
print("   ╠═══════════════════════════════════════════════════╣");
print("   ║ Sistema: {relatorio.sistema}");
print("   ║ Versão: {relatorio.versao}");
print("   ║ Desenvolvedor: {relatorio.desenvolvedor}");
print("   ║ Funcionários processados: {relatorio.funcionarios_processados}");
print("   ║ Total de vendas: R$ {relatorio.total_vendas}");
print("   ║ Modelos treinados: {relatorio.modelos_treinados}");
print("   ║ Datasets analisados: {relatorio.datasets_analisados}");
print("   ╚═══════════════════════════════════════════════════╝");
aguardar(2);

# ========================================================================
# FINALIZAÇÃO
# ========================================================================

separador();
print(" Demonstração concluída com sucesso!");
print("🎉 Obrigado por conhecer a CorpLang!");
print("📧 Para mais informações, contate o desenvolvedor: {nome}");
print("");
print("🚀 CorpLang - Transformando dados corporativos em insights!");
separador();

# ========================================================================
# FUNÇÃO PRINCIPAL
# ========================================================================

intent main() {
    print("🎯 Iniciando demonstração completa da CorpLang...");
    print("    Prepare-se para uma jornada através das funcionalidades!");
    aguardar(3);
}

main();
