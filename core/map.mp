# core/map.mp

# HashMap genérico com tipagem rigorosa Map<K,V>
class Map<K, V> {
    private var data
    private var keyType: string
    private var valueType: string
    private var _size: int = 0
    
    intent constructor(keyType, valueType) {
        this.data = mf.objects.Map()
        if (keyType == null) {
            this.keyType = "any"
        } else {
            this.keyType = keyType
        }
        if (valueType == null) {
            this.valueType = "any"  
        } else {
            this.valueType = valueType
        }
        this._size = 0
    }

    static intent fromDict(d: dict, keyType: string, valueType: string) {
        var m = new Map(keyType, valueType)
        var keys = mf.objects.keys(d)
        var i = 0
        while (i < len(keys)) {
            var k = keys[i]
            var v = d[k]
            m.put(k, v)
            i = i + 1
        }
        return m
    }

    static intent default() {
        return new Map(null, null)
    }
    
    # Validação rigorosa de tipos
    intent _validateKeyType(key) {
        if (this.keyType == "any") {
            return true
        }
        
        var keyActualType = ""
        if (key == null) {
            keyActualType = "null"
        } else {
            keyActualType = type(key)
        }
        
        # Suporte a str/string
        var expectedKey = this.keyType
        if (expectedKey == "string") {
            expectedKey = "str"
        }
        if (keyActualType == "string") {
            keyActualType = "str"
        }
        
        if (keyActualType != expectedKey) {
            print("TypeError: Expected key type " + this.keyType + " but got " + keyActualType)
            return false
        }
        return true
    }
    
    intent _validateValueType(value) {
        if (this.valueType == "any") {
            return true
        }
        
        var valueActualType = ""
        if (value == null) {
            valueActualType = "null"
        } else {
            valueActualType = type(value)
        }
        
        # Suporte a str/string
        var expectedValue = this.valueType
        if (expectedValue == "string") {
            expectedValue = "str"
        }
        if (valueActualType == "string") {
            valueActualType = "str"
        }
        
        if (valueActualType != expectedValue) {
            print("TypeError: Expected value type " + this.valueType + " but got " + valueActualType)
            return false
        }
        return true
    }
    
    intent put(key, value) {
        if (not this._validateKeyType(key)) {
            print("TypeError: Cannot put key " + type(key) + " in Map<" + this.keyType + "," + this.valueType + ">")
            return false
        }
        if (not this._validateValueType(value)) {
            print("TypeError: Cannot put value " + type(value) + " in Map<" + this.keyType + "," + this.valueType + ">")
            return false
        }
        
        var hadKey = mf.objects.mapHas(this.data, key)
        mf.objects.mapPut(this.data, key, value)
        if (not hadKey) {
            this._size = this._size + 1
        }
        return true
    }
    
    intent get(key) {
        return mf.objects.mapGet(this.data, key)
    }
    
    intent has(key): boolean {
        return mf.objects.mapHas(this.data, key)
    }
    
    intent remove(key): boolean {
        return mf.objects.mapRemove(this.data, key)
    }
    
    intent clear() {
        this.data = mf.objects.Map()
    }
    
    intent size(): int {
        return len(mf.objects.keys(this.data))
    }
    
    intent keys(): List {
        var result = new List("any")
        var keyArray = mf.objects.keys(this.data)
        var i = 0
        while (i < len(keyArray)) {
            result.append(keyArray[i])
            i = i + 1
        }
        return result
    }
    
    intent values(): List {
        var result = new List("any")
        var valueArray = mf.objects.values(this.data)
        var i = 0
        while (i < len(valueArray)) {
            result.append(valueArray[i])
            i = i + 1
        }
        return result
    }
    
    intent entries(): List {
        var result = new List("any")
        var entryArray = mf.objects.entries(this.data)
        var i = 0
        while (i < len(entryArray)) {
            result.append(entryArray[i])
            i = i + 1
        }
        return result
    }
    
    intent forEach(callback) {
        var keyArray = mf.objects.keys(this.data)
        var i = 0
        while (i < len(keyArray)) {
            var key = keyArray[i]
            var value = this.get(key)
            callback(key, value)
            i = i + 1
        }
    }

    intent __raw__() {
        return this.data
    }
    
    intent toString(): string {
        var s = "{"
        var keyArray = mf.objects.keys(this.data)
        var i = 0
        while (i < len(keyArray)) {
            var key = keyArray[i]
            var value = this.get(key)
            
            # Format key
            var keyStr = "{key}"
            if (type(key) == "string") {
                keyStr = "\"" + key + "\""
            }
            
            # Format value
            var valueStr = "{value}"
            if (type(value) == "string") {
                valueStr = "\"" + value + "\""
            }
            
            s = s + keyStr + ": " + valueStr
            
            if (i < len(keyArray) - 1) {
                s = s + ", "
            }
            i = i + 1
        }
        s = s + "}"
        return s
    }
}