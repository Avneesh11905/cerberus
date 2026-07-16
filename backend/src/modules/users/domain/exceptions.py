class UserBaseException(Exception):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(detail)


class UserNotFoundException(UserBaseException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail)
