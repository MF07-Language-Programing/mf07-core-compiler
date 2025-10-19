# Testes de alto nível para Requests e conexões TCP

intent test_requests_module() {
	print("=== TESTE: Requests & TCP ===")

	var client = new Requests("https://postman-echo.com", null)

	var params = mf.objects.Map()
	mf.objects.mapPut(params, "foo", "bar")

	var getResponse = client.get("/get", params, null, 20)
	if (getResponse.hasError()) {
		print("Falha GET:", getResponse.error())
	} else {
		print("GET data:", getResponse.json())
		print("GET status:", getResponse.status)
		print("GET ok?", getResponse.isSuccess())
		print("Header server:", getResponse.header("server"))
		var getJson = getResponse.json()
		if (getJson != null and mf.objects.mapHas(getJson, "args")) {
			var args = getJson["args"]
			print("Echo foo:", args["foo"])
		}
	}

	var postBody = {
		"name": "CorpLang",
		"feature": "requests"
	}

	var postResponse = client.post("/post", postBody, null, 20)
	if (postResponse.hasError()) {
		print("Falha POST:", postResponse.error())
	} else {
		var postJson = postResponse.json()
		if (postJson != null and mf.objects.mapHas(postJson, "json")) {
			var echoed = postJson["json"]
			print("POST echo name:", echoed["name"])
		}
	}

	var socket = client.openSocket("example.com", 80, 10)
	if (socket != null and socket.isOpen()) {
		print("Socket conectado:", socket.remoteHost, socket.remotePort)
		var requestLine = "HEAD / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"
		var sendResult = socket.send(requestLine, "utf-8")
		print("Bytes enviados:", sendResult.bytesSent)
		var receiveResult = socket.receive(2048, "utf-8")
		if (receiveResult.isOk()) {
			print("Resposta parcial:")
			print(receiveResult.text)
		} else {
			print("Erro ao receber:", receiveResult.error)
		}
		socket.close()
	} else {
		if (socket == null) {
			print("Não foi possível abrir socket: instancia nula")
		} else {
			print("Não foi possível abrir socket:", socket.lastError)
		}
	}

	print("=== FIM DO TESTE ===")
}

test_requests_module()
