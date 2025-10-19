# Demo MF script demonstrating import and async/await

# Import a module placed under tests/imported/mod.mp using dotted path
import tests.imported.requests;

# Use intent from imported module
print("Chamando requests:")
var response = get("Lucas");
print("response:", response);

# Define an async intent
async intent add_async(a: int, b: int) {
    waitSeconds(1)
    return a + b;
}

# Call async intent and await
print("Executando...")
var sum_result = await add_async("1", 7);
print("ASYNC_SUM:", sum_result);


intent g(): int {
    return "LuH"
}

var a: int = g()
type = type(a)
print("value: {a}")
print("test: {type}")
