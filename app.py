import streamlit as st
from prompts import get_prompt
import json
import openai  # Reserved for Phase 3 (real API testing)
import os
import PyPDF2 


# Use mock outputs (toggle to False when using real GPT API) 
USE_MOCK = st.sidebar.checkbox("Use Mock Outputs", value=False, help="Toggle to use mock data instead of real API calls.")

# Streamlit UI
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #f0f4ff, #ffffff);
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.set_page_config(page_title="GPT StudyMate", page_icon="🎓")
st.markdown("<h1 style='color:#4A90E2;'>🎓 GPT StudyMate</h1>", unsafe_allow_html=True)
st.caption("Your academic assistant for smart summaries, flashcards, and quizzes.")

# User Input 
uploaded_file = st.file_uploader("📥 Upload lecture notes (PDF or text file):", type=["pdf", "txt"])
text_input = ""

#Handle uploaded file or fallback to paste
if uploaded_file:
    if uploaded_file.type == "text/plain":
        text_input = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text_input = ""
        for page in pdf_reader.pages:
            text_input += page.extract_text()
        st.success(f"✅ Extracted text from {len(pdf_reader.pages)} pages.")
else:
    text_input = st.text_area("📄 Or paste your notes manually:", height=200)

# Limit character count after loading text to prevent token overuse.
MAX_CHARS = 4000
if len(text_input) > MAX_CHARS:
    st.warning(f"⚠️ Your input is long. Only the first {MAX_CHARS} characters will be processed.")
    text_input = text_input[:MAX_CHARS]

mode = st.selectbox("Select output type:", ["Summary", "Flashcards", "Quiz"])

# Mock Data Function 
def get_mock_response(mode):
    if mode == "Summary":
        return """📝**Mock Summary:**
- AI simulates human intelligence.
- It handles tasks like decision-making and language understanding.
- AI includes subfields like machine learning and NLP. 
- Machine learning improves from data.
- NLP allows understanding of human language."""

    elif mode == "Flashcards":
        return json.dumps([
            {"question": "What is AI?", "answer": "Simulation of human intelligence in machines"},
            {"question": "Name one subfield of AI.", "answer": "Machine Learning"},
            {"question": "What does NLP stand for?", "answer": "Natural Language Processing"},
            {"question": "What does machine learning use to improve?", "answer": "Data"},
            {"question": "What is the goal of AI?", "answer": "To mimic human reasoning and tasks"}
        ])

    elif mode == "Quiz":
        return json.dumps([
            {
                "question": "What is AI?",
                "options": ["A fruit", "A spreadsheet", "Simulation of human intelligence", "A robot"],
                "answer": "C"
            },
            {
                "question": "Which of these is a subfield of AI?",
                "options": ["Botany", "Machine Learning", "History", "Chemistry"],
                "answer": "B"
            },
            {
                "question": "What does NLP help machines do?",
                "options": ["Fly", "Cook", "Understand human language", "Sleep"],
                "answer": "C"
            }
        ])

# GPT Response Fetch (Mock or Real) 
def fetch_output(mode, text_input):
    prompt = get_prompt(mode, text_input)

    if USE_MOCK:
        return get_mock_response(mode)
    else:
        try:
            client = openai.OpenAI(api_key= st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw_output = response.choices[0].message.content.strip()

            # Clean output: Try to extract just the JSON part if extra text exists
            if mode in ["Flashcards", "Quiz"]:
                json_start = raw_output.find("[")
                json_end = raw_output.rfind("]") + 1
                raw_output = raw_output[json_start:json_end]

            return raw_output
        except Exception as e:
            return f"❌ Error: {str(e)}\n\nShowing mock output instead:\n\n" + get_mock_response(mode)

# --- Display Flashcards ---
def render_flashcards(json_data):
    st.subheader("📝 Flashcards:")
    try:
        cards = json.loads(json_data)
        if not isinstance(cards, list):
            raise ValueError("Flashcards not returned as a list.")
        for i, card in enumerate(cards):
            with st.expander(f"Flashcard {i+1}: {card.get('question', 'No question')}"):
                st.write(f"**Answer:** {card.get('answer', 'No answer')}")
    except Exception as e:
        st.error("⚠️ Could not display flashcards. The output format may be incorrect.")
        st.text_area("Raw Output:", json_data, height=200)


# --- Display Quiz ---
def render_quiz(json_data):
    st.subheader("📝 Quiz:")
    try:
        questions = json.loads(json_data)
        if not isinstance(questions, list):
            raise ValueError("Quiz data not returned as a list")
    except Exception as e:
        st.error("⚠️ Could not display quiz. The output format may be incorrect.")
        st.text_area("Raw Output:", json_data, height=250)
        return
    
    # Initialize session state for answers and submission
    if "selected_answers" not in st.session_state or "quiz_length" not in st.session_state or st.session_state.quiz_length != len(questions):
        st.session_state.selected_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.quiz_length = len(questions)

    for i, q in enumerate(questions):
        st.markdown(f"**{i+1}. {q.get('question', 'Missing question text')}**")
        
        option_keys = ["", "A", "B", "C", "D"]
        option_labels = ["Select an answer:"]+[
            f"{label}.{q['options'][i]}" for i, label in enumerate(["A", "B", "C", "D"])
        ]

        if not st.session_state.quiz_submitted:
            selected = st.radio(
                "",
                option_keys,
                format_func=lambda x: option_labels[option_keys.index(x)],
                key=f"radio_{i}",
                index=option_keys.index(st.session_state.selected_answers.get(i, "")) if i in st.session_state.selected_answers else 0
            )
            st.session_state.selected_answers[i] = selected
        else:
            selected = st.session_state.selected_answers.get(i, "")
            selected_index = option_keys.index(selected) if selected in option_keys else -1
            selected_text = option_labels[selected_index] if selected_index >= 0 else "Not answered"
            st.markdown(f"**Your answer:** {selected_text}")

            correct = q["answer"]
            correct_index = option_keys.index(correct)
            correct_text = option_labels[correct_index]
            if selected == correct:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct answer: {correct_text}")

        st.markdown("---")

    if not st.session_state.quiz_submitted:
        if st.button("📩 Submit Quiz"):
            st.session_state.quiz_submitted = True

# helper functionto collect feedback
def collect_feedback(mode, output):
    st.markdown("### 📋 Was this output helpful?")
    feedback = st.radio("Your feedback:", ["👍 Yes", "👎 No"], key=f"feedback_{mode}")
    comment  = st.text_input("Any comments or suggestions?", key=f"comment_{mode}")

    if st.button("Submit Feedback", key=f"submit_{mode}"):
        data = {
            "mode": mode,
            "feedback": feedback,
            "comment": comment,
            "output_snippet": output[:200]  # just store a snippet
        }

        if not os.path.exists("feedback.json"):
            with open("feedback.json", "w") as f:
                json.dump([data], f, indent=2)
        else:
            with open("feedback.json", "r+") as f:
                existing = json.load(f)
                existing.append(data)
                f.seek(0)
                json.dump(existing, f, indent=2)

        st.success("✅ Feedback submitted. Thank you!")

if st.button("🔁 Regenerate Output"):
    st.session_state.show_quiz = False
    st.rerun()

# exporting output files
def render_export_button(mode, output):
    st.markdown("### ⬇️ Export Output")

    if mode == "Summary":
        # Export summary as plain .txt
        st.download_button(
            label="Download Summary",
            data=output,
            file_name="summary.txt",
            mime="text/plain"
        )

    elif mode == "Flashcards":
        try:
            cards = json.loads(output)
            # Build pretty .txt version
            text_output = "\n\n".join([f"Q: {c['question']}\nA: {c['answer']}" for c in cards])

            st.download_button(
                label="Download Flashcards",
                data=text_output,
                file_name="flashcards.txt",
                mime="text/plain"
            )
        except:
            st.warning("⚠️ Could not generate flashcard files.")

    elif mode == "Quiz":
        try:
            questions = json.loads(output)
            # Build pretty .txt version
            text_output = ""
            for i, q in enumerate(questions):
                text_output += f"{i+1}. {q['question']}\n"
                text_output += f"   A. {q['options'][0]}\n"
                text_output += f"   B. {q['options'][1]}\n"
                text_output += f"   C. {q['options'][2]}\n"
                text_output += f"   D. {q['options'][3]}\n"
                text_output += f"   Answer: {q['answer']}\n\n"

            st.download_button(
                label="Download Quiz",
                data=text_output,
                file_name="quiz.txt",
                mime="text/plain"
            )
        except:
            st.warning("⚠️ Could not generate quiz files.")


# --- Output Trigger ---
if st.button("🚀 Generate"):
    if not text_input.strip():
        st.warning("Please paste your notes first.")
        st.session_state.show_quiz = False
    else:
        with st.spinner("Generating output..."):
            output = fetch_output(mode, text_input)
        st.session_state.generated_output = output
        st.session_state.generated_mode = mode
        st.session_state.show_quiz = True

# Always show output if generated
if st.session_state.get("show_quiz", False):
    output = st.session_state.get("generated_output", "")
    mode = st.session_state.get("generated_mode", "")
    if mode == "Summary":
        st.subheader("📝 Summary:")
        st.markdown(output)
        collect_feedback("summary", output)
        render_export_button("Summary", output)
    elif mode == "Flashcards":
        render_flashcards(output)
        collect_feedback("flashcards", output)
        render_export_button("Flashcards", output)
    elif mode == "Quiz":
        render_quiz(output)
        collect_feedback("quiz", output)
        render_export_button("Quiz", output)

   