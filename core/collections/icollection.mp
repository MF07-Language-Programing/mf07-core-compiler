# core/collections/icollection.mp
# Interface base para todas as coleções do sistema MF07

interface ICollection<T> {
    # Métodos básicos obrigatórios
    intent size() -> int
    intent isEmpty() -> bool  
    intent clear()
    intent contains(value: T) -> bool
    intent toArray() -> Array<T>
    
    # Métodos de iteração
    intent get(index: int) -> T
    intent length() -> int
}

interface IComparable<T> {
    intent compareTo(other: T) -> int
    intent equals(other: T) -> bool
    intent hashCode() -> int
}

interface IIterable<T> {
    intent iterator() -> Iterator<T>
}

# Interface para embeddings e IA
interface IEmbeddable<T> {
    intent embed(item: T) -> Vector<float>
    intent findSimilar(item: T, threshold: float = 0.8) -> List<T>
    intent updateEmbedding(index: int, item: T)
    intent getEmbedding(index: int) -> Vector<float>
}

# Classe base abstrata para todas as coleções
abstract class BaseCollection<T> implements ICollection<T> {
    protected var elementType: string
    protected var aiEnabled: bool = false
    
    intent constructor(elementType: string) {
        this.elementType = elementType
    }
    
    # Implementação padrão para isEmpty
    intent isEmpty() -> bool {
        return this.size() == 0
    }
    
    # Validação de tipos
    protected intent validateType(item: T) -> bool {
        # TODO: Implementar validação em runtime
        return true
    }
    
    # Suporte a IA
    intent enableAI() {
        this.aiEnabled = true
    }
    
    intent isAIEnabled() -> bool {
        return this.aiEnabled
    }
}