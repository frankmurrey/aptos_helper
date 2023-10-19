from pydantic import ValidationError

class AppValidationError(ValueError):
    def __init__(
            self,
            message: str,
    ):
        self.message = message
        super().__init__(message)
