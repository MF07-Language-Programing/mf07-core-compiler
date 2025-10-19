# Teste de For-In e For-Of loops 
intent test_for_in_of() {
    sout("=== Teste For-In Loops ===")
    
    # Criar uma lista
    var numbers = new List()
    numbers.append(10)
    numbers.append(20) 
    numbers.append(30)
    
    sout("Lista original:", numbers.toString())
    
    # For-in: itera sobre os valores
    sout("For-In loop:")
    for (var num in numbers) {
        sout("  Valor:", num.toString())
    }
    
    # For-of: itera sobre os valores
    sout("For-Of loop:")  
    for (var value of numbers) {
        sout("  For-of value:", value.toString())
    }
    
    sout("Comparando com for tradicional:")
    
    # Por enquanto usando for tradicional
    for (var i: int = 0; i < 3; i = i + 1) {
        var value = numbers.get(i)
        sout("  Posição ", i.toString(), ": ", value.toString())
    }
}
test_for_in_of()
