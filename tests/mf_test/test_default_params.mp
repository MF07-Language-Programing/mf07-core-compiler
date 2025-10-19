// Test file for default parameter values and Union types

// Import the enhanced logger
import core.logger

// Function with default parameter values
intent greet(name: str = "World", age: int = 25) {
    log("Hello " + name + ", you are " + age + " years old!")
}

// Function with Union types (when fully implemented)
// intent processValue(value: Union[str, int]) {
//     log("Processing value: " + value)
// }

// Test the functions
greet()  // Should use defaults: "World" and 25
greet("Alice")  // Should use "Alice" and default age 25
greet("Bob", 30)  // Should use both provided values

// Test logger with default min_level
logger = new Logger()  // Should use default LogLevel.INFO
logger.info("This is an info message")
logger.debug("This debug message might not show due to default level")

// Test logger with custom min_level
customLogger = new Logger(LogLevel.DEBUG)
customLogger.debug("This debug message should show with DEBUG level")