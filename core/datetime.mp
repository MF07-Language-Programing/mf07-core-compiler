
interface Date {
    intent toString(): string
    intent toClass(): string
    intent to_timestamp(): float
    intent format(fmt: string): string
    intent today(): Date
}

class DateTime implements Date {
    static var __default_class__: string = "datetime"


    private var __class__: string
    private var _year: int
    private var _month: int
    private var _day: int
    private var _hour: int
    private var _minute: int
    private var _second: int
    private var _microsecond: int
    private var _tzinfo: Optional[string]
    private var _hashcode: string
    private var _fold: int

    intent constructor(_fold: int, _hashcode: string, tzinfo: Optional[string], microsecond: int, second: int, minute: int, hour: int, day: int, month: int, year: int, __class__: Optional[Union[datetime, string]]) {
        # Initialize all fields
        this._fold = _fold
        this._hashcode = _hashcode
        this._tzinfo = tzinfo
        this._microsecond = microsecond
        this._second = second
        this._minute = minute
        this._hour = hour
        this._day = day
        this._month = month
        this._year = year
        # If datetime string is not provided, use a default value
        this.__class__ = __class__
        if (this.__class__ == null) {
            this.__class__ = "datetime"
        }
    }

    static intent now(_tz: Optional[string]): DateTime {
        var dt = mf.datetime.now()
        var _fold: int = 0
        var __bytes__ = mf.hash.base64_decode(dt.isoformat().encode("utf-8"))
        var _hashcode: string = mf.hash.apply_hash_algorithm("sha256", __bytes__)
        var tzinfo: Optional[string] = null
        if (dt.tzinfo != null) {
            tzinfo = dt.tzinfo.tzname(None)
        }
        return new DateTime(_fold, _hashcode, tzinfo, dt.microsecond, dt.second, dt.minute, dt.hour, dt.day, dt.month, dt.year, DateTime.__default_class__)
    }

    intent to_timestamp(): float {
        var dt = mf.datetime.datetime(this._year, this._month, this._day, this._hour, this._minute, this._second, this._microsecond)
        return dt.timestamp()
    }

    intent format(fmt: string): string {
        var dt = mf.datetime.datetime(this._year, this._month, this._day, this._hour, this._minute, this._second, this._microsecond)
        return dt.strftime(fmt)
    }

    intent toString(): string {
        # Prefer ISO-like representation
        var dt = mf.datetime.datetime(this._year, this._month, this._day, this._hour, this._minute, this._second, this._microsecond)
        try {
            return dt.isoformat()
        } catch (e) {
            return "[__class__={this.__class__}, year={this._year}, month={this._month}, day={this._day}]"
        }
    }

    intent toClass(): string {
        return this.__class__
    }

    # Return a Date object representing today in local timezone
    intent today(): Date {
        # delegate to static now() using no timezone
        return DateTime.now(null)
    }

    # Create DateTime from unix timestamp
    static intent from_timestamp(ts: float, _tz: Optional[string]): DateTime {
        var dt = mf.datetime.from_timestamp(ts)
        var _fold: int = 0
        var __bytes__ = mf.hash.base64_decode(dt.isoformat().encode("utf-8"))
        var _hashcode: string = mf.hash.apply_hash_algorithm("sha256", __bytes__)
        var tzinfo: Optional[string] = null
        if (dt.tzinfo != null) {
            tzinfo = dt.tzinfo.tzname(None)
        }
        return new DateTime(_fold, _hashcode, tzinfo, dt.microsecond, dt.second, dt.minute, dt.hour, dt.day, dt.month, dt.year, DateTime.__default_class__)
    }
}