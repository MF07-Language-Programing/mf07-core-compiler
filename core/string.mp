# core/string.mp

class StringHelpers {
    static intent toUpper(s: string): string {
        print("[DEBUGGER] StringHelpers.toUpper called with string:", s)
        if (s == null) {
            return ""
        }
        # Usar função built-in do MF07 para converter para maiúsculo
        return mf.utils.upper(s)
    }

    static intent toLower(s: string): string {
        if (s == null) {
            return ""
        }
        return mf.utils.lower(s)
    }

    static intent trim(s: string): string {
        if (s == null) {
            return ""
        }
        return mf.utils.strip(s)
    }

    # Funções de verificação de strings

    static intent isEmpty(s: string): bool {
        if (s == null) {
            return true
        }
        return s == ""
    }

    static intent isNotEmpty(s: string): bool {
        return !StringHelpers.isEmpty(s)
    }

    static intent isBlank(s: string): bool {
        if (s == null) {
            return true
        }
        return mf.utils.strip(s) == ""
    }

    static intent isNotBlank(s: string): bool {
        return !StringHelpers.isBlank(s)
    }

    static intent equalsIgnoreCase(a: string, b: string): bool {
        if (a == null and b == null) {
            return true
        }
        if (a == null or b == null) {
            return false
        }
        return mf.utils.upper(a) == mf.utils.upper(b)
    }
}
