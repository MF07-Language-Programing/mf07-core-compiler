
var logger = new Logger(LogLevel.DEBUG, "SegmentTest")
var useCallback = fn(args: list<string>){
	for (var arg in args) {
		logger.info("Olá {arg}! {Math.pi()}")
	}
}


class SegmentTest {
	private var string name: Optional[string]
	private var int waitingTime: Optional[int]

	intent constructor(name: Optional[string] = "test_segment_or", waitingTime: Optional[int] = 1000) {
		if (name == null) {
			this.name = "test_segment"
		} else {
			this.name = name
		}
		if (waitingTime == null) {
			this.waitingTime = 1000
		} else {
			this.waitingTime = waitingTime
		}
	}

	intent test_filesystem(){
		logger.debug("=== TESTE: FileSystem & Path ===")

		var root = Path.join(Path.cwd(), "tests", "tmp_fs", null, null)
		var workdir = new Directory(root)
		logger.debug("Diretório temporário: {root}")

		if (not workdir.exists()) {
			var created = workdir.ensure()
			logger.debug("Criado diretório temporário: {created}")
		}

		var filePath = Path.join(root, "amostra.txt", null, null, null)
		var file = new File(filePath)
		logger.debug("Arquivo alvo: {filePath}")

		var wrote = file.writeText("Linha inicial", null)
		logger.debug("Escreveu texto inicial: {wrote}")

		var appended = file.appendText("\nSegunda linha", null)
		logger.debug("Append realizado: {appended}")

		var content = file.readText(null)
		logger.debug("Conteúdo atual:\n{content}")

		var info = file.info()
		if (info != null) {
			logger.debug("Tamanho do arquivo: {info.size}")
			logger.debug("É arquivo? {info.isFile()}")
			logger.debug("Última modificação: {info.modified}")
		}

		var copyPath = Path.join(root, "copia.txt", null, null, null)
		var copied = file.copyTo(copyPath, true)
		logger.debug("Cópia criada: {copied}")

		var movedPath = Path.join(root, "movido.txt", null, null, null)
		var moved = file.moveTo(movedPath, true)
		logger.debug("Movido com sucesso: {moved}")

		var listing = workdir.list(false)
		logger.debug("Itens no diretório: {listing.size()}")

		var i = 0
		while (i < listing.size()) {
			var entry = listing.get(i)
			logger.debug(" - {entry.name} ({entry.type})")
			i = i + 1
		}

		var globbed = FileSystem.glob(root, "*.txt")
		logger.debug("Resultado glob: {globbed.size()}")

		var walked = FileSystem.walk(root)
		logger.debug("Frames do walk: {walked.size()}")
		waitSeconds(5)  # Espera para garantir que o walk seja concluído

		var copyRemoved = FileSystem.remove(copyPath, false)
		logger.debug("Cópia removida: {copyRemoved}")

		var movedRemoved = FileSystem.remove(movedPath, false)
		logger.debug("Arquivo movido removido: {movedRemoved}")

		var cleaned = workdir.remove(true)
		logger.debug("Diretório temporário limpo: {cleaned}")

		logger.debug("=== FIM DO TESTE FileSystem ===")
	}

	intent test_http_requests(){
		logger.debug("=== TESTE: Requests & TCP ===")

		var client = new Requests("https://postman-echo.com", null)

		var params = mf.objects.Map()
		mf.objects.mapPut(params, "foo", "bar")

		var getResponse = client.get("/get", params, null, 20)
		if (getResponse.hasError()) {
			logger.debug("Falha GET:", getResponse.error())
		} else {
			logger.debug("GET data:", getResponse.json())
			logger.debug("GET status:", getResponse.status)
			logger.debug("GET ok?", getResponse.isSuccess())
			logger.debug("Header server:", getResponse.header("server"))
			var getJson = getResponse.json()
			if (getJson != null and mf.objects.mapHas(getJson, "args")) {
				var args = getJson["args"]
				logger.debug("Echo foo:", args["foo"])
			}
		}

		var postBody = {
			"name": "CorpLang",
			"feature": "requests"
		}

		var postResponse = client.post("/post", postBody, null, 20)
		if (postResponse.hasError()) {
			logger.debug("Falha POST:", postResponse.error())
		} else {
			var postJson = postResponse.json()
			if (postJson != null and mf.objects.mapHas(postJson, "json")) {
				var echoed = postJson["json"]
				logger.debug("POST echo name:", echoed["name"])
			}
		}

		var socket = client.openSocket("example.com", 80, 10)
		if (socket != null and socket.isOpen()) {
			logger.debug("Socket conectado:", socket.remoteHost, socket.remotePort)
			var requestLine = "HEAD / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"
			var sendResult = socket.send(requestLine, "utf-8")
			logger.debug("Bytes enviados:", sendResult.bytesSent)
			var receiveResult = socket.receive(2048, "utf-8")
			if (receiveResult.isOk()) {
				logger.debug("Resposta parcial:")
				logger.debug(receiveResult.text)
			} else {
				logger.debug("Erro ao receber:", receiveResult.error)
			}
			socket.close()
		} else {
			if (socket == null) {
				logger.debug("Não foi possível abrir socket: instancia nula")
			} else {
				logger.debug("Não foi possível abrir socket:", socket.lastError)
			}
		}

		logger.debug("=== FIM DO TESTE: Requests ===")
	}

	intent test_typing(){

	}

	intent test_collections() {
		var list: List<string> = new List()
		list.append("item1")
		list.append("item2")
		list.append("item3")
		logger.debug("Lista de itens:", list.toString())
	}

	intent test_loops(){
		var count: int = 0
		var items: List<string> = new List(["item1", "item2", "item3"])
		while (count < 3) {
			logger.info("Count is: {count}")
			count = count + 1
		}
		
		for (var item in items) {
			logger.info("Item: {item}")
		}
	}

	intent test_try_catch(){
		try {
			var x = 1 / 4
			logger.debug("Resultado da divisão({type(x)}): {x}")
		} catch (error) {
			logger.debug("Capture message: {error.message}")
			logger.debug("Cause by: {error.cause}")
			logger.debug("Object Type: error={type(error)} | trace={type(error.stackTrace)}")
		}
	}

	intent test_import(){
		import examples.first_project.models.schemas
		import examples.first_project.models.test
		import examples.first_project.models.demo_class_system
	}

	async intent run() {
		logger.warn("Running segment: {Optional.unwrap(this.name)}")
		this.test_filesystem()
		waitSeconds(1) # Simulating work
		# this.test_http_requests()
		waitSeconds(1) # Simulating work
		this.test_typing()
		waitSeconds(1) # Simulating work
		this.test_try_catch()
		waitSeconds(1) # Simulating work
		this.test_collections()
		waitSeconds(1) # Simulating work
		this.test_loops()
		waitSeconds(1) # Simulating work
		this.test_import()
		waitSeconds(3) # Simulating work
		logger.warn("Segment finished")
	}
}

class Base {
    var x: int = 0
    intent constructor(x: int) {
        this.x = x
    }
    intent getX() { return this.x }
}

class Derived extends Base {
    var y: int = 0
    intent constructor(x: int, y: int) {
        super(x)
        this.y = y
    }
    intent getY() { return this.y }
    intent getValue() { return this.getX() + this.getY() }
}

intent test() {
 	var rows: int = 3
    var cols: int = 4
    var matrix = new List()

    print(" Criando matriz com FOR TRADICIONAL:")
    for (var i: int = 0; i < rows; i = i + 1) {
        # var row = new List()
        
        # for (var j: int = 0; j < cols; j = j + 1) {
        #     var obj = new Derived((i + 1) * 10, (j + 1) * 5)
        #     row.append(obj)
        # }
        
        # matrix.append(row)
        print("  ✓ Linha ", (i + 1).toString(), " criada")
    }
}

intent debug(value: CorpLangFunction){
	var msg = value()
	print("DEBUG({type(value)}):", Object.keys(value))
	print("DEBUG RESULT:", msg)
}

async intent main() {
	var segment = new SegmentTest()
	var rows: int = 3
	try{
		for (var i: int = 0; i < 100; i = i + 1) {
			var test: Union[int, float] = Math.min(0, 100)
			if (test == 100) {
				throw new RuntimeException("Teste de erro lançado na iteração {i}-{test}, valor máximo atingido.")
			}
			var result = test % 2
			# print("Index {i} value={test.toString()}")
			if (result == 0) {
				print("Item {i} - E Par. calc={result} | random_value={test}")
			}
		}
	} catch (error) {
		logger.error("Error occurred: {error.message}")
	}
}

# await main():
useCallback(["Alice", "Bob", "Charlie"])
# debug(fn() {
# 	print("Executing debug function...")
# 	return "Hello from debug!"
# })
# debug("test string")