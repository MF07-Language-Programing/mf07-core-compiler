print("=== TESTE: Exceptions ===")

class CustomError extends Exception {
    intent constructor(message: string) {
        super(message, null)
    }
}

intent mightFail(code: int) {
    if (code == 0) {
        throw new Exception("Divisão por zero simulada", null)
    }
    if (code == 1) {
        throw new CustomError("Falha customizada", null)
    }
    if (code == 2) {
        throw "Erro bruto"
    }
    return "ok"
}

var i = 0
while (i < 3) {
    try {
        var result = mightFail(i)
        print("Resultado:", result)
    } catch (CustomError err) {
        print("Catch CustomError:", err.getMessage())
        var trace = exceptionStackTrace(err)
        print("Frames custom:", len(trace))
    } catch (Exception err) {
        print("Catch Exception:", err.getMessage())
        err.printStackTrace()
    } catch (erroGenerico) {
        print("Catch Fallback:", erroGenerico)
        var fallbackTrace = exceptionStackTrace(erroGenerico)
        print("Frames fallback:", len(fallbackTrace))
    } finally {
        print("Finally executado para", i)
    }
    i = i + 1
}

try {
    try {
        throw new Exception("Erro com rethrow", null)
    } catch (Exception interno) {
        print("Catch interno:", interno.getMessage())
        throw
    }
} catch (Exception externo) {
    print("Catch externo após rethrow:", externo.getMessage())
    var outerTrace = exceptionStackTrace(externo)
    print("Frames rethrow:", len(outerTrace))
}

print("=== FIM DO TESTE ===")
