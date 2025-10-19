
class LogLevel {
    static var DEBUG: int = 10
    static var INFO: int = 20
    static var WARNING: int = 30
    static var ERROR: int = 40
    static var CRITICAL: int = 50
}

class Logger {
    private var level: Optional[int]
    private var log_file: Optional[string]

    intent constructor(level: Optional[int], log_file: Optional[string]) {
        this.level = level
        if (this.level == null) {
            this.level = LogLevel.INFO
        }
        this.log_file = log_file
        if (this.log_file == null) {
            this.log_file = "app.log.running"
        }
    }

    intent _get_format_message_(level: int, message: string): string {
        var level_name = ""
        if (level == LogLevel.DEBUG) {
            level_name = "DEBUG"
        } else if (level == LogLevel.INFO) {
            level_name = "INFO"
        } else if (level == LogLevel.WARNING) {
            level_name = "WARNING"
        } else if (level == LogLevel.ERROR) {
            level_name = "ERROR"
        } else if (level == LogLevel.CRITICAL) {
            level_name = "CRITICAL"
        }
        var timestamp = DateTime.now()
        var timestamps_formatted = timestamp.format("%Y-%m-%d %H:%M:%S")
        return "[{timestamps_formatted}] {level_name}: {message}"
    }

    intent _log(message: string, level: int) {  
        if (level < this.level) {
            return
        }
        var log_message: string = this._get_format_message_(level, message)
        sout(log_message)
    }

    intent debug(message: string) {
        this._log(message, LogLevel.DEBUG)
    }

    intent info(message: string) {
        this._log(message, LogLevel.INFO)
    }

    intent warning(message: string) {
        this._log(message, LogLevel.WARNING)
    }

    intent warn(message: string) {
        this._log(message, LogLevel.WARNING)
    }

    intent error(message: string) {
        this._log(message, LogLevel.ERROR)
    }

    intent critical(message: string) {
        this._log(message, LogLevel.CRITICAL)
    }
}

var console = new Logger(LogLevel.DEBUG, "application.log")