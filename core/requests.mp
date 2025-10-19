
class RequestOptions {
    var uri: string
    var path: string
    var method: string
    var timeout: float
    var retries: int
    var headers
    var params
    var data
    var jsonData
    var textData: string
    var binaryData
    var auth
    var ssl_verify: bool
    var follow_redirects: bool
    var proxy
    var stream: bool

    intent constructor(path: string, method: string) {
        this.path = path
        this.method = method
        this.timeout = 30.0
        this.retries = 3
        this.headers = RequestOptions._emptyMap()
        this.params = RequestOptions._emptyMap()
        this.data = {}
        this.jsonData = null
        this.textData = null
        this.binaryData = null
        this.auth = {}
        this.ssl_verify = true
        this.follow_redirects = true
        this.proxy = null
        this.stream = false
        this.uri = ""
    }

    static intent _emptyMap() {
        return mf.objects.Map()
    }

    static intent _cloneMap(source) {
        var result = mf.objects.Map()
        if (source == null) {
            return result
        }
        var raw = source
        if (type(source) == "InstanceObject") {
            raw = source.__raw__()
        }
        var keys = mf.objects.keys(raw)
        var i = 0
        while (i < len(keys)) {
            var key = keys[i]
            mf.objects.mapPut(result, key, raw[key])
            i = i + 1
        }
        return result
    }

    intent setURI(uri: string) {
        this.uri = uri
    }

    intent useTimeout(seconds) {
        if (seconds != null and seconds > 0) {
            this.timeout = seconds
        }
        return this
    }

    intent useRetries(count) {
        if (count == null) {
            return this
        }
        if (count < 0) {
            count = 0
        }
        this.retries = count
        return this
    }

    intent setJson(payload) {
        this.jsonData = payload
        return this
    }

    intent setText(payload: string) {
        this.textData = payload
        return this
    }

    intent setBinary(payload) {
        this.binaryData = payload
        return this
    }

    intent setData(payload) {
        this.data = payload
        return this
    }

    intent setParams(values) {
        this.params = RequestOptions._cloneMap(values)
        return this
    }

    intent setHeaders(values) {
        this.headers = RequestOptions._cloneMap(values)
        return this
    }

    intent setAuth(values) {
        if (values == null) {
            this.auth = {}
        } else {
            this.auth = values
        }
        return this
    }

    intent setProxy(value) {
        this.proxy = value
        return this
    }

    intent setFollowRedirects(value: bool) {
        if (value == null) {
            return this
        }
        this.follow_redirects = value
        return this
    }

    intent setVerifySSL(value: bool) {
        if (value == null) {
            return this
        }
        this.ssl_verify = value
        return this
    }

    intent setStream(value: bool) {
        if (value == null) {
            return this
        }
        this.stream = value
        return this
    }

    intent header(key: string, value: string) {
        if (key == null) {
            return this
        }
        if (value == null) {
            value = ""
        }
        mf.objects.mapPut(this.headers, key, value)
        return this
    }

    intent param(key: string, value: string) {
        if (key == null) {
            return this
        }
        if (value == null) {
            value = ""
        }
        mf.objects.mapPut(this.params, key, value)
        return this
    }

    intent dictionary() {
        return {
            "uri": this.uri,
            "path": this.path,
            "method": this.method,
            "follow_redirects": this.follow_redirects,
            "timeout": this.timeout,
            "retries": this.retries,
            "headers": this.headers,
            "params": this.params,
            "data": this.data,
            "json": this.jsonData,
            "text": this.textData,
            "binary": this.binaryData,
            "auth": this.auth,
            "ssl_verify": this.ssl_verify,
            "proxy": this.proxy,
            "stream": this.stream
        }
    }

    intent validate() {
        if (this.timeout <= 0) {
            throw new Error("Timeout must be greater than zero")
        }
        if (this.retries < 0) {
            throw new Error("Retries must be zero or greater")
        }
    }
}

class RequestResponse {
    var ok: bool
    var status: int
    var reason: string
    var url: string
    var elapsed: float
    var headers
    var headerIndex
    var textValue: string
    var jsonValue
    var bytesValue
    var errorMessage: string

    intent constructor(raw) {
        if (raw == null) {
            raw = {}
        }
        this.ok = RequestResponse._bool(raw, "ok", false)
        this.status = RequestResponse._int(raw, "status", 0)
        this.reason = RequestResponse._string(raw, "reason", "")
        this.url = RequestResponse._string(raw, "url", "")
        this.elapsed = RequestResponse._float(raw, "elapsed", 0.0)
        this.textValue = RequestResponse._string(raw, "text", "")
        this.jsonValue = RequestResponse._field(raw, "json")
        this.bytesValue = RequestResponse._list(raw, "content")
        this.errorMessage = RequestResponse._string(raw, "error", "")
        this.headers = RequestResponse._map(raw, "headers")
        this.headerIndex = RequestResponse._map(raw, "headers")
        this._buildHeaderIndex()
    }

    static intent _field(raw, key: string) {
        if (raw == null) {
            return null
        }
        if (not mf.objects.mapHas(raw, key)) {
            return null
        }
        return raw[key]
    }

    static intent _bool(raw, key: string, fallback: bool): bool {
        var value = RequestResponse._field(raw, key)
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

    static intent _int(raw, key: string, fallback: int): int {
        var value = RequestResponse._field(raw, key)
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent _float(raw, key: string, fallback: float): float {
        var value = RequestResponse._field(raw, key)
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent _string(raw, key: string, fallback: string): string {
        var value = RequestResponse._field(raw, key)
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent _list(raw, key: string) {
        var value = RequestResponse._field(raw, key)
        if (value == null) {
            return new List([])
        }
        return new List(value)
    }

    static intent _map(raw, key: string) {
        var value = RequestResponse._field(raw, key)
        if (value == null) {
            return mf.objects.Map()
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

    intent _buildHeaderIndex() {
        var raw = this.headers
        if (raw == null) {
            raw = {}
        }
        if (type(raw) == "InstanceObject") {
            raw = raw.__raw__()
        }
        var keys = mf.objects.keys(raw)
        this.headerIndex = mf.objects.Map()
        var i = 0
        while (i < len(keys)) {
            var key = keys[i]
            var lower = key.lower()
            mf.objects.mapPut(this.headerIndex, lower, raw[key])
            i = i + 1
        }
    }

    intent isSuccess(): bool {
        return this.ok == true and this.status >= 200 and this.status < 400
    }

    intent isClientError(): bool {
        return this.status >= 400 and this.status < 500
    }

    intent isServerError(): bool {
        return this.status >= 500
    }

    intent hasError(): bool {
        return not this.isSuccess()
    }

    intent ensureSuccess(message: string) {
        if (this.isSuccess()) {
            return this
        }
        if (message == null or message == "") {
            message = "HTTP request failed with status " + this.status.toString()
        }
        throw new Error(message + ": " + this.error())
    }

    intent header(name: string): string {
        if (name == null) {
            return ""
        }
        var lower = name.lower()
        if (mf.objects.mapHas(this.headerIndex, lower)) {
            var value = mf.objects.mapGet(this.headerIndex, lower)
            if (value == null) {
                return ""
            }
            return value
        }
        return ""
    }

    intent headersMap() {
        return this.headers
    }

    intent text(): string {
        return this.textValue
    }

    intent json() {
        return this.jsonValue
    }

    intent bytes() {
        return this.bytesValue
    }

    intent error(): string {
        if (this.errorMessage != null and this.errorMessage != "") {
            return this.errorMessage
        }
        if (this.isSuccess()) {
            return ""
        }
        return this.reason
    }

    intent summary(): string {
        var statusText = this.status.toString()
        if (this.reason != "") {
            statusText = statusText + " " + this.reason
        }
        var urlText = this.url
        if (urlText == null) {
            urlText = ""
        }
        return "[" + statusText + "] " + urlText
    }
}

class RequestError {
    var message: string
    var response: RequestResponse

    intent constructor(message: string, response: RequestResponse) {
        this.message = message
        this.response = response
    }

    intent raise() {
        throw new RuntimeException(this.message, this.response)
    }

    intent raiseError() {
        this.raise()
    }
}

class Requests {
    private var uri: string
    private var defaults_headers
    private var defaultTimeout: float
    private var defaultRetries: int
    private var defaultVerify: bool
    private var defaultFollowRedirects: bool
    private var defaultProxy

    intent constructor(uri: string, defaults_headers) {
        this.uri = uri
        if (defaults_headers == null) {
            this.defaults_headers = mf.objects.Map()
        } else {
            this.defaults_headers = defaults_headers
        }
        this.defaultTimeout = 30.0
        this.defaultRetries = 3
        this.defaultVerify = true
        this.defaultFollowRedirects = true
        this.defaultProxy = null
        this._ensureHeader("User-Agent", "CorpLang-HTTP/1.0")
        this._ensureHeader("Accept", "application/json")
    }

    intent getUri() {
        return this.uri
    }

    intent getDefaultsHeaders() {
        return this.defaults_headers
    }

    intent setDefaultTimeout(timeoutSeconds: float) {
        if (timeoutSeconds != null and timeoutSeconds > 0) {
            this.defaultTimeout = timeoutSeconds
        }
    }

    intent setDefaultRetries(retries: int) {
        if (retries != null and retries >= 0) {
            this.defaultRetries = retries
        }
    }

    intent setDefaultVerify(verify: bool) {
        if (verify == null) {
            return
        }
        this.defaultVerify = verify
    }

    intent setDefaultFollowRedirects(value: bool) {
        if (value == null) {
            return
        }
        this.defaultFollowRedirects = value
    }

    intent setDefaultProxy(proxy) {
        this.defaultProxy = proxy
    }

    intent clearDefaultHeaders() {
        this.defaults_headers = mf.objects.Map()
    }

    intent header(name: string, value: string) {
        this._ensureHeader(name, value)
    }

    intent _ensureHeader(name: string, value: string) {
        if (name == null) {
            return
        }
        if (value == null) {
            value = ""
        }
        mf.objects.mapPut(this.defaults_headers, name, value)
    }

    static intent _copyMap(target, source) {
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

    intent newOptions(path: string, method: string): RequestOptions {
        var options = new RequestOptions(path, method)
        options.useTimeout(this.defaultTimeout)
        options.useRetries(this.defaultRetries)
        options.setVerifySSL(this.defaultVerify)
        options.setFollowRedirects(this.defaultFollowRedirects)
        if (this.defaultProxy != null) {
            options.setProxy(this.defaultProxy)
        }
        options.setHeaders(RequestOptions._cloneMap(this.defaults_headers))
        return options
    }

    intent get(path: string, params, headers, timeout) {
        var options = this.newOptions(path, "GET")
        options.setParams(params)
        options.setHeaders(headers)
        options.useTimeout(timeout)
        return this.execute(options)
    }

    intent post(path: string, data, headers, timeout) {
        var options = this.newOptions(path, "POST")
        options.setHeaders(headers)
        options.useTimeout(timeout)
        if (data != null) {
            options.setData(data)
        }
        return this.execute(options)
    }

    intent put(path: string, data, headers, timeout) {
        var options = this.newOptions(path, "PUT")
        options.setHeaders(headers)
        options.useTimeout(timeout)
        if (data != null) {
            options.setData(data)
        }
        return this.execute(options)
    }

    intent patch(path: string, data, headers, timeout) {
        var options = this.newOptions(path, "PATCH")
        options.setHeaders(headers)
        options.useTimeout(timeout)
        if (data != null) {
            options.setData(data)
        }
        return this.execute(options)
    }

    intent delete(path: string, headers, timeout) {
        var options = this.newOptions(path, "DELETE")
        options.setHeaders(headers)
        options.useTimeout(timeout)
        return this.execute(options)
    }

    intent head(path: string, headers, timeout) {
        var options = this.newOptions(path, "HEAD")
        options.setHeaders(headers)
        options.useTimeout(timeout)
        return this.execute(options)
    }

    intent options(path: string, headers, timeout) {
        var options = this.newOptions(path, "OPTIONS")
        options.setHeaders(headers)
        options.useTimeout(timeout)
        return this.execute(options)
    }

    intent request(options: RequestOptions) {
        return this.execute(options)
    }

    intent execute(options: RequestOptions) {
        if (options == null) {
            throw new Error("RequestOptions cannot be null")
        }
        options.setHeaders(options.headers)
        options.setParams(options.params)
        options.setURI(this.uri)
        options.validate()

        var merged = RequestOptions._cloneMap(this.defaults_headers)
        Requests._copyMap(merged, options.headers)
        options.setHeaders(merged)

        if (options.timeout == null or options.timeout <= 0) {
            options.useTimeout(this.defaultTimeout)
        }
        if (options.retries == null or options.retries < 0) {
            options.useRetries(this.defaultRetries)
        }
        if (options.ssl_verify == null) {
            options.setVerifySSL(this.defaultVerify)
        }
        if (options.follow_redirects == null) {
            options.setFollowRedirects(this.defaultFollowRedirects)
        }
        if (options.proxy == null and this.defaultProxy != null) {
            options.setProxy(this.defaultProxy)
        }

        var rawResponse = mf.strict.https.request(options.dictionary())
        if (rawResponse == null) {
            rawResponse = mf.objects.Map()
            mf.objects.mapPut(rawResponse, "ok", false)
            mf.objects.mapPut(rawResponse, "status", 0)
            mf.objects.mapPut(rawResponse, "error", "Empty response")
            mf.objects.mapPut(rawResponse, "url", options.path)
            mf.objects.mapPut(rawResponse, "content", [])
            mf.objects.mapPut(rawResponse, "headers", mf.objects.Map())
        }
        return new RequestResponse(rawResponse)
    }

    intent openSocket(host: string, port: int, timeout) {
        return TcpConnection.connect(host, port, timeout)
    }
}