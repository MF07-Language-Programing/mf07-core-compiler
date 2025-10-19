# Debug - Verificar como type() funciona realmente

intent debug_types() {
    print("=== DEBUG TIPOS ===")
    
    var testStr = "hello"
    var testInt = 42  
    var testBool = true
    var testFloat = 3.14
    
    print("type('hello'):", type(testStr))
    print("type(42):", type(testInt))
    print("type(true):", type(testBool)) 
    print("type(3.14):", type(testFloat))
    
    # Testar comparações
    var strType = type(testStr)
    print("strType == 'str':", (strType == "str"))
    print("strType == 'string':", (strType == "string"))  
    print("strType == '<class 'str'>':", (strType "<class 'str'>"))
    
    print("=== FIM DEBUG ===")
}

debug_types()