# core/utils.mp

class Utils {
    static intent isNull(v: any): bool {
        return v == null
    }

    static intent isInstanceOf(v: any, type: string): bool {
        return v != null and typeOf(v) == type
    }

    static intent typeOf(v: any): string {
        return type(v)
    }
}
