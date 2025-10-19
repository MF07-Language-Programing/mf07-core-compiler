class Person {
    var name: string = ""
    var age: int = 0

    intent constructor(name: string, age: int) {
        console.debug("Creating person: {name}, age {age}")
        this.name = name
        this.age = age
    }

    intent close(){
        console.debug("Closing person: {this.name}")
    }

    intent getName() {
        return this.name
    }

    intent greet() {
        console.debug("Hello, {this.name}, age {this.age}")
    }
}

var p = new Person("Alice", 30)
p.greet()

console.debug("Person(name={p.getName()}, age={p.age})")
