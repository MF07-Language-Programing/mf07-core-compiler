# core/matrix.mp
# Sistema de Matrix matemático com tipagem genérica Matrix<T>

class Matrix<T> {
    private var data
    private var rows: int
    private var cols: int  
    private var elementType: string
    
    intent constructor(elementType, rows, cols) {
        if (elementType == null) {
            this.elementType = "float"
        } else {
            this.elementType = elementType
        }
        
        if (rows == null) {
            this.rows = 1
        } else {
            this.rows = rows
        }
        
        if (cols == null) {
            this.cols = 1
        } else {
            this.cols = cols
        }
        
        # Inicializar matriz como lista de listas
        this.data = mf.collections.List()
        for (var i: int = 0; i < this.rows; i = i + 1) {
            var row = mf.collections.List()
            for (var j: int = 0; j < this.cols; j = j + 1) {
                if (this.elementType == "int") {
                    row.push(0)
                } else {
                    row.push(0.0)
                }
            }
            this.data.push(row)
        }
    }
    
    # Validação de tipos para Matrix
    intent _validateType(element) {
        if (this.elementType == "any") {
            return true
        }
        
        var actualType = ""
        if (element == null) {
            actualType = "null"
        } else {
            actualType = type(element)
        }
        
        # Suporte a conversões automáticas para números
        if (this.elementType == "float" and actualType == "int") {
            return true
        }
        if (this.elementType == "string" and actualType == "str") {
            return true
        }
        if (this.elementType == "str" and actualType == "string") {
            return true
        }
        
        if (actualType != this.elementType) {
            print("TypeError: Expected " + this.elementType + " but got " + actualType + " in Matrix<" + this.elementType + ">")
            return false
        }
        return true
    }
    
    intent set(row: int, col: int, value) {
        if (row < 0 or row >= this.rows) {
            print("IndexError: Row " + row + " out of bounds")
            return false
        }
        if (col < 0 or col >= this.cols) {
            print("IndexError: Column " + col + " out of bounds")
            return false
        }
        if (not this._validateType(value)) {
            return false
        }
        
        # Recrear array inteiro substituindo elemento específico
        var newData = mf.collections.List()
        var i = 0
        while (i < this.rows) {
            if (i == row) {
                var newRow = mf.collections.List()
                var j = 0
                while (j < this.cols) {
                    if (j == col) {
                        newRow.push(value)
                    } else {
                        newRow.push(this.data[i][j])
                    }
                    j = j + 1
                }
                newData.push(newRow)
            } else {
                newData.push(this.data[i])
            }
            i = i + 1
        }
        this.data = newData
        return true
    }
    
    intent get(row: int, col: int) {
        if (row < 0 or row >= this.rows) {
            return null
        }
        if (col < 0 or col >= this.cols) {
            return null
        }
        
        var rowData = this.data[row]
        return rowData[col]
    }
    
    intent getRows(): int {
        return this.rows
    }
    
    intent getCols(): int {
        return this.cols
    }
    
    # Operações matemáticas
    intent add(other) {
        if (other.getRows() != this.rows or other.getCols() != this.cols) {
            print("DimensionError: Cannot add matrices of different sizes")
            return null
        }
        
        var result = new Matrix(this.elementType, this.rows, this.cols)
        for (var i: int = 0; i < this.rows; i = i + 1) {
            for (var j: int = 0; j < this.cols; j = j + 1) {
                var a = this.get(i, j)
                var b = other.get(i, j)
                result.set(i, j, a + b)
            }
        }
        return result
    }
    
    intent multiply(other) {
        if (this.cols != other.getRows()) {
            print("DimensionError: Cannot multiply matrices - incompatible dimensions")
            return null
        }
        
        var result = new Matrix(this.elementType, this.rows, other.getCols())
        for (var i: int = 0; i < this.rows; i = i + 1) {
            for (var j: int = 0; j < other.getCols(); j = j + 1) {
                var sum = 0
                for (var k: int = 0; k < this.cols; k = k + 1) {
                    var a = this.get(i, k)
                    var b = other.get(k, j)
                    sum = sum + (a * b)
                }
                result.set(i, j, sum)
            }
        }
        return result
    }
    
    intent transpose() {
        var result = new Matrix(this.elementType, this.cols, this.rows)
        for (var i: int = 0; i < this.rows; i = i + 1) {
            for (var j: int = 0; j < this.cols; j = j + 1) {
                var value = this.get(i, j)
                result.set(j, i, value)
            }
        }
        return result
    }
    
    intent toString(): string {
        var result = "Matrix<" + this.elementType + ">[\n"
        for (var i: int = 0; i < this.rows; i = i + 1) {
            result = result + "  ["
            for (var j: int = 0; j < this.cols; j = j + 1) {
                if (j > 0) {
                    result = result + ", "
                }
                var value = this.get(i, j)
                result = result + value
            }
            result = result + "]\n"
        }
        result = result + "]"
        return result
    }
}