import pytest

from django_expertise import setup_dev


@pytest.mark.parametrize(
    "password,expected_insecure",
    [
        ("short", True),
        ("LongEnough123", False),
        ("nouppercase123", True),
        ("NOLOWERCASE123", True),
        ("NoDigitsHere", True),
    ],
)
def test_is_insecure_password(password, expected_insecure):
    assert setup_dev._is_insecure_password(password) is expected_insecure
