class NazurinError(Exception):
    def __init__(self, msg):
        """Initialize with error message."""
        super().__init__(msg)
        self.msg = str(msg)

    def __str__(self):
        """Returns the string representation of this exception."""
        return self.msg


class InvalidCommandUsageError(NazurinError):
    """Raised when a command is used incorrectly."""

    command: str

    def __init__(self, command):
        self.command = command
        super().__init__(f"Invalid usage of command {command}")


class AlreadyExistsError(NazurinError):
    def __init__(self, msg="Already exists in database, skipped update."):
        super().__init__(msg)
