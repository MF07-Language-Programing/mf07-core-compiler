# test de Tipagem Genérica
intent test_generic_types() {
    # Teste simples com List<int>
    var numbers: List<int> = new List()
    numbers.append(1)
    numbers.append(2)
    numbers.append(3)
    
    print("Lista de números:", numbers.toString())
    
    # Teste com List<str>
    var names: List<str> = new List()
    names.append("CEO")
    names.append("MF07")
    names.append(1) # Deve gerar erro de tipo
    
    print("Lista de nomes:", names.toString())
    
    # Teste com Map<str, int>
    print("Teste com Map<str, int>:")
    var ages: HashMap<str, int> = new Map()
    print("Ages map:", Object.keys(ages.get("_fields")))
    ages.set("CEO", 25)

    
    print("Tipagem genérica funcionando!")
}

test_generic_types()