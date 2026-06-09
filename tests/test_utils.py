"""Unit tests for Base62 encoding/decoding."""

from app.utils import decode, encode, BASE, ALPHABET


class TestEncode:
    def test_zero(self):
        assert encode(0) == "0"

    def test_one(self):
        assert encode(1) == "1"

    def test_base(self):
        assert encode(BASE) == "10"

    def test_known_values(self):
        assert encode(1000000) == "4c92"

    def test_roundtrip(self):
        for n in [0, 1, 42, 100, 9999, 1000000, 999999999]:
            assert decode(encode(n)) == n

    def test_positive_only(self):
        """Encode only handles non-negative integers."""
        assert isinstance(encode(1), str)


class TestDecode:
    def test_single_char(self):
        for i, char in enumerate(ALPHABET):
            assert decode(char) == i

    def test_known_values(self):
        assert decode("4c92") == 1000000

    def test_case_sensitive(self):
        """Base62 is case-sensitive: 'a' != 'A'."""
        assert decode("a") != decode("A")
