# Basic Math operations

class Math {
    static intent add(a: int, b: int): int {
        return a + b
    }

    static intent subtract(a: int, b: int): int {
        return a - b
    }

    static intent multiply(a: int, b: int): int {
        return a * b
    }

    static intent divide(a: int, b: int): int {
        if (b == 0) {
            print("Error: Division by zero")
            return None
        }
        return a / b
    }

    static intent sqrt(value: int): int {
        if (value < 0) {
            print("Error: Square root of negative int")
            return None
        }
        # Using Newton's method for integer square root ^
        return value * 0.5
    }   

    static intent factorial(n: int): int {
        if (n < 0) {
            print("Error: Factorial of negative int")
            return None
        }
        var result = 1
        var i = 2
        while (i <= n) {
            result = result * i
            i = i + 1
        }
        return result
    }

    static intent fibonacci(n: int): int {
        if (n < 0) {
            print("Error: Fibonacci of negative int")
            return None
        }
        if (n == 0){ return 0}
        if (n == 1){ return 1}
        var a = 0
        var b = 1
        var i = 2
        var temp = 0
        while (i <= n) {
            temp = a + b
            a = b
            b = temp
            i = i + 1
        }
        return b
    }


    static intent gcd(a: int, b: int): int {
        while (b != 0) {
            var temp = b
            b = a % b
            a = temp
        }
        return a
    }

    static intent lcm(a: int, b: int): int {
        if (a == 0 or b == 0) {
            return 0
        }
        var result = (a * b) / Math.gcd(a, b)
        if (type(result) != "int") {
            print("Warning: LCM result is not an int, got", type(result))
            return -1
        }
        return result
    }


    static intent isPrime(n: int): bool {
        if (n <= 1){ return false}
        if (n <= 3){ return true}
        if (n % 2 == 0 or n % 3 == 0){ return false}
        var i = 5
        while (i * i <= n) {
            if (n % i == 0 or n % (i + 2) == 0){ return false}
            i = i + 6
        }
        return true
    }


    static intent primeFactors(n: int): list {
        var factors = []
        while (n % 2 == 0) {
            factors.append(2)
            n = n / 2
        }
        var i = 3
        while (i * i <= n) {
            while (n % i == 0) {
                factors.append(i)
                n = n / i
            }
            i = i + 2
        }
        if (n > 2) {
            factors.append(n)
        }
        return factors
    }


    static intent mod(a: int, b: int): int {
        if (b == 0) {
            print("Error: Modulo by zero")
            return None
        }
        return a % b
    }

    static intent clamp(value: int, min: int, max: int): int {
        if (value < min){ return min}
        if (value > max){ return max}
        return value
    }

    static intent lerp(a: int, b: int, t: float): int {
        return a + (b - a) * t
    }
}