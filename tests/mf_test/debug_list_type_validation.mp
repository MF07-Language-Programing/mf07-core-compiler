# Debug - Validação de Tipos em List<T>

intent test_list_type_validation() {
    print("=== Teste de Validação de Tipos ===")
    
    # Criar lista de inteiros
    var numbers: List<int> = new List()
    print("Lista criada para int")
    
    # Verificar tipo da lista
    var listType = type(numbers)
    print("Tipo da lista:", listType)
    
    # Tentar adicionar inteiro (deve funcionar)
    print("Tentando adicionar 1 (int)...")
    var result1 = numbers.append(1)
    print("Resultado:", result1)
    
    # Tentar adicionar string (deve falhar)  
    print("Tentando adicionar 'test' (str)...")
    var result2 = numbers.append("test")
    print("Resultado:", result2)
    
    print("Lista final:", numbers.toString())
}

test_list_type_validation()