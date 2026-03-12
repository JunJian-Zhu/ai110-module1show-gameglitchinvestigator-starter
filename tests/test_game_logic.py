from logic_utils import check_guess, parse_guess, get_range_for_difficulty

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

# FIX: Added test to verify the swapped Higher/Lower message bug is resolved.
# Before the fix, guess > secret returned "Go HIGHER!" instead of "Go LOWER!".
def test_too_high_message_says_lower():
    outcome, message = check_guess(70, 50)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_too_low_message_says_higher():
    outcome, message = check_guess(30, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message

# FIX: Added test to confirm integer comparison is used, not string comparison.
# Before the fix, on even attempts secret was cast to str, causing "9" > "42" = True
# (lexicographic), which made check_guess return wrong outcomes.
def test_check_guess_uses_integer_comparison():
    # 9 < 42 numerically, so outcome must be "Too Low"
    outcome, _ = check_guess(9, 42)
    assert outcome == "Too Low"

def test_parse_guess_valid():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None

def test_parse_guess_empty():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None

def test_parse_guess_non_number():
    ok, value, err = parse_guess("abc")
    assert ok is False

def test_get_range_easy():
    low, high = get_range_for_difficulty("Easy")
    assert low == 1 and high == 20

def test_get_range_normal():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1 and high == 100

# --- Edge Case Tests (Challenge 1) ---
# These were identified via AI-assisted prompting:
# "What inputs could break a number guessing game's parse function?"

def test_parse_guess_negative_number():
    # Edge case: negative numbers are valid integers and should parse successfully.
    # The game logic (check_guess) will correctly treat -5 as lower than any secret.
    ok, value, err = parse_guess("-5")
    assert ok is True
    assert value == -5
    assert err is None

def test_parse_guess_decimal_truncates():
    # Edge case: a decimal like "7.9" should be accepted and truncated to 7,
    # not rejected or rounded up. The player typed a near-integer, not garbage.
    ok, value, err = parse_guess("7.9")
    assert ok is True
    assert value == 7
    assert err is None

def test_parse_guess_very_large_number():
    # Edge case: an absurdly large number (e.g. 999999) should parse without
    # crashing. check_guess will simply return "Too High" since it exceeds any secret.
    ok, value, err = parse_guess("999999")
    assert ok is True
    assert value == 999999
    assert err is None

def test_check_guess_negative_guess_is_too_low():
    # Edge case: a negative guess is always below any valid secret (min is 1),
    # so the outcome must be "Too Low" — not a crash or unexpected result.
    outcome, message = check_guess(-10, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message

def test_parse_guess_whitespace_only():
    # Edge case: a string of spaces should be treated as empty/invalid input.
    ok, value, err = parse_guess("   ")
    assert ok is False
    assert value is None
