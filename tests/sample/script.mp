var _global_user = '{name: "Lucas"}';
# Exemplo 1: Variáveis e operações básicas
print("1. Exemplo básico:")
var x = 10;
var y = 20;
var resultado = x + y;
print("Resultado:", resultado);
print()

# Exemplo 2: Funções
print("2. Funções:")
intent calcular_bonus(salario, percentual) {
    return salario * (percentual / 100);
}

var salario_base = 5000;
var bonus = calcular_bonus(salario_base, 15);
print("Salário base:", salario_base);
print("Bônus (15%):", bonus);
print("Total:", salario_base + bonus);
print()

# Exemplo 3: Estruturas de controle
print("3. Estruturas de controle:")
var idade = 25;

if (idade >= 18) {
    print("Maior de idade");
} else {
    print("Menor de idade");
}

var contador = 0;
while (contador < 3) {
    print("Contador:", contador);
    contador = contador + 1;
}
print()

# Exemplo 4: Operações com datasets
print("4. Operações com datasets:")
# Carregamento de dataset
dataset load funcionarios("funcionarios.csv");

# Análise básica
# dataset analyze funcionarios;

# Filtros (simulado)
dataset filter funcionarios;

# Salvamento
dataset save funcionarios;
print()

# Exemplo 5: Modelos de Machine Learning
print("5. Modelos de Machine Learning:")
# Criação de modelo
model create predictor_salario(type="linear_regression");

# Treinamento
# model train predictor_salario(dataset="funcionarios");

# Predição
# model predict predictor_salario(input="novo_funcionario");

print()

# Exemplo 6: Programa completo
print("6. Programa completo de análise:")
# Programa de análise de RH
print("=== Sistema de Análise de RH ===");

# Carregamento de dados
dataset load funcionarios("funcionarios.csv");
# dataset analyze funcionarios;

# Função para calcular estatísticas
intent calcular_media_salarial() {
    print("Calculando média salarial...");
    return 5500; # Simulado
}

# Análise salarial
var media_salario = calcular_media_salarial();
print("Média salarial:", media_salario);

# Criação e treinamento de modelo
model create modelo_promocao(type="classification");
# model train modelo_promocao(dataset="funcionarios");

# Predição para novos funcionários
var score_promocao = 0.75;
if (score_promocao > 0.7) {
    print("Funcionário elegível para promoção");
} else {
    print("Funcionário não elegível para promoção");
}

print("Análise concluída!");
print(_global_user)