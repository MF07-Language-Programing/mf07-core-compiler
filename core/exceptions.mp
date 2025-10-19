class Exception {
    var message: string
    var cause
    var stackTrace

    intent constructor(message: string, cause) {
        if (message == null) {
            message = ""
        }
        this.message = message
        this.cause = cause
        this.stackTrace = new List([])
    }

    intent getMessage(): string {
        return this.message
    }

    intent getCause() {
        return this.cause
    }

    intent _attachStackTrace(frames) {
        if (frames == null) {
            this.stackTrace = new List([])
            return
        }
        if (type(frames) == "InstanceObject") {
            this.stackTrace = frames
            return
        }
        this.stackTrace = new List(frames)
    }

    intent stackTraceList() {
        if (this.stackTrace == null) {
            this.stackTrace = new List([])
        }
        return this.stackTrace
    }

    intent stackTraceToString(): string {
        var trace = this.stackTraceList()
        if (len(trace) == 0) {
            return ""
        }
        var buffer = ""
        var i = 0
        while (i < len(trace)) {
            var frame = trace[i]
            if (type(frame) == "InstanceObject") {
                frame = frame.__raw__()
            }
            var functionName = "<unknown>"
            if (mf.objects.mapHas(frame, "function")) {
                var maybeFn = frame["function"]
                if (maybeFn != null and maybeFn != "") {
                    functionName = maybeFn
                }
            }
            var file = ""
            if (mf.objects.mapHas(frame, "file") and frame["file"] != null) {
                file = frame["file"]
            }
            var lineInfo = ""
            if (mf.objects.mapHas(frame, "line") and frame["line"] != null) {
                lineInfo = frame["line"].toString()
            }
            var entry = functionName
            if (file != "") {
                entry = entry + " (" + file
                if (lineInfo != "") {
                    entry = entry + ":" + lineInfo
                }
                entry = entry + ")"
            }
            if (buffer != "") {
                buffer = buffer + "\n"
            }
            buffer = buffer + entry
            i = i + 1
        }
        return buffer
    }

    intent toString(): string {
        var msg = this.getMessage()
        if (msg == null or msg == "") {
            return "Exception"
        }
        return msg
    }

    intent printStackTrace() {
        var trace = this.stackTraceList()
        if (len(trace) == 0) {
            print("Stack trace not available.")
            return
        }
        print("Stack trace:")
        var i = 0
        while (i < len(trace)) {
            var frame = trace[i]
            if (type(frame) == "InstanceObject") {
                frame = frame.__raw__()
            }
            var functionName = "<unknown>"
            if (mf.objects.mapHas(frame, "function")) {
                var maybeFn = frame["function"]
                if (maybeFn != null and maybeFn != "") {
                    functionName = maybeFn
                }
            }
            var file = ""
            if (mf.objects.mapHas(frame, "file") and frame["file"] != null) {
                file = frame["file"]
            }
            var lineInfo = ""
            if (mf.objects.mapHas(frame, "line") and frame["line"] != null) {
                lineInfo = frame["line"].toString()
            }
            var columnInfo = ""
            if (mf.objects.mapHas(frame, "column") and frame["column"] != null) {
                columnInfo = frame["column"].toString()
            }
            var entry = "  at " + functionName
            if (file != "") {
                entry = entry + " (" + file
                if (lineInfo != "") {
                    entry = entry + ":" + lineInfo
                    if (columnInfo != "") {
                        entry = entry + ":" + columnInfo
                    }
                }
                entry = entry + ")"
            }
            print(entry)
            i = i + 1
        }
    }
}

class RuntimeException extends Exception {
    intent constructor(message: string, cause) {
        super(message, cause)
    }
}
