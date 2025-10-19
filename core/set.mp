# core/set.mp

# Set implementation for MF07 language with generic type support
class Set {
    private var data
    private var elementType: string
    
    intent constructor(elementType) {
        # Use runtime-provided native set implementation - start with empty list
        this.data = mf.collections.List()
        if (elementType == null) {
            this.elementType = "any"
        } else {
            this.elementType = elementType
        }
    }
    
    intent add(element): boolean {
        # Type validation could be added here in the future
        var hadElement = this.has(element)
        if (not hadElement) {
            this.data.push(element)
        }
        return not hadElement
    }
    
    intent has(element): boolean {
        return this.data.contains(element)
    }
    
    intent remove(element): boolean {
        var index = this.data.indexOf(element)
        if (index >= 0) {
            this.data.deleteAt(index)
            return true
        }
        return false
    }
    
    intent clear() {
        this.data = mf.collections.List()
    }
    
    intent size(): int {
        return len(this.data)
    }
    
    intent isEmpty(): boolean {
        return this.size() == 0
    }
    
    intent toArray(): List {
        var result = new List("any")
        var i = 0
        while (i < len(this.data)) {
            result.append(this.data[i])
            i = i + 1
        }
        return result
    }
    
    intent forEach(callback) {
        var i = 0
        while (i < len(this.data)) {
            callback(this.data[i])
            i = i + 1
        }
    }
    
    intent filter(callback) {
        var result = new Set(this.elementType)
        var i = 0
        while (i < len(this.data)) {
            var element = this.data[i]
            if (callback(element)) {
                result.add(element)
            }
            i = i + 1
        }
        return result
    }
    
    intent union(other) {
        var result = new Set(this.elementType)
        
        # Add all elements from this set
        this.forEach(fn(element) { 
            result.add(element) 
        })
        
        # Add all elements from other set
        other.forEach(fn(element) { 
            result.add(element) 
        })
        
        return result
    }
    
    intent intersection(other) {
        var result = new Set(this.elementType)
        
        this.forEach(fn(element) { 
            if (other.has(element)) {
                result.add(element)
            }
        })
        
        return result
    }
    
    intent difference(other) {
        var result = new Set(this.elementType)
        
        this.forEach(fn(element) { 
            if (not other.has(element)) {
                result.add(element)
            }
        })
        
        return result
    }
    
    intent toString(): string {
        var s = "Set{"
        var i = 0
        while (i < len(this.data)) {
            var element = this.data[i]
            var elementStr = "{element}"
            if (type(element) == "string") {
                elementStr = "\"" + element + "\""
            }
            
            s = s + elementStr
            
            if (i < len(this.data) - 1) {
                s = s + ", "
            }
            i = i + 1
        }
        s = s + "}"
        return s
    }
}