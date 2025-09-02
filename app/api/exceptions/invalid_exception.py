class InvalidError(Exception):
    def __init__(self, message, http_status_code, error_code, error_type):
        self.http_status_code = http_status_code
        self.error_code = error_code
        self.error_type = error_type
        self.message = message
        super().__init__(self.message)

    def to_dict(self):
        return {
            "http_status_code": self.http_status_code,
            "error_code": self.error_code,
            "error_type": self.error_type,
            "message": self.message,
        }

    def __str__(self):
        return (
            f"InvalidError: {self.message}. Error code: {self.error_code}. "
            f"HTTP status code: {self.http_status_code}. message: {self.message}"
        )
