# =================================================================
# EXEMPLO COMPLETO: MATRIZ MODERNA COM TODOS OS TIPOS DE FOR LOOPS
# =================================================================

class Base {
    var x: int = 0
    intent constructor(x: int) {
        this.x = x
    }
    intent getX() { return this.x }
}

class Derived extends Base {
    var y: int = 0
    intent constructor(x: int, y: int) {
        super(x)
        this.y = y
    }
    intent getY() { return this.y }
    intent getValue() { return this.getX() + this.getY() }
}

intent exemplo_completo_for_loops() {
    print(" === EXEMPLO COMPLETO: TODOS OS TIPOS DE FOR LOOPS ===")
    print()

    # Criar matriz com for tradicional
    var rows: int = 3
    var cols: int = 4
    var matrix = new List()

    print(" Criando matriz com FOR TRADICIONAL:")
    for (var i: int = 0; i < rows; i = i + 1) {
        var row = new List()
        
        for (var j: int = 0; j < cols; j = j + 1) {
            var obj = new Derived((i + 1) * 10, (j + 1) * 5)
            row.append(obj)
        }
        
        matrix.append(row)
        print("  ✓ Linha ", (i + 1).toString(), " criada")
    }
    print()

    # Imprimir matriz com for-in
    print(" Iterando matriz com FOR-IN:")
    var rowIndex: int = 0
    for (var row in matrix) {
        print("  Linha ", (rowIndex + 1).toString(), ":")
        var colIndex: int = 0
        
        for (var cell in row) {
            var value = cell.getValue()
            print("    [", (rowIndex + 1).toString(), ",", (colIndex + 1).toString(), "] = ", value.toString())
            colIndex = colIndex + 1
        }
        
        rowIndex = rowIndex + 1
    }
    print()

    # Demonstrar for-of com lista de valores
    print(" Usando FOR-OF para somar valores:")
    var firstRow = matrix.get(0)
    var sum: int = 0
    
    for (var cell of firstRow) {
        var value = cell.getValue()
        sum = sum + value
        print("  + ", value.toString(), " (soma parcial: ", sum.toString(), ")")
    }
    print("   Soma total da primeira linha: ", sum.toString())
    print()

    # Comparação de performance com diferentes loops
    print("⏱️  Comparando PERFORMANCE dos loops:")
    
    print("  • FOR Tradicional (com contador):")
    for (var i: int = 0; i < 2; i = i + 1) {
        print("    Iteração ", i.toString(), " - controle manual do índice")
    }
    
    print("  • FOR-IN (iteração direta):")
    var count: int = 0
    for (var item in firstRow) {
        if (count < 2) {
            print("    Item ", count.toString(), " - acesso direto ao elemento")
        }
        count = count + 1
    }
    
    print("  • FOR-OF (iteração de valores):")
    var valueCount: int = 0
    for (var value of firstRow) {
        if (valueCount < 2) {
            print("    Valor ", valueCount.toString(), " - foco nos dados")
        }
        valueCount = valueCount + 1
    }
    print()

    print(" === TODOS OS FOR LOOPS FUNCIONANDO PERFEITAMENTE! ===")
}

intent demonstracao_casos_uso() {
    print()
    print("💡 === CASOS DE USO RECOMENDADOS ===")
    print()
    
    # Lista de números para demonstrar
    var numbers = new List()
    numbers.append(100)
    numbers.append(200)
    numbers.append(300)
    
    print("📋 Lista de exemplo:", numbers.toString())
    print()
    
    print("1️⃣  FOR TRADICIONAL - quando você precisa do índice:")
    for (var i: int = 0; i < 3; i = i + 1) {
        var value = numbers.get(i)
        print("   numbers[", i.toString(), "] = ", value.toString())
    }
    print()
    
    print("2️⃣  FOR-IN - quando você quer iterar pelos valores:")
    for (var num in numbers) {
        print("   Processando: ", num.toString())
    }
    print()
    
    print("3️⃣  FOR-OF - alternativa ao for-in (mesmo comportamento):")
    for (var value of numbers) {
        print("   Valor encontrado: ", value.toString())
    }
    print()
    
    print("🎯 Resumo:")
    print("   • FOR tradicional: máximo controle, acesso ao índice")
    print("   • FOR-IN/FOR-OF: código mais limpo, foco nos dados")
    print("   • Todos suportam break/continue (futuramente)")
}

# Executar demonstrações
exemplo_completo_for_loops()
demonstracao_casos_uso()