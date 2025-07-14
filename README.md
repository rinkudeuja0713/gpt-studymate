# 🎓 GPT StudyMate

**GPT StudyMate** is an academic assistant web app that helps students turn their lecture notes into helpful study materials like summaries, flashcards, and quizzes — powered by GPT-3.5.

---

## Features

- 📄 **Text or File Input**: Paste lecture notes or upload `.txt` / `.pdf` files.
-  **3 Modes**:
  - **Summary**: Condensed bullet-point overview.
  - **Flashcards**: Q&A cards for concept recall.
  - **Quiz**: Multiple choice questions with instant feedback.
- 💬 **LLM-Powered Output**: Uses GPT-3.5 via OpenAI API (or fallback mock mode).
- 🧪 **Evaluation Loop**: Built-in feedback system for refining prompt quality.
- 📥 **Export**: Download outputs as `.txt` files for reuse.
- 🔄 **Regenerate**: Retry for alternate GPT output.

---

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM Backend**: [OpenAI GPT-3.5](https://platform.openai.com/)
- **PDF Parsing**: `PyPDF2`
- **Feedback Storage**: Local JSON
- **Prompt Engineering**: Custom prompt templates in `prompts.py`

---

##  Sample Use Cases

- Studying lecture notes on AI, NLP, or programming
- Turning class PDFs into flashcards before exams
- Quickly generating self-assessment quizzes

---

##  File Structure
gpt-studymate/
├── app.py
├── prompts.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│ └── secrets.toml # Add your OpenAI API key here (not included in repo)
└── README.md


