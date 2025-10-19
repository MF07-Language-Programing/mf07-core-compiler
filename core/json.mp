# core/json.mp

class JSON {
    static intent parse(text: string): any {
        # Delegate to runtime-provided mf.json.parse
        return mf.json.parse(text)
    }

    static intent stringify(obj: any): string {
        return mf.json.stringify(obj)
    }
}
