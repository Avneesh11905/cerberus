import pytest
from src.shared.domain.value_objects.email_address import EmailAddress
from src.shared.domain.value_objects.person_name import PersonName
from src.shared.domain.value_objects.https_url import HttpsUrl


def test_email_address_valid():
    email = EmailAddress("Test@Example.com ")
    assert email.value == "test@example.com"
    assert str(email) == "test@example.com"


def test_email_address_invalid():
    with pytest.raises(ValueError, match="Invalid email format"):
        EmailAddress("invalid-email")


def test_email_address_non_string():
    class Dummy:
        def __str__(self):
            return "dummy@test.com"

    email = EmailAddress(Dummy())  # type: ignore
    assert email.value == "dummy@test.com"


def test_email_address_eq():
    e1 = EmailAddress("a@b.com")
    e2 = EmailAddress("a@b.com")
    assert e1 == e2
    assert e1 == "a@b.com"
    assert e1 != "b@b.com"
    assert e1 != 123


def test_person_name_valid():
    name = PersonName("  John Doe  ")
    assert name.value == "John Doe"
    assert str(name) == "John Doe"


def test_person_name_too_long():
    with pytest.raises(ValueError, match="Name too long"):
        PersonName("a" * 101)


def test_person_name_non_string():
    class Dummy:
        def __str__(self):
            return "Dummy Name"

    name = PersonName(Dummy())  # type: ignore
    assert name.value == "Dummy Name"


def test_person_name_eq():
    n1 = PersonName("John")
    n2 = PersonName("John")
    assert n1 == n2
    assert n1 == "John"
    assert n1 != "Jane"
    assert n1 != 123


def test_https_url_valid():
    url = HttpsUrl("https://example.com")
    assert url.value == "https://example.com"
    assert str(url) == "https://example.com"

    url_local = HttpsUrl("http://localhost:3000")
    assert url_local.value == "http://localhost:3000"


def test_https_url_invalid():
    with pytest.raises(ValueError, match="Must be an HTTPS URL or http://localhost"):
        HttpsUrl("http://example.com")


def test_https_url_non_string():
    class Dummy:
        def __str__(self):
            return "https://dummy.com"

    url = HttpsUrl(Dummy())  # type: ignore
    assert url.value == "https://dummy.com"


def test_https_url_eq():
    u1 = HttpsUrl("https://example.com")
    u2 = HttpsUrl("https://example.com")
    assert u1 == u2
    assert u1 == "https://example.com"
    assert u1 != "https://other.com"
    assert u1 != 123
