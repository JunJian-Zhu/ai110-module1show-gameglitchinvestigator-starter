# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, it appeared to work but the behavior was clearly wrong. The most obvious bug was that the hints were backwards: if I guessed too high, the game told me to go higher, and if I guessed too low, it told me to go lower. The second bug was subtler: on every even-numbered attempt, the secret number was silently converted to a string before being compared to my integer guess, which caused the comparison to use lexicographic ordering instead of numeric ordering, making the hints randomly incorrect. The "New Game" button also failed to fully reset the game. It left the old score, status, and history in place, and used a hardcoded range of 1–100 regardless of the selected difficulty.

---

## 2. How did you use AI as a teammate?

I used Claude Code as my primary AI tool throughout this project. For the Higher/Lower logic bug, I asked Claude to explain why the hints felt backwards, and it correctly identified that the return values in `check_guess` were swapped — `guess > secret` was returning "Go HIGHER!" when it should return "Go LOWER!". I verified this by manually tracing through the function with a concrete example (guess = 70, secret = 50) and confirming the fix made the output match the expected behavior. One area where I had to push back was the state bug explanation: the AI's first instinct was to point only at the `if "secret" not in st.session_state` guard, but the real culprit was the even/odd string-conversion block a few lines lower, which I found by reading the submit handler more carefully myself.

---

## 3. Debugging and testing your fixes

I decided a bug was fixed when I could reproduce the original bad behavior, apply the fix, and confirm the output changed to what I expected. For the `check_guess` logic, I tested it directly in a Python shell: I called `check_guess(70, 50)` before and after the fix and compared the returned message — before the fix it said "Go HIGHER!" (wrong), after the fix it correctly said "Go LOWER!". I also tested the string-conversion bug by calling `check_guess(9, "42")` to simulate the even-attempt path, which returned "Too Low" because `"9" > "42"` is True in Python string comparison — this confirmed why hints were unreliable. Claude helped me understand that Python's `>` operator on mixed int/str types raises a `TypeError` in Python, which explained why the original `try/except TypeError` block existed, but it was masking the real problem rather than fixing it.

---

## 4. What did you learn about Streamlit and state?

The secret number appeared to change because on even-numbered attempts, the code converted it to a string before comparing — so the comparison result was based on string ordering, not the actual number. For example, if the secret was 5 and I guessed 20, string comparison says `"20" < "5"` (because "2" < "5"), so the game incorrectly reported my guess as too low. To explain Streamlit to a friend: every time you interact with the app (click a button, type in a box), Streamlit reruns the entire Python script from top to bottom — like refreshing a page. Without `st.session_state`, every variable would reset to its initial value on each rerun. `st.session_state` is a dictionary that persists across these reruns, so values stored in it survive the page refresh. The fix that made the secret stable was removing the even/odd type-casting block entirely and always passing `st.session_state.secret` (an integer) directly to `check_guess`.

---

## 5. Looking ahead: your developer habits

One habit I want to carry forward is reading the full function before trusting an AI explanation — the string-conversion bug was hidden a few lines away from where I initially looked, and skimming would have missed it. Next time I work with AI on a coding task, I would give it the actual buggy code up front rather than describing the behavior in words, because the AI caught the logic issues much faster once it could see the exact lines. This project changed how I think about AI-generated code: it's not wrong in obvious ways, it's wrong in plausible-looking ways that pass a quick glance, which means I need to test edge cases and read the logic carefully rather than assume it works because it looks reasonable.
