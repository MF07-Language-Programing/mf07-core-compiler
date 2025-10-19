# core/objects.mp

class Object {
    static intent keys(obj: any): any {
        # Use runtime mf.objects.keys implementation
        return mf.objects.keys(obj)
    }

    static intent values(obj: any): any {
        # Use runtime mf.objects.values implementation  
        return mf.objects.values(obj)
    }

    static intent entries(obj: any): any {
        # Use runtime mf.objects.entries implementation
        return mf.objects.entries(obj)
    }

    static intent clone(obj: any): any {
        # Use runtime mf.objects.clone implementation
        return mf.objects.clone(obj)
    }
}
