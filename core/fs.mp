# core/fs.mp
# Biblioteca de arquivos e diretórios para CorpLang

class FileSystem {
    static intent readText(path: string, encoding) {
        var useEncoding = FileSystem._encodingOrDefault(encoding)
        var response = mf.fs.read_text(path, useEncoding)
        if (FileSystem._responseOk(response)) {
            return response["content"]
        }
        FileSystem._printError("readText", response)
        return null
    }

    static intent readJSON(path: string, encoding) {
        var useEncoding = FileSystem._encodingOrDefault(encoding)
        var response = mf.fs.read_json(path, useEncoding)
        if (FileSystem._responseOk(response)) {
            return response["data"]
        }
        FileSystem._printError("readJSON", response)
        return null
    }

    static intent writeText(path: string, content, encoding): bool {
        var useEncoding = FileSystem._encodingOrDefault(encoding)
        var response = mf.fs.write_text(path, content, useEncoding)
        if (FileSystem._responseOk(response)) {
            return true
        }
        FileSystem._printError("writeText", response)
        return false
    }

    static intent appendText(path: string, content, encoding): bool {
        var useEncoding = FileSystem._encodingOrDefault(encoding)
        var response = mf.fs.append_text(path, content, useEncoding)
        if (FileSystem._responseOk(response)) {
            return true
        }
        FileSystem._printError("appendText", response)
        return false
    }

    static intent writeJSON(path: string, data, encoding): bool {
        var useEncoding = FileSystem._encodingOrDefault(encoding)
        var response = mf.fs.write_json(path, data, useEncoding, 2, false)
        if (FileSystem._responseOk(response)) {
            return true
        }
        FileSystem._printError("writeJSON", response)
        return false
    }

    static intent readBytes(path: string) {
        var response = mf.fs.read_bytes(path)
        if (FileSystem._responseOk(response)) {
            return new List(response["content"])
        }
        FileSystem._printError("readBytes", response)
        return new List([])
    }

    static intent writeBytes(path: string, data): bool {
        var payload = FileSystem._coerceList(data)
        var response = mf.fs.write_bytes(path, payload.__raw__())
        if (FileSystem._responseOk(response)) {
            return true
        }
        FileSystem._printError("writeBytes", response)
        return false
    }

    static intent exists(path: string): bool {
        return mf.fs.exists(path)
    }

    static intent isFile(path: string): bool {
        return mf.fs.is_file(path)
    }

    static intent isDirectory(path: string): bool {
        return mf.fs.is_dir(path)
    }

    static intent ensureDir(path: string): bool {
        var response = mf.fs.make_dir(path, true)
        if (FileSystem._responseOk(response)) {
            return true
        }
        FileSystem._printError("ensureDir", response)
        return false
    }

    static intent touch(path: string): bool {
        var response = mf.fs.touch(path)
        if (FileSystem._responseOk(response)) {
            return true
        }
        FileSystem._printError("touch", response)
        return false
    }

    static intent remove(path: string, recursive: bool): bool {
        if (recursive == null) {
            recursive = false
        }
        var response = mf.fs.remove(path, recursive)
        if (FileSystem._responseOk(response)) {
            return response["removed"] == true or not FileSystem.exists(path)
        }
        FileSystem._printError("remove", response)
        return false
    }

    static intent copy(source: string, destination: string, overwrite: bool): bool {
        if (overwrite == null) {
            overwrite = true
        }
        var response = mf.fs.copy(source, destination, overwrite)
        if (FileSystem._responseOk(response)) {
            return true
        }
        FileSystem._printError("copy", response)
        return false
    }

    static intent move(source: string, destination: string, overwrite: bool) {
        if (overwrite == null) {
            overwrite = true
        }
        var response = mf.fs.move(source, destination, overwrite)
        if (FileSystem._responseOk(response)) {
            return response["destination"]
        }
        FileSystem._printError("move", response)
        return ""
    }

    static intent stat(path: string) {
        var response = mf.fs.stat(path)
        if (FileSystem._responseOk(response)) {
            return new FileInfo(response["info"])
        }
        FileSystem._printError("stat", response)
        return null
    }

    static intent listDir(path: string, recursive: bool) {
        if (recursive == null) {
            recursive = false
        }
        var response = mf.fs.list_dir(path, recursive)
        if (FileSystem._responseOk(response)) {
            var entries = response["entries"]
            var result = new List([])
            if (entries == null) {
                return result
            }
            var i = 0
            while (i < len(entries)) {
                result.append(new DirectoryEntry(entries[i]))
                i = i + 1
            }
            return result
        }
        FileSystem._printError("listDir", response)
        return new List([])
    }

    static intent glob(path: string, pattern: string) {
        var response = mf.fs.glob(path, pattern)
        if (FileSystem._responseOk(response)) {
            return new List(response["matches"])
        }
        FileSystem._printError("glob", response)
        return new List([])
    }

    static intent walk(path: string) {
        var response = mf.fs.walk(path)
        if (FileSystem._responseOk(response)) {
            var frames = response["entries"]
            var result = new List([])
            if (frames == null) {
                return result
            }
            var i = 0
            while (i < len(frames)) {
                result.append(new WalkEntry(frames[i]))
                i = i + 1
            }
            return result
        }
        FileSystem._printError("walk", response)
        return new List([])
    }

    static intent parent(path: string): string {
        return mf.fs.parent(path)
    }

    static intent cwd(): string {
        return mf.fs.cwd()
    }

    static intent home(): string {
        return mf.fs.home()
    }

    static intent separator(): string {
        return mf.fs.separator()
    }

    static intent removeDir(path: string, recursive: bool): bool {
        if (recursive == null) {
            recursive = true
        }
        return FileSystem.remove(path, recursive)
    }

    static intent _encodingOrDefault(value): string {
        if (value == null or value == "") {
            return "utf-8"
        }
        return value
    }

    static intent _responseOk(response) {
        if (response == null) {
            return false
        }
        if (mf.objects.mapHas(response, "ok")) {
            return response["ok"] == true
        }
        if (mf.objects.mapHas(response, "success")) {
            return response["success"] == true
        }
        return false
    }

    static intent _printError(operation: string, response) {
        var message = "FileSystem error in " + operation
        if (response != null and mf.objects.mapHas(response, "error")) {
            message = message + ": " + response["error"]
        }
        print(message)
    }

    static intent _coerceList(data) {
        if (data == null) {
            return new List([])
        }
        var dataType = type(data)
        if (dataType == "InstanceObject") {
            return data
        }
        if (dataType == "list") {
            return new List(data)
        }
        var result = new List([])
        result.append(data)
        return result
    }

    static intent _stringField(raw, key: string, fallback: string): string {
        if (raw == null) {
            return fallback
        }
        if (not mf.objects.mapHas(raw, key)) {
            return fallback
        }
        var value = raw[key]
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent _boolField(raw, key: string, fallback: bool): bool {
        if (raw == null) {
            return fallback
        }
        if (not mf.objects.mapHas(raw, key)) {
            return fallback
        }
        var value = raw[key]
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

    static intent _intField(raw, key: string, fallback: int): int {
        if (raw == null) {
            return fallback
        }
        if (not mf.objects.mapHas(raw, key)) {
            return fallback
        }
        var value = raw[key]
        if (value == null) {
            return fallback
        }
        return value
    }

    static intent _listField(raw, key: string) {
        if (raw == null) {
            return new List([])
        }
        if (not mf.objects.mapHas(raw, key)) {
            return new List([])
        }
        var value = raw[key]
        return FileSystem._coerceList(value)
    }
}

class FileInfo {
    var path: string
    var size: int
    var modified: string
    var created: string
    var accessed: string
    var isFileFlag: bool
    var isDirectoryFlag: bool

    intent constructor(raw) {
        this.path = FileSystem._stringField(raw, "path", "")
        this.size = FileSystem._intField(raw, "size", 0)
        this.modified = FileSystem._stringField(raw, "modified", "")
        this.created = FileSystem._stringField(raw, "created", "")
        this.accessed = FileSystem._stringField(raw, "accessed", "")
        this.isFileFlag = FileSystem._boolField(raw, "is_file", false)
        this.isDirectoryFlag = FileSystem._boolField(raw, "is_dir", false)
    }

    intent isFile(): bool {
        return this.isFileFlag
    }

    intent isDirectory(): bool {
        return this.isDirectoryFlag
    }
}

class DirectoryEntry {
    var name: string
    var path: string
    var type: string
    var size

    intent constructor(raw) {
        this.name = FileSystem._stringField(raw, "name", "")
        this.path = FileSystem._stringField(raw, "path", "")
        this.type = FileSystem._stringField(raw, "type", "file")
        var sizeValue: int = 0
        if (raw != null and mf.objects.mapHas(raw, "size")) {
            var value = raw["size"]
            if (value != null) {
                sizeValue = value
            }
        }
        this.size = sizeValue
    }

    intent isFile(): bool {
        return this.type == "file"
    }

    intent isDirectory(): bool {
        return this.type == "dir"
    }
}

class WalkEntry {
    var path: string
    var directories
    var files

    intent constructor(raw) {
        this.path = FileSystem._stringField(raw, "path", "")
        this.directories = FileSystem._listField(raw, "directories")
        this.files = FileSystem._listField(raw, "files")
    }
}

class File {
    var path: string

    intent constructor(path: string) {
        this.path = path
    }

    intent exists(): bool {
        return FileSystem.exists(this.path)
    }

    intent readText(encoding) {
        return FileSystem.readText(this.path, encoding)
    }

    intent readJSON(encoding) {
        return FileSystem.readJSON(this.path, encoding)
    }

    intent writeText(content, encoding): bool {
        return FileSystem.writeText(this.path, content, encoding)
    }

    intent appendText(content, encoding): bool {
        return FileSystem.appendText(this.path, content, encoding)
    }

    intent writeJSON(data, encoding): bool {
        return FileSystem.writeJSON(this.path, data, encoding)
    }

    intent readBytes() {
        return FileSystem.readBytes(this.path)
    }

    intent writeBytes(data): bool {
        return FileSystem.writeBytes(this.path, data)
    }

    intent touch(): bool {
        return FileSystem.touch(this.path)
    }

    intent remove(): bool {
        return FileSystem.remove(this.path, false)
    }

    intent copyTo(destination: string, overwrite: bool): bool {
        return FileSystem.copy(this.path, destination, overwrite)
    }

    intent moveTo(destination: string, overwrite: bool): bool {
        var result = FileSystem.move(this.path, destination, overwrite)
        if (result == "") {
            return false
        }
        this.path = result
        return true
    }

    intent info() {
        return FileSystem.stat(this.path)
    }

    intent parent(): string {
        return FileSystem.parent(this.path)
    }

    intent name(): string {
        return mf.path.basename(this.path)
    }

    intent extension(): string {
        return mf.path.extname(this.path)
    }

    intent stem(): string {
        return mf.path.stem(this.path)
    }

    intent directory() {
        return new Directory(mf.path.dirname(this.path))
    }
}

class Directory {
    var path: string

    intent constructor(path: string) {
        this.path = path
    }

    intent exists(): bool {
        return FileSystem.isDirectory(this.path)
    }

    intent ensure(): bool {
        return FileSystem.ensureDir(this.path)
    }

    intent remove(recursive: bool): bool {
        return FileSystem.removeDir(this.path, recursive)
    }

    intent list(recursive: bool) {
        return FileSystem.listDir(this.path, recursive)
    }

    intent file(name: string) {
        return new File(mf.path.join(this.path, name))
    }

    intent directory(name: string) {
        return new Directory(mf.path.join(this.path, name))
    }
}
