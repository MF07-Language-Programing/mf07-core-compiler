

var person_obj = {
    "name": "Lucas"
}




intent love(person){
    intent helloword(){
        intent endpoint(person){
            print("--------------------")
            print("endpoint intent | {person}")
            print("--------------------")
        }

        print("Hello world!")
        return endpoint
    }


    print("Eu amo {person}")
    var result = helloword()
    var obj = type(result)
    print("type: {obj}")
    # endpoint()
    result(person)
}


love(person_obj)