

intent get(name) {
    print("Buscando dados do {name} em GET - https://example.com/auth/me")
    var data = {
        "nome": "Olá {name}",
        "data" : {
            "age": 16
        }
    }

    return data
}
