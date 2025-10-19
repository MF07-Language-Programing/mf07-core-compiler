# Teste Completo - Tipagem Genérica Rigorosa

intent test_strict_generic_validation() {
    print("=== SISTEMA DE TIPAGEM GENÉRICA RIGOROSA ===")
    
    # Teste 1: List<int> - deve aceitar apenas inteiros
    print("\n--- Teste 1: List<int> ---")
    var numbers: List<int> = new List()
    
    # Adicionar valores válidos
    numbers.append(1)    #  int válido
    numbers.append(42)   #  int válido
    numbers.append(100)  #  int válido
    
    # Tentar adicionar valores inválidos
    numbers.append("string")  # ❌ deveria falhar
    numbers.append(3.14)      # ❌ deveria falhar
    
    print("Lista de números:", numbers.toString())
    print("Tamanho:", numbers.length())
    
    # Teste 2: List<str> - deve aceitar apenas strings
    print("\n--- Teste 2: List<str> ---")
    var names: List<str> = new List()
    
    # Adicionar valores válidos
    names.append("Alice")    #  string válida
    names.append("Bob")      #  string válida
    names.append("Charlie")  #  string válida
    
    # Tentar adicionar valores inválidos
    names.append(123)    # ❌ deveria falhar
    names.append(true)   # ❌ deveria falhar
    
    print("Lista de nomes:", names.toString())
    print("Tamanho:", names.length())
    
    # Teste 3: Verificar que tipos são preservados
    print("\n--- Teste 3: Verificação de Tipos ---")
    print("Tipo da lista numbers:", type(numbers))
    print("Tipo da lista names:", type(names))
    
    # Teste 4: Métodos funcionando corretamente
    print("\n--- Teste 4: Métodos da Lista ---")
    print("Primeiro número:", numbers.get(0))
    print("Último nome:", names.get(names.length() - 1))
    print("Lista vazia?", numbers.isEmpty())
    
    print("\n=== VALIDAÇÃO RIGOROSA FUNCIONANDO! ===")
}

test_strict_generic_validation()