# Exercício de Optional combinado com coleções

# Verifica Optional<List<int>>
intent testOptionalList() {
    var numbers: Optional[List<int>] = null
    if (Optional.isNone(numbers)) {
        print("Lista opcional vazia")
    }

    numbers = new List([])
    numbers.append(10)
    numbers.append(20)

    if (Optional.isSome(numbers)) {
        var unwrapped = Optional.unwrap(numbers)
        print("Tamanho:", unwrapped.size())
        print("Primeiro elemento:", unwrapped.get(0))
    }

    var doubled = Optional.unwrapOr(numbers, new List([]))
    print("Length via unwrapOr:", doubled.size())
}

# Optional<Map<string, int>>
intent testOptionalMap() {
    var stats: Optional[Map<string, int>] = null
    var result = Optional.unwrapOr(stats, Map.default())
    print("Entradas iniciais:", result.size())

    stats = Map.default()
    stats.put("xp", 150)
    stats.put("level", 12)

    if (Optional.isSome(stats)) {
        var actual = Optional.unwrap(stats)
        print("XP:", actual.get("xp"))
        print("Level:", actual.get("level"))
    }
}

# Optional em parâmetros e retorno
intent maybeGetFirst(values: Optional[List]): Optional[int] {
    if (Optional.isNone(values)) {
        return null
    }
    var items = Optional.unwrap(values)
    if (items.size() == 0) {
        return null
    }
    return items.get(0)
}

intent testOptionalReturn() {
    var empty: Optional[List] = new List([])
    var first = maybeGetFirst(empty)
    if (Optional.isNone(first)) {
        print("Nenhum item na lista vazia")
    }

    var filled: Optional[List] = new List([])
    filled.append(99)
    var firstValue = maybeGetFirst(filled)
    print("Primeiro valor:", Optional.unwrapOr(firstValue, -1))
}

testOptionalList()
testOptionalMap()
testOptionalReturn()
