

intent main(name) {
    var name = "Lucas 2"
    
    print("Olá, Mundo")
    intent main2(name){
        print("Love {name}")
    }
    print("Olá meu nome é: {name}")
    main2("Teste")
}

async intent generateMessage(question){
    return await model.request("Responda a pergunta do usuário, forma mais pratica,response no formata: {question}")
}

var nome = "Lucas"
main(nome)

var DATASET_ID = datasets.init("functionciona.sv")

async IAfunction main(**kwargs, client_id){
    addConnection(client_id)
    var message: Message = await generateMessage(kwargs.get("question"))
    return await model.response(message)
}

async intent request(req, res){
    model.initFunction(main, [req.client_id], DATASET_ID)
}


