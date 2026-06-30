from app.services.shortcode import BASE62_ALPHABET, generate_short_code


def test_default_length_is_seven():
    assert len(generate_short_code()) == 7


def test_custom_length_respected():
    assert len(generate_short_code(length=10)) == 10


def test_only_base62_characters():
    code = generate_short_code(length=50)
    assert all(ch in BASE62_ALPHABET for ch in code)


def test_codes_are_not_trivially_repeated():
    # Not a proof of uniqueness, just a smoke test that we're not returning
    # a constant or low-entropy value.
    codes = {generate_short_code() for _ in range(1000)}
    assert len(codes) == 1000
