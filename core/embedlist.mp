# core/embedlist.mp
# EmbedList com IA integrada para embeddings e busca semântica

class EmbedList<T> {
    private var data
    private var embeddings
    private var elementType: string
    private var _size: int = 0
    private var aiEnabled: bool = true
    
    intent constructor(elementType) {
        if (elementType == null) {
            this.elementType = "any"
        } else {
            this.elementType = elementType
        }
        
        this.data = mf.collections.List()
        this.embeddings = mf.collections.List()
        this._size = 0
        this.aiEnabled = true
        
        print("EmbedList<" + this.elementType + "> initialized with AI embeddings")
    }
    
    # Validação rigorosa de tipos
    intent _validateType(item) {
        if (this.elementType == "any") {
            return true
        }
        
        var actualType = ""
        if (item == null) {
            actualType = "null"
        } else {
            actualType = type(item)
        }
        
        # Suporte str/string
        if (this.elementType == "string" and actualType == "str") {
            return true
        }
        if (this.elementType == "str" and actualType == "string") {
            return true
        }
        
        if (actualType != this.elementType) {
            print("TypeError: Expected " + this.elementType + " but got " + actualType + " in EmbedList<" + this.elementType + ">")
            return false
        }
        return true
    }
    
    # Gerar embedding simulado (em produção seria IA real)
    intent _generateEmbedding(item) {
        if (not this.aiEnabled) {
            return null
        }
        
        # Simular embedding baseado no item
        var embedding = mf.collections.List()
        var itemStr = item
        
        # Gerar embedding de 5 dimensões baseado no conteúdo
        var hash = 0
        var i = 0
        while (i < len(itemStr)) {
            hash = hash + i
            i = i + 1
        }
        
        # Embedding simulado
        embedding.push((hash % 100) / 100.0)
        embedding.push(((hash * 2) % 100) / 100.0)
        embedding.push(((hash * 3) % 100) / 100.0)
        embedding.push(((hash * 5) % 100) / 100.0)
        embedding.push(((hash * 7) % 100) / 100.0)
        
        return embedding
    }
    
    intent append(item) {
        if (not this._validateType(item)) {
            return false
        }
        
        # Adicionar item
        this.data.push(item)
        
        # Gerar e armazenar embedding
        var embedding = this._generateEmbedding(item)
        this.embeddings.push(embedding)
        
        this._size = this._size + 1
        
        if (this.aiEnabled) {
            print("AI: Generated embedding for '" + item + "' -> [" + embedding[0].toString() + ", " + embedding[1].toString() + ", ...]")
        }
        
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
    
    # Busca semântica por similaridade
    intent findSimilar(query, maxResults) {
        if (not this.aiEnabled) {
            print("AI disabled - returning first items")
            var results = mf.collections.List()
            var limit = maxResults
            if (limit > this._size) {
                limit = this._size
            }
            for (var i: int = 0; i < limit; i = i + 1) {
                results.push(this.data[i])
            }
            return results
        }
        
        var queryEmbedding = this._generateEmbedding(query)
        var similarities = mf.collections.List()
        
        # Calcular similaridade com cada item
        for (var i: int = 0; i < this._size; i = i + 1) {
            var itemEmbedding = this.embeddings[i]
            var similarity = this._cosineSimilarity(queryEmbedding, itemEmbedding)
            
            var entry = mf.objects.Map()
            mf.objects.mapPut(entry, "item", this.data[i])
            mf.objects.mapPut(entry, "similarity", similarity)
            mf.objects.mapPut(entry, "index", i)
            similarities.push(entry)
        }
        
        # Retornar os mais similares (simulado - sem ordenação completa)
        var results = mf.collections.List()
        var found = 0
        var bestSim = 0.5
        
        for (var i: int = 0; i < this._size and found < maxResults; i = i + 1) {
            var entry = similarities[i]
            if (mf.objects.mapGet(entry, "similarity") > bestSim) {
                results.push(mf.objects.mapGet(entry, "item"))
                found = found + 1
            }
        }
        
        print("AI: Found " + found.toString() + " similar items to '" + query + "'")
        return results
    }
    
    # Similaridade cosseno simulada
    intent _cosineSimilarity(vec1, vec2) {
        var dotProduct = 0.0
        var norm1 = 0.0
        var norm2 = 0.0
        
        for (var i: int = 0; i < 5; i = i + 1) {
            var v1 = vec1[i]
            var v2 = vec2[i]
            dotProduct = dotProduct + (v1 * v2)
            norm1 = norm1 + (v1 * v1)
            norm2 = norm2 + (v2 * v2)
        }
        
        var denom = norm1 * norm2
        if (denom == 0) {
            return 0.0
        }
        
        return dotProduct / denom
    }
    
    intent enableAI(enabled: bool) {
        this.aiEnabled = enabled
        if (enabled) {
            print("AI embeddings enabled for EmbedList")
        } else {
            print("AI embeddings disabled for EmbedList")
        }
    }
    
    intent toString(): string {
        var result = "EmbedList<" + this.elementType + ">["
        for (var i: int = 0; i < this._size; i = i + 1) {
            if (i > 0) {
                result = result + ", "
            }
            var item = this.get(i)
            result = result + item
        }
        if (this.aiEnabled) {
            result = result + "] (AI: enabled)"
        } else {
            result = result + "] (AI: disabled)"
        }
        return result
    }
}