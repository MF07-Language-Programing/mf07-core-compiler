# core/socket.mp
# Abstrações nativas para conexões TCP em CorpLang

class SocketHelpers {
    static intent field(raw, key: string) {
        if (raw == null) {
            return null
        }
        if (not mf.objects.mapHas(raw, key)) {
            return null
        }
        return raw[key]
    }

    static intent bool(raw, key: string, fallback: bool): bool {
        var value = SocketHelpers.field(raw, key)
        if (value == null) {
            return fallback
        }
        if (value == true) {
            return true
        }
        if (value == false) {
            return false
        }
        return fallback
    }

    static intent int(raw, key: string, fallback: int): int {
        var value = SocketHelpers.field(raw, key)
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent float(raw, key: string, fallback: float): float {
        var value = SocketHelpers.field(raw, key)
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent string(raw, key: string, fallback: string): string {
        var value = SocketHelpers.field(raw, key)
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent map(raw, key: string) {
        var value = SocketHelpers.field(raw, key)
        if (value == null) {
            return null
        }
        if (type(value) == "InstanceObject") {
            return value
        }
        var result = mf.objects.Map()
        var keys = mf.objects.keys(value)
        var i = 0
        while (i < len(keys)) {
            var name = keys[i]
            mf.objects.mapPut(result, name, value[name])
            i = i + 1
        }
        return result
    }

    static intent list(raw, key: string) {
        var value = SocketHelpers.field(raw, key)
        if (value == null) {
            return new List([])
        }
        return new List(value)
    }

    static intent copyMap(target, source) {
        if (source == null) {
            return
        }
        var raw = source
        if (type(source) == "InstanceObject") {
            raw = source.__raw__()
        }
        var keys = mf.objects.keys(raw)
        var i = 0
        while (i < len(keys)) {
            var key = keys[i]
            mf.objects.mapPut(target, key, raw[key])
            i = i + 1
        }
    }
}

class SocketStatus {
    var ok: bool
    var error: string
    var id: string

    intent constructor(raw) {
        if (raw == null) {
            raw = {}
        }
        this.ok = SocketHelpers.bool(raw, "ok", false)
        this.error = SocketHelpers.string(raw, "error", "")
        this.id = SocketHelpers.string(raw, "id", "")
    }

    intent isOk(): bool {
        return this.ok
    }

    intent throwIfError(message: string) {
        if (this.ok) {
            return
        }
        if (message == null or message == "") {
            message = this.error
        }
        throw new Error(message)
    }
}

class SocketSendResult extends SocketStatus {
    var bytesSent: int

    intent constructor(raw) {
        super(raw)
        this.bytesSent = SocketHelpers.int(raw, "bytes", 0)
    }
}

class SocketReceiveResult extends SocketStatus {
    var text: string
    var data
    var size: int
    var closed: bool

    intent constructor(raw) {
        super(raw)
        this.text = SocketHelpers.string(raw, "text", "")
        this.data = SocketHelpers.list(raw, "bytes")
        this.size = SocketHelpers.int(raw, "size", this.data.size())
        this.closed = SocketHelpers.bool(raw, "closed", false)
    }

    intent bytes() {
        return this.data
    }
}

class SocketInfo extends SocketStatus {
    var local
    var remote
    var timeout: float

    intent constructor(raw) {
        super(raw)
        var localRaw = SocketHelpers.map(raw, "local")
        if (localRaw == null) {
            this.local = mf.objects.Map()
        } else {
            this.local = localRaw
        }
        var remoteRaw = SocketHelpers.map(raw, "remote")
        if (remoteRaw == null) {
            this.remote = mf.objects.Map()
        } else {
            this.remote = remoteRaw
        }
        this.timeout = SocketHelpers.float(raw, "timeout", 0.0)
    }
}

class TcpConnection {
    var id: string
    var remoteHost: string
    var remotePort: int
    var localHost: string
    var localPort: int
    var timeout: float
    var open: bool
    var lastError: string

    intent constructor(raw) {
        this.id = ""
        this.remoteHost = ""
        this.remotePort = 0
        this.localHost = ""
        this.localPort = 0
        this.timeout = 0.0
        this.open = false
        this.lastError = ""
        this._apply(raw)
    }

    static intent connect(host: string, port: int, timeout) {
        var raw = mf.connections.tcp_connect(host, port, timeout)
        var connection = new TcpConnection(raw)
        connection.applyDefaults(host, port)
        return connection
    }

    intent applyDefaults(host: string, port: int) {
        if (host != null and host != "" and this.remoteHost == "") {
            this.remoteHost = host
        }
        if (port != null and port > 0 and this.remotePort == 0) {
            this.remotePort = port
        }
    }

    intent _apply(raw) {
        if (raw == null) {
            this.lastError = "Invalid socket response"
            return
        }
        if (SocketHelpers.bool(raw, "ok", false)) {
            this.open = true
            this.id = SocketHelpers.string(raw, "id", "")
            var remote = SocketHelpers.map(raw, "remote")
            if (remote != null) {
                var remoteRaw = remote
                if (type(remoteRaw) == "InstanceObject") {
                    remoteRaw = remoteRaw.__raw__()
                }
                this.remoteHost = SocketHelpers.string(remoteRaw, "host", this.remoteHost)
                this.remotePort = SocketHelpers.int(remoteRaw, "port", this.remotePort)
            }
            var local = SocketHelpers.map(raw, "local")
            if (local != null) {
                var localRaw = local
                if (type(localRaw) == "InstanceObject") {
                    localRaw = localRaw.__raw__()
                }
                this.localHost = SocketHelpers.string(localRaw, "host", this.localHost)
                this.localPort = SocketHelpers.int(localRaw, "port", this.localPort)
            }
            this.timeout = SocketHelpers.float(raw, "timeout", this.timeout)
        } else {
            this.open = false
            this.lastError = SocketHelpers.string(raw, "error", this.lastError)
        }
    }

    intent isOpen(): bool {
        return this.open
    }

    intent ensureOpen() {
        if (not this.open) {
            var message = "Socket connection is closed"
            if (this.lastError != "") {
                message = message + ": " + this.lastError
            }
            throw new Error(message)
        }
    }

    intent send(data, encoding: string) {
        this.ensureOpen()
        var result = new SocketSendResult(mf.connections.tcp_send(this.id, data, encoding))
        if (not result.isOk()) {
            this.lastError = result.error
        }
        return result
    }

    intent receive(size: int, encoding: string) {
        this.ensureOpen()
        var result = new SocketReceiveResult(mf.connections.tcp_receive(this.id, size, encoding))
        if (not result.isOk()) {
            this.lastError = result.error
            if (result.closed) {
                this.open = false
            }
        }
        return result
    }

    intent setTimeout(seconds) {
        this.ensureOpen()
        var response = new SocketStatus(mf.connections.set_timeout(this.id, seconds))
        if (response.isOk()) {
            if (seconds != null and seconds > 0) {
                this.timeout = seconds
            }
        } else {
            this.lastError = response.error
        }
        return response
    }

    intent info() {
        this.ensureOpen()
        return new SocketInfo(mf.connections.connection_info(this.id))
    }

    intent shutdown(mode: string) {
        this.ensureOpen()
        var response = new SocketStatus(mf.connections.tcp_shutdown(this.id, mode))
        if (not response.isOk()) {
            this.lastError = response.error
        }
        return response
    }

    intent close(): bool {
        if (not this.open) {
            return true
        }
        var response = new SocketStatus(mf.connections.tcp_close(this.id))
        if (response.isOk()) {
            this.open = false
        } else {
            this.lastError = response.error
        }
        return response.isOk()
    }
}

class TcpAcceptResult extends SocketStatus {
    var connection: TcpConnection

    intent constructor(raw) {
        super(raw)
        if (this.ok) {
            this.connection = new TcpConnection(raw)
        } else {
            this.connection = null
        }
    }
}

class TcpServer {
    var id: string
    var localHost: string
    var localPort: int
    var backlog: int
    var timeout: float
    var listening: bool
    var lastError: string

    intent constructor(raw) {
        this.id = ""
        this.localHost = ""
        this.localPort = 0
        this.backlog = 0
        this.timeout = 0.0
        this.listening = false
        this.lastError = ""
        this._apply(raw)
    }

    static intent listen(host: string, port: int, backlog: int, timeout) {
        var raw = mf.connections.tcp_listen(host, port, backlog, true, timeout)
        return new TcpServer(raw)
    }

    intent _apply(raw) {
        if (raw == null) {
            this.listening = false
            this.lastError = "Invalid listen response"
            return
        }
        if (SocketHelpers.bool(raw, "ok", false)) {
            this.listening = true
            this.id = SocketHelpers.string(raw, "id", "")
            var local = SocketHelpers.map(raw, "local")
            if (local != null) {
                var localRaw = local
                if (type(localRaw) == "InstanceObject") {
                    localRaw = localRaw.__raw__()
                }
                this.localHost = SocketHelpers.string(localRaw, "host", "")
                this.localPort = SocketHelpers.int(localRaw, "port", 0)
            }
            this.backlog = SocketHelpers.int(raw, "backlog", 0)
            this.timeout = SocketHelpers.float(raw, "timeout", 0.0)
        } else {
            this.listening = false
            this.lastError = SocketHelpers.string(raw, "error", "")
        }
    }

    intent isListening(): bool {
        return this.listening
    }

    intent accept(timeout) {
        if (not this.listening) {
            throw new Error("Server is not listening")
        }
        var result = new TcpAcceptResult(mf.connections.tcp_accept(this.id, timeout))
        if (not result.isOk()) {
            this.lastError = result.error
        }
        return result
    }

    intent close(): bool {
        if (not this.listening) {
            return true
        }
        var response = new SocketStatus(mf.connections.tcp_close(this.id))
        if (response.isOk()) {
            this.listening = false
        } else {
            this.lastError = response.error
        }
        return response.isOk()
    }
}
