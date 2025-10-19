# --- Matriz Moderna com For Loops ---
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
    intent showBoth() {
        print("x=", this.getX(), "y=", this.getY())
    }
}

intent test_matriz_moderna() {
    var rows: int = 4
    var cols: int = 6
    var matrix = new List()

    print("=== Criando Matriz Moderna com For Loops ===")

    # Cria matriz usando for loops tradicionais modernos
    for (var i: int = 0; i < rows; i = i + 1) {
        var row = new List()
        
        for (var j: int = 0; j < cols; j = j + 1) {
            var obj = new Derived(i + 1, (j + 1) * 2)
            row.append(obj)
        }
        
        matrix.append(row)
        print("Linha ", (i + 1).toString(), " criada com ", cols.toString(), " elementos")
    }

    # Cabeçalho da tabela com for loop
    var header = "ROW "
    for (var col: int = 1; col <= cols; col = col + 1) {
        header = header + " C" + col.toString()
    }
    
    print("")
    print("Matriz Final (" + rows.toString() + "x" + cols.toString() + "):")
    print(header)
    print("----", "-------------------------")

    # Imprime matriz com for loops
    for (var i: int = 0; i < rows; i = i + 1) {
        var row = matrix.get(i)
        var line = " " + (i + 1).toString() + " |"
        
        for (var j: int = 0; j < cols; j = j + 1) {
            var cell = row.get(j)
            var value = cell.getX() + cell.getY()
            line = line + "  " + value.toString()
        }
        
        print(line)
    }

    print("")
    print(" Matriz moderna com for loops criada com sucesso!")
    
    # Demonstra acesso individual
    print("")
    print("=== Teste de Acesso Individual ===")
    for (var test_i: int = 0; test_i < 2; test_i = test_i + 1) {
        for (var test_j: int = 0; test_j < 2; test_j = test_j + 1) {
            var cell = matrix.get(test_i).get(test_j)
            print("Posição [", test_i.toString(), ",", test_j.toString(), 
                  "]: x=", cell.getX().toString(), 
                  " y=", cell.getY().toString(),
                  " soma=", (cell.getX() + cell.getY()).toString())
        }
    }
}

# Teste direto de for loops
intent test_for_loops_basico() {
    print("")
    print("=== Teste Básico de For Loops ===")
    
    print("Contagem crescente:")
    for (var i: int = 1; i <= 5; i = i + 1) {
        print("  Número: ", i.toString())
    }
    
    print("Contagem decrescente:")
    for (var countdown: int = 5; countdown >= 1; countdown = countdown - 1) {
        print("  Countdown: ", countdown.toString())
    }
    
    print("Tabuada do 3:")
    for (var mult: int = 1; mult <= 10; mult = mult + 1) {
        var result = 3 * mult
        print("  3 x ", mult.toString(), " = ", result.toString())
    }
}

# Executa todos os testes
test_for_loops_basico()
test_matriz_moderna()