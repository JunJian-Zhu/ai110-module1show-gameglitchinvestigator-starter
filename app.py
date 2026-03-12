import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []


# FEATURE (Challenge 4): hot/cold temperature label based on distance.
def _temperature_label(distance: int) -> str:
    """Return an emoji temperature label based on how close the guess is."""
    if distance <= 3:
        return "🔥 Burning Hot!"
    if distance <= 10:
        return "🌡️ Warm"
    if distance <= 25:
        return "❄️ Cold"
    return "🧊 Freezing!"


# FEATURE (Challenge 2): Guess History sidebar.
# Claude Code Agent was prompted: "Add a sidebar section that shows each guess,
# its outcome, and how far it was from the secret as a visual distance bar.
# Store history as dicts so we can display structured data without touching
# the core game logic functions."
st.sidebar.divider()
st.sidebar.subheader("Guess History")
if st.session_state.history:
    for i, entry in enumerate(st.session_state.history):
        guess = entry["guess"]
        outcome = entry["outcome"]
        distance = entry["distance"]

        if outcome == "Win":
            icon = "🎉"
            bar = ""
        elif outcome == "Too High":
            icon = "📉"
            closeness = max(0, 10 - min(distance // 5, 10))
            bar = "🔥" * closeness + "🧊" * (10 - closeness)
        else:
            icon = "📈"
            closeness = max(0, 10 - min(distance // 5, 10))
            bar = "🔥" * closeness + "🧊" * (10 - closeness)

        st.sidebar.write(f"**#{i + 1}** — {guess} {icon} _{outcome}_")
        if bar:
            st.sidebar.caption(bar)
else:
    st.sidebar.caption("No guesses yet.")

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts + 1}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # FIX: Original code only reset attempts and secret (hardcoded to 1-100).
    # Now fully resets all state and uses the current difficulty range.
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 1
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.rerun()

# FEATURE (Challenge 4): show session summary table when game ends.
if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

    valid_guesses = [
        e for e in st.session_state.history if e["outcome"] != "Invalid"
    ]
    if valid_guesses:
        st.subheader("Session Summary")
        rows = []
        for i, e in enumerate(valid_guesses):
            rows.append({
                "Attempt": i + 1,
                "Guess": e["guess"],
                "Outcome": e["outcome"],
                "Distance": e["distance"],
                "Temperature": _temperature_label(e["distance"]) if e["outcome"] != "Win" else "🎯 Exact!",
            })
        st.table(rows)
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append({"guess": raw_guess, "outcome": "Invalid", "distance": 0})
        st.error(err)
    else:
        # FIX: Original code cast secret to str on even attempts, causing lexicographic
        # comparison (e.g. "9" > "42" = True). Now always passes the integer secret.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        distance = abs(guess_int - st.session_state.secret)
        st.session_state.history.append({
            "guess": guess_int,
            "outcome": outcome,
            "distance": distance,
        })

        # FEATURE (Challenge 4): color-coded hints based on distance and outcome.
        if show_hint:
            temp = _temperature_label(distance)
            if outcome == "Win":
                st.success(f"{message}")
            elif distance <= 10:
                st.warning(f"{message}  {temp}")
            else:
                st.error(f"{message}  {temp}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
