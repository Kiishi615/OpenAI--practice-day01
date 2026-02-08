import requests
import streamlit as st
import html
import random
from streamlit_lottie import st_lottie


def load_lottie_url(url):
    """Load Lottie animation from URL"""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


st.set_page_config(page_title="Trivia Night 🔥", page_icon="🪇")

st.title("🪇 Trivia Night!!!!")
st.write("Test your knowledge with random trivia questions!")

# Sidebar controls
st.sidebar.header("Game Settings")
difficulty = st.sidebar.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
amount = st.sidebar.slider("Number of questions", 1, 10, 5)

# Initialize ALL session state variables
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "scored" not in st.session_state:
    st.session_state.scored = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False


if st.sidebar.button("🚀 Start New Game", type="primary"):
    with st.spinner("Fetching fresh questions..."):
        url = "https://opentdb.com/api.php"
        params = {
            "amount": amount,
            "difficulty": difficulty,
            "type": "multiple"
            # Removed "encode": "url" - default works better with html.unescape()
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data["response_code"] == 0:
                questions = []
                for q in data["results"]:
                    question_text = html.unescape(q["question"])
                    correct = html.unescape(q["correct_answer"])
                    incorrect = [html.unescape(ans) for ans in q["incorrect_answers"]]
                    all_answers = incorrect + [correct]
                    random.shuffle(all_answers)
                    questions.append({
                        "question": question_text,
                        "options": all_answers,
                        "correct": correct
                    })
                
                # Reset all game state
                st.session_state.questions = questions
                st.session_state.current_idx = 0
                st.session_state.score = 0
                st.session_state.answers = {}
                st.session_state.scored = []
                st.session_state.game_started = True
                st.session_state.game_over = False
                st.session_state.submitted = False
                st.rerun()
            else:
                st.error("Failed to fetch questions. Try again!")
        except Exception as e:
            st.error(f"Connection error: {e}")


# Main game logic - only show if game started and NOT over
if st.session_state.game_started and not st.session_state.game_over and st.session_state.questions:
    q = st.session_state.questions[st.session_state.current_idx]
    total = len(st.session_state.questions)
    
    # Fixed progress calculation
    progress = (st.session_state.current_idx + 1) / total

    st.write(f"### Question {st.session_state.current_idx + 1} of {total}")
    st.progress(progress)
    st.markdown(f"**{q['question']}**")

    # Disable radio after submission
    user_answer = st.radio(
        "Choose your answer:",
        options=q["options"],
        key=f"q_{st.session_state.current_idx}",
        index=None,
        disabled=st.session_state.submitted
    )

    col1, col2 = st.columns(2)
    
    with col1:
        submit_disabled = st.session_state.submitted or user_answer is None
        if st.button("Submit Answer", type="primary", use_container_width=True, disabled=st.session_state.submitted):
            if user_answer is None:
                st.warning("Please select an answer!")
            else:
                st.session_state.answers[st.session_state.current_idx] = user_answer
                st.session_state.submitted = True
                
                # Score the answer
                if user_answer == q["correct"]:
                    if st.session_state.current_idx not in st.session_state.scored:
                        st.session_state.score += 1
                        st.session_state.scored.append(st.session_state.current_idx)
                st.rerun()

    # Show feedback after submission
    if st.session_state.submitted:
        stored_answer = st.session_state.answers.get(st.session_state.current_idx)
        if stored_answer == q["correct"]:
            st.success("✅ Correct!")
            st.balloons()
        else:
            st.error(f"❌ Wrong! The correct answer was: **{q['correct']}**")

    with col2:
        if st.session_state.submitted:
            if st.session_state.current_idx < total - 1:
                if st.button("Next Question ➡️", use_container_width=True):
                    st.session_state.current_idx += 1
                    st.session_state.submitted = False
                    st.rerun()
            else:
                if st.button("Finish Game 🏁", use_container_width=True, type="primary"):
                    st.session_state.game_over = True
                    st.rerun()

    # Show current score
    answered = len(st.session_state.answers)
    st.caption(f"Score: **{st.session_state.score} / {answered}**")


# Game Over Screen
elif st.session_state.game_over and st.session_state.questions:
    st.balloons()
    total = len(st.session_state.questions)
    
    st.success(f"### 🎉 Game Over! Final Score: {st.session_state.score}/{total}")
    
    accuracy = (st.session_state.score / total) * 100
    
    if accuracy == 100:
        st.markdown("## 🏆 PERFECT SCORE! YOU'RE A GENIUS! 🧠✨")
    elif accuracy >= 80:
        st.markdown("## 🌟 Amazing performance!")
    elif accuracy >= 60:
        st.markdown("## 👍 Not bad at all!")
    else:
        st.markdown("## 💪 Keep practicing!")

    st.divider()
    
    if st.button("🎯 Play Again", type="primary", use_container_width=True):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# Welcome screen - when no game is active
elif not st.session_state.game_started and not st.session_state.game_over:
    st.info("👈 Adjust settings and click **Start New Game** to begin!")
    
    # Fixed: Use load_lottie_url() then st_lottie()
    lottie_url = "https://lottie.host/0458c86c-2b3a-4338-8806-277b589a7ed0/OdFDxKZL3A.json"
    lottie_animation = load_lottie_url(lottie_url)
    
    if lottie_animation:
        st_lottie(lottie_animation, height=300, key="welcome_animation")
    else:
        # Fallback if lottie fails to load
        st.markdown("### 🎮 Ready to test your knowledge?")