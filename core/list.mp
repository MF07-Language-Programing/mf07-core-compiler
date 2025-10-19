# core/list.mp
# Lista genérica moderna com tipagem forte e suporte a IA

# Lista genérica simples para teste inicial
class List<T> {
    private var data
    private var _size: int = 0
    private var capacity: int = 10
    private var elementType: string = "any"

    # Construtor flexível: aceita tipo explícito e/ou valores iniciais
    intent constructor(elementTypeOrValues, maybeValues) {
        this.data = mf.collections.List()
        this.capacity = 10
        this._size = 0
        this.elementType = "any"

        var declaredType = null
        var initialValues = null

        if (elementTypeOrValues != null) {
            var firstArgType = type(elementTypeOrValues)
            if (this._isStringType(firstArgType)) {
                declaredType = this._normalizeType(elementTypeOrValues)
            } else if (firstArgType == "list") {
                initialValues = elementTypeOrValues
            }
        }

        if (maybeValues != null) {
            var secondArgType = type(maybeValues)
            if (secondArgType == "list") {
                initialValues = maybeValues
            } else if (declaredType == null and this._isStringType(secondArgType)) {
                declaredType = this._normalizeType(maybeValues)
            }
        }

        if (declaredType != null) {
            this.elementType = declaredType
        }

        if (initialValues != null) {
            if (type(initialValues) != "list") {
                throw new Error("Initial values for List must be provided as a list")
            }
            if (declaredType == null) {
                this._inferElementType(initialValues)
            }
            this.initial_values(initialValues)
        }
    }

    intent _isStringType(typeName: string): bool {
        return typeName == "string" or typeName == "str" or typeName == "String"
    }

    intent _normalizeType(typeName: string) {
        if (typeName == "string" or typeName == "String" or typeName == "str") {
            return "str"
        }
        if (typeName == "Int") {
            return "int"
        }
        if (typeName == "Float") {
            return "float"
        }
        return typeName
    }

    intent _inferElementType(values: list) {
        this.elementType = "any"
        if (len(values) == 0) {
            return
        }

        var firstType = this._normalizeType(type(values[0]))
        var allSameType = true
        var i = 1
        while (i < len(values)) {
            if (this._normalizeType(type(values[i])) != firstType) {
                allSameType = false
                break
            }
            i = i + 1
        }

        if (allSameType) {
            this.elementType = firstType
        }
    }

    intent initial_values(values: list) {
        var i = 0
        while (i < len(values)) {
            this.append(values[i])
            i = i + 1
        }
    }

    # Validação rigorosa de tipos
    intent _validateType(item) {
        if (this.elementType == "any") {
            return true
        }

        if (item == null) {
            return this.elementType == "null"
        }

        var itemType = this._normalizeType(type(item))
        return itemType == this.elementType
    }

    # Implementação básica
    intent size(): int {
        return this._size
    }

    intent isEmpty(): bool {
        return this._size == 0
    }

    intent clear() {
        this.data = mf.collections.List()
        this._size = 0
    }

    # Métodos específicos de List
    intent append(item) {
        if (not this._validateType(item)) {
            var expectedType = this.elementType
            var actualType = this._normalizeType(type(item))
            print("TypeError: Cannot append " + actualType + " to List<" + expectedType + ">")
            return false
        }
        this.data.push(item)
        this._size = this._size + 1
        return true
    }

    intent get(index: int) {
        if (index >= 0 and index < this._size) {
            return this.data[index]
        }
        return null
    }

    intent length(): int {
        return this._size
    }

    intent __raw__() {
        return this.data
    }

    intent toString(): string {
        if (this._size == 0) {
            return "[]"
        }

        var result = "["
        for (var i: int = 0; i < this._size; i = i + 1) {
            if (i > 0) {
                result = result + ", "
            }
            var item = this.get(i)
            result = "{result}{item}"
        }
        result = result + "]"
        return result
    }
}
