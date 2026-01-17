from resume_analyzer.parsing.contact import extract_contact_info, normalize_phone, normalize_url


def test_normalize_url_www():
    assert normalize_url("www.github.com/user") == "https://www.github.com/user"


def test_normalize_phone_basic():
    assert normalize_phone("+91 98765-43210") == "+919876543210"
    assert normalize_phone("98765 43210") == "9876543210"
    assert normalize_phone("12345") == ""


def test_extract_contact_info():
    text = """
    Name: Test User
    Email: test.user+dev@gmail.com
    Phone: +91 98765 43210
    GitHub: https://github.com/testuser
    LinkedIn: www.linkedin.com/in/test-user
    Portfolio: http://example.com
    """

    c = extract_contact_info(text)
    assert c.email == "test.user+dev@gmail.com"
    assert "+919876543210" in c.phones
    assert c.github and "github.com/testuser" in c.github
    assert c.linkedin and "linkedin.com/in/test-user" in c.linkedin
    assert any("example.com" in u for u in c.links)
