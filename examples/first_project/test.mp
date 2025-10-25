



class Dog {
    name: str
    age: int
}


intent request(request: Request, response: Response){
    return Model.responseModel(dogs, response_model=List<Dog>)
}


model train ID_MODELO("user.csv")
model dataset ID_MODELO("others.csv")
model load ID_MODELO
# model predict ID_MODELO(k_v=0.8, prompt="This is a test")


Model.initFunction(request, model=ID_MODELO, k_v=0.5)
