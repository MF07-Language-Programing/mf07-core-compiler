"""Module de teste para docstrings em intents."""

var logger = new Logger()

intent test_docstring(){
    """
    This intent tests the docstring functionality.
    It contains multiple lines to verify proper handling.
    """
    logger.info("This is a test for docstrings.")
}

test_docstring()