# core/optional.mp
# Utilitários para trabalhar com valores opcionais.

class Optional {
    static intent isSome(value): bool {
        return value != null
    }

    static intent isNone(value): bool {
        return value == null
    }

    static intent unwrap(value) {
        if (value == null) {
            throw new Error("Cannot unwrap a null Optional value")
        }
        return value
    }

    static intent unwrapOr(value, defaultValue) {
        if (value == null) {
            return defaultValue
        }
        return value
    }

    static intent map(value, func) {
        if (value == null) {
            return null
        }
        return func(value)
    }
}
