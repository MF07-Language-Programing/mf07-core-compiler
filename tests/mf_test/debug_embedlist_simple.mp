# Teste isolado de EmbedList para debugar
var documents: EmbedList<str> = new EmbedList()
documents.append("Teste 1")
documents.append("Teste 2")

print("EmbedList criada:", documents.toString())

# Tentar busca semântica
print("Iniciando busca semântica...")
var similar = documents.findSimilar("teste", 1)
print("Busca concluída, resultados:")
print("Tipo de similar:", type(similar))
print("Tamanho:", len(similar))

# Tentar iterar
print("Tentando iterar:")
for (var i: int = 0; i < len(similar); i = i + 1) {
    var doc = similar[i]
    print("Item " + i.toString() + ":", type(doc))
    print("Valor:", doc)
}