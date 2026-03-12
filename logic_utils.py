"""
logic_utils.py — Core game logic for the Game Glitch Investigator.

All functions here are pure (no Streamlit imports) so they can be tested
independently with pytest. The UI layer in app.py calls these functions
and owns all session state.

Reviewed for PEP 8 compliance using Claude Code with the prompt:
"Review logic_utils.py for PEP 8 style issues: naming, spacing, line length,
type annotations, and docstring format. Apply fixes."
"""

from __future__ import annotations


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive (low, high) number range for a given difficulty.

    Args:
        difficulty: One of "Easy", "Normal", or "Hard". Any other value
            falls back to the Normal range.

    Returns:
        A tuple (low, high) where both values are inclusive bounds for
        the secret number.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 50)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str) -> tuple[bool, int | None, str | None]:
    """Parse raw text input from the player into a validated integer guess.

    Accepts whole numbers and decimal strings (decimals are truncated, not
    rounded). Rejects None, empty strings, whitespace-only strings, and
    non-numeric text.

    Args:
        raw: The raw string typed by the player in the guess input box.

    Returns:
        A 3-tuple ``(ok, value, error)``:

        - ``ok`` (bool): True if parsing succeeded, False otherwise.
        - ``value`` (int | None): The parsed integer, or None on failure.
        - ``error`` (str | None): A human-readable error message, or None
          on success.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("7.9")
        (True, 7, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except (ValueError, TypeError):
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare the player's guess to the secret number.

    Args:
        guess: The integer the player guessed.
        secret: The secret integer the player is trying to find.

    Returns:
        A 2-tuple ``(outcome, message)``:

        - ``outcome`` (str): One of ``"Win"``, ``"Too High"``, or
          ``"Too Low"``.
        - ``message`` (str): A short hint string shown to the player.

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(70, 50)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(30, 50)
        ('Too Low', '📈 Go HIGHER!')
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: Original code had "Go HIGHER!" and "Go LOWER!" swapped.
    # guess > secret means the player guessed too high, so they need to go lower.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(
    current_score: int,
    outcome: str,
    attempt_number: int,
) -> int:
    """Calculate the new score after a guess.

    Scoring rules:
    - **Win**: awards ``max(10, 100 - 10 * (attempt_number + 1))`` points.
    - **Too High** on an even attempt: +5 points (bonus for alternating strategy).
    - **Too High** on an odd attempt: -5 points.
    - **Too Low**: -5 points.
    - Any other outcome: score is unchanged.

    Args:
        current_score: The player's score before this guess.
        outcome: The outcome string returned by :func:`check_guess`.
        attempt_number: The 1-based attempt count for this guess.

    Returns:
        The updated integer score.

    Examples:
        >>> update_score(0, "Win", 1)
        70
        >>> update_score(50, "Too Low", 3)
        45
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
