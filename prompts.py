def get_prompt(mode, text):
    if mode == "Summary":
        return f"""Summarize the following academic text using 5–10 concise bullet points. 
Focus on key concepts, definitions, and any important relationships.

Academic content:
{text}
"""

    elif mode == "Flashcards":
        return f"""Create as many flashcards as appropriate from the academic content below. 
Each flashcard should contain:
- A "question"
- Its corresponding "answer"

Return the flashcards as a JSON list like this:
[
  {{
    "question": "What is ...?",
    "answer": "..."
  }}
]
Ensure each flashcard covers a unique, important point. Skip obvious or repeated facts.


Academic content:
{text}
"""

    elif mode == "Quiz":
        return f"""Create as many multiple-choice questions as appropriate for the following academic content (minimum 3, maximum 10).
 
For each question, include:
- "question" : the question string
- "options" : a list of 4 answer choices (A-D))
- "answer" : the correct option letter: "A", "B", "C", or "D"

Return the output as a JSON list like this:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "answer": "B"
  }},
  ...
]

Academic content:
{text}
"""
