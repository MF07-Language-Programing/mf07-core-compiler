

# 🚀 TESTE COMPLETO DE SINTAXES CORPLANG v2.1.0 🚀

async intent main() {	
	print("=== TESTE DE SINTAXES MELHORADAS ===")
	
	# Variáveis tipadas com cores distintas
	var x: int = 4
	var y: int = 2
	var name: string = "CorpLang"
	var active: bool = true
	
	# Funções matemáticas (deve ter cor verde específica)
	var mod_result: int = Math.mod(x, y)
	var fib_result: int = Math.fibonacci(x)
	var fact_result: int = Math.factorial(x)
	var gcd_result: int = Math.gcd(x, y)
	var lcm_result: int = Math.lcm(x, y)

	print("Modulus of", x, "and", y, "is", mod_result)
	print("Fibonacci of", x, "is", fib_result)
	print("Factorial of", x, "is", fact_result)
	print("GCD of", x, "and", y, "is", gcd_result)
	print("LCM of", x, "and", y, "is", lcm_result)

	print("=" * 50)

	# Coleções genéricas com cores contrastantes
	var headers: Map<string, string> = new Map()
	var numbers: List<int> = new List()
	var users: HashMap<string, Employee> = new HashMap()
	var uniqueIds: Set<string> = new Set()
	
	# Métodos devem ter cores específicas (azul ciano)
	headers.put("Authorization", "Bearer YOUR_API_KEY")
	headers.put("Content-Type", "application/json")
	numbers.append(10)
	numbers.append(20)
	uniqueIds.add("user123")
	
	print("Headers size:", headers.size())
	print("Numbers length:", numbers.length())
	print("Is numbers empty?", numbers.isEmpty())

	# Classes personalizadas (deve ter cor laranja)
	var request = new Requests("https://viacep.com.br", headers)
	var options = new RequestOptions("/ws/PR/Curitiba/Rua%20/json/", "GET", 5000, 0, headers, Map.default(), {}, {}, true, true, "")
	
	# Métodos chamados devem ter destaque especial
	var response: dict = await request.execute(options)

	
	# Processamento de dados
	var data_dict = response["data"]
	var instance = new List(data_dict)
	
	# Loop tradicional
	for (var i: int = 0; i < instance.size(); i = i + 1) {
		var item = instance.get(i)
		print("Address", i, ":", item["logradouro"], "-", item["bairro"])
	}
	
	# Classe com interface
	interface Employee {
		intent getName(): string
		intent getSalary(): float
	}
	
	class Developer implements Employee {
		private var name: string
		private var salary: float
		
		intent constructor(name: string, salary: float) {
			this.name = name
			this.salary = salary
		}
		
		intent getName(): string {
			return this.name
		}
		
		intent getSalary(): float {
			return this.salary
		}
	}
	
	# Instanciação e uso
	var dev = new Developer("Lucas", 5500.50)
	print("Developer:", dev.getName(), "- Salary:", dev.getSalary())
	
	# Operações corporativas
	dataset load employees from "database.json"
	model train ml_model (dataset=employees, algorithm="decision_tree")
	var prediction = await model.predict(new_data)
	
	print("Status:", response["status"])
	print("=== TESTE DE SINTAXES CONCLUÍDO ===")
}

# Chamada principal
main()