import sys


class TokensErrorException(Exception):
    sys.exit


class JsonError(Exception):
    pass
