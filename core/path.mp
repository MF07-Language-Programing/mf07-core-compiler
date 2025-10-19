# core/path.mp
# Utilidades modernas de manipulação de caminhos para CorpLang

class Path {
    static intent separator(): string {
        return mf.fs.separator()
    }

    static intent cwd(): string {
        return mf.path.cwd()
    }

    static intent home(): string {
        return mf.path.home()
    }

    static intent join(base, part1, part2, part3, part4) {
        var segments = mf.collections.List()
        Path._appendSegment(segments, base)
        Path._appendSegment(segments, part1)
        Path._appendSegment(segments, part2)
        Path._appendSegment(segments, part3)
        Path._appendSegment(segments, part4)
        return mf.path.join_all(segments)
    }

    static intent joinSegments(values) {
        if (values == null) {
            return ""
        }
        if (type(values) == "list") {
            return mf.path.join_all(values)
        }
        if (type(values) == "InstanceObject") {
            return mf.path.join_all(values.__raw__())
        }
        return ""
    }

    static intent basename(path: string): string {
        return mf.path.basename(path)
    }

    static intent dirname(path: string): string {
        return mf.path.dirname(path)
    }

    static intent stem(path: string): string {
        return mf.path.stem(path)
    }

    static intent extension(path: string): string {
        return mf.path.extname(path)
    }

    static intent normalize(path: string): string {
        return mf.path.normalize(path)
    }

    static intent resolve(path: string, base: string): string {
        if (base == null) {
            return mf.path.resolve(path)
        }
        return mf.path.resolve(path, base)
    }

    static intent relative(path: string, start: string): string {
        return mf.path.relative_to(path, start)
    }

    static intent isAbsolute(path: string): bool {
        return mf.path.is_absolute(path)
    }

    static intent match(path: string, pattern: string): bool {
        return mf.path.match(path, pattern)
    }

    static intent parts(path: string) {
        var raw = mf.path.parts(path)
        return new List(raw)
    }

    static intent split(path: string) {
        return Path.parts(path)
    }

    static intent commonPath(paths) {
        if (paths == null) {
            return ""
        }
        if (type(paths) == "list") {
            return mf.path.common_path(paths)
        }
        if (type(paths) == "InstanceObject") {
            return mf.path.common_path(paths.__raw__())
        }
        return ""
    }

    static intent withSuffix(path: string, suffix: string): string {
        return mf.path.with_suffix(path, suffix)
    }

    static intent toPOSIX(path: string): string {
        return mf.path.to_posix(path)
    }

    static intent toWindows(path: string): string {
        return mf.path.to_windows(path)
    }

    static intent drive(path: string): string {
        return mf.path.drive(path)
    }

    static intent expandUser(path: string): string {
        return mf.path.expanduser(path)
    }

    static intent parent(path: string): string {
        var result = mf.fs.parent(path)
        if (result == null) {
            return ""
        }
        return result
    }

    static intent _appendSegment(container, value) {
        if (value == null) {
            return
        }
        if (value == "") {
            return
        }
        if (container == null) {
            return
        }
        container.push(value)
    }
}
