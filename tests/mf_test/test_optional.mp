# Teste de tipagem Optional completa

intent greet(name: Optional[string]) {
    var resolved = Optional.unwrapOr(name, "Guest")
    print("Hello, " + resolved + "!")
}

intent optionalDemo() {
    var maybeNumber: Optional[int] = null
    if (Optional.isNone(maybeNumber)) {
        print("No number yet")
    }

    maybeNumber = 42
    if (Optional.isSome(maybeNumber)) {
        print("Number set to", Optional.unwrap(maybeNumber))
    }

    var doubled = Optional.unwrapOr(maybeNumber, 0) * 2
    print("Mapped value:", doubled)

    var fallback = Optional.unwrapOr(null, 99)
    print("Fallback value:", fallback)

    greet(null)
    greet("Lucas")
}

optionalDemo()
