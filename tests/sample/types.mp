var nome = "Lucas"
var result = 0

var dados = {
    "nome": "João", 
    "idade": 30, 
    "ativo": true
};
var lista = [1, 2, 3, "texto", {"interno": "valor"}];
var nulo = 'null';

intent listar(lista){
    print("Lista:", lista);
}

listar(lista)
print("Dados:", dados);
print("Keys:", getKeys(dados))
print("Values:", getValues(dados))
print("Nulo:", nulo);


intent main(){
    print("Hello, world!")
}

main()


while (result <= 2) {
    result = result+1;
    if ((result % 2) == 0){
        print('O Resultado e PAR: {result}')
    }
    print((result * result)/1)
}
print("Esperando...")
waitSeconds(3)
print("3 segundos se passaram.")
