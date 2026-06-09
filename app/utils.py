"""URL shortening utilities using Base62 encoding."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


def encode(num: int) -> str:
    """Encode a positive integer to a Base62 string.

    Examples:
        >>> encode(1)
        '1'
        >>> encode(62)
        '10'
        >>> encode(1000000)
        '4c92'
    """
    if num == 0:
        return ALPHABET[0]

    result = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        result.append(ALPHABET[remainder])

    return "".join(reversed(result))


def decode(short_id: str) -> int:
    """Decode a Base62 string back to an integer.

    Examples:
        >>> decode('1')
        1
        >>> decode('10')
        62
        >>> decode('4c92')
        1000000
    """
    result = 0
    for char in short_id:
        result = result * BASE + ALPHABET.index(char)

    return result
