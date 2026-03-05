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
