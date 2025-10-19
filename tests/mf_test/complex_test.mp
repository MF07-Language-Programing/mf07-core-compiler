
var logger = new Logger(LogLevel.DEBUG, "first_project")

async intent main() {
	var x: int = 4
	var y: int = 2
	var mod_result: int = Math.mod(x, y)
	var fib_result: int = Math.fibonacci(x)
	var fact_result: int = Math.factorial(x)
	var gcd_result: int = Math.gcd(x, y)
	var lcm_result: int = Math.lcm(x, y)

	sout("Modulus of", x, "and", y, "is", mod_result)
	sout("Fibonacci of", x, "is", fib_result)
	sout("Factorial of", x, "is", fact_result)
	sout("GCD of", x, "and", y, "is", gcd_result)
	sout("LCM of", x, "and", y, "is", lcm_result)

	sout("=-"*30)
	var result = await main_with("Lucas")
	print(type(logger))
	logger.info("Welcome to the program!")
	logger.info("First result of type {type(result)}: {result}")
	print("-"*60)
	test_typing(15)
}


async intent main_with(name: Optional[string] )  {	
	if (name == null) {
		print("Name is null, exiting function.")
		throw new Exception("Name cannot be null", null)
	}
	var x: int = 4
	if (x < 0) {
		print("x is negative, exiting function.")
		return false
	}

	sout("+-"*x)
	sout("Hello, {name}!")
	return true
}


intent test_typing(name: Optional[Union[string, int]] ): bool  {
    if (name != null and type(name) != "string" and type(name) != "int") 
        throw new Exception("Invalid type for name", null)
	if (name == null) {
		print("Name is null, exiting function.")
		throw new Exception("Name cannot be null", null)
	}

	if (type(name) != "string") {
		print("Name is not a string, exiting function.")
		throw new Exception("Name must be a string", null)
	}

	return true
}

try{
	await main()
} catch (error) {
	print("Error occurred:", error.message)
}
