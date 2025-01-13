ResponseCodeMapping = (
    ("HTTP_200", "OK"),
    ("HTTP_400", "BAD_REQUEST"),
    ("HTTP_401", "UNAUTHORIZED"),
    ("HTTP_403", "FORBIDDEN"),
    ("HTTP_404", "NOT_FOUND"),
    ("HTTP_500", "INTERNAL_SERVER_ERROR"),
)

ResponseCode = type("Enum", tuple(), dict(ResponseCodeMapping))