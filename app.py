import re

import fitz  # PyMuPDF
import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 920px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }
        .quiz-hero {
            padding: 2.25rem 0 1.5rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.25);
            margin-bottom: 1.75rem;
        }
        .quiz-eyebrow {
            color: #2f9bf4;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }
        .quiz-hero h1 {
            font-size: 3.5rem;
            line-height: 1.05;
            margin: 0 0 0.9rem;
        }
        .quiz-hero p {
            color: rgba(180, 185, 195, 0.95);
            font-size: 1.15rem;
            line-height: 1.65;
            max-width: 620px;
            margin: 0;
        }
        .step-number {
            color: #2f9bf4;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .step-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0.3rem 0;
        }
        .step-copy {
            color: rgba(160, 165, 175, 0.95);
            font-size: 0.9rem;
            line-height: 1.5;
        }
        [data-testid="stFileUploader"] {
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 8px;
            padding: 0.6rem 1rem 1rem;
        }
        @media (max-width: 640px) {
            .block-container { padding-top: 1.25rem; }
            .quiz-hero h1 { font-size: 2.5rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
    return "\n".join(page.get_text("text", sort=True) for page in doc)


def parse_quiz_text(text):
    questions = []

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?m)^\s*Asia Pacific University.*?Database Security.*?\d+\s*$", "", text)
    text = re.sub(r"(?m)^\s*COMPREHENSIVE DATABASE SECURITY QUIZ\s*$", "", text)
    text = re.sub(r"(?m)^\s*Official Revision Bank.*$", "", text)
    text = re.sub(r"(?m)^\s*Module:.*$", "", text)
    text = re.sub(r"(?m)^\s*Scope:.*$", "", text)

    question_pattern = re.compile(
        r"(?ms)^\s*(\d{1,3})\.\s*(.*?)^\s*Answer\s*:\s*([A-D])\s*$"
    )

    for match in question_pattern.finditer(text):
        question_number = int(match.group(1))
        body = match.group(2).strip()
        correct_answer = match.group(3).upper()
        parts = re.split(r"(?m)^\s*([A-D])\.\s+", body)

        if len(parts) < 9:
            continue

        options = {}
        for i in range(1, len(parts), 2):
            letter = parts[i].upper()
            option_text = parts[i + 1] if i + 1 < len(parts) else ""
            options[letter] = " ".join(option_text.split())

        if all(letter in options for letter in ["A", "B", "C", "D"]):
            questions.append(
                {
                    "number": question_number,
                    "question": " ".join(parts[0].split()),
                    "options": {letter: options[letter] for letter in ["A", "B", "C", "D"]},
                    "answer": correct_answer,
                }
            )

    return questions


def reset_quiz():
    for key in [
        "questions",
        "quiz_started",
        "submitted",
        "current_index",
        "user_answers",
        "checked_questions",
        "answer_mode",
        "source_file",
        "exit_quiz_requested",
    ]:
        st.session_state.pop(key, None)

    for key in list(st.session_state):
        if key.startswith("answer_"):
            st.session_state.pop(key, None)


def start_quiz(questions, answer_mode, source_file):
    reset_quiz()
    st.session_state.questions = questions
    st.session_state.answer_mode = answer_mode
    st.session_state.source_file = source_file
    st.session_state.quiz_started = True
    st.session_state.submitted = False
    st.session_state.current_index = 0
    st.session_state.user_answers = {}
    st.session_state.checked_questions = set()
    st.session_state.exit_quiz_requested = False


def submit_quiz():
    st.session_state.submitted = True


def show_exit_confirmation():
    st.warning("Exit this quiz? Your current answers and progress will be cleared.")
    stay_col, exit_col = st.columns(2)

    with stay_col:
        if st.button("Keep answering", use_container_width=True):
            st.session_state.exit_quiz_requested = False
            st.rerun()

    with exit_col:
        if st.button("Exit to home", type="primary", use_container_width=True):
            reset_quiz()
            st.rerun()


def show_results():
    questions = st.session_state.questions
    answers = st.session_state.user_answers
    score = sum(
        answers.get(index) == question["answer"]
        for index, question in enumerate(questions)
    )

    st.title("Quiz results")
    st.metric("Final score", f"{score}/{len(questions)}")
    st.progress(score / len(questions))
    st.write(f"You scored **{(score / len(questions)) * 100:.1f}%**.")

    answered = len(answers)
    if answered < len(questions):
        st.warning(f"{len(questions) - answered} question(s) were left unanswered.")

    st.subheader("Answer review")
    for index, question in enumerate(questions):
        selected = answers.get(index)
        correct = question["answer"]
        is_correct = selected == correct

        with st.expander(
            f"Question {index + 1}: {'Correct' if is_correct else 'Incorrect'}",
            expanded=not is_correct,
        ):
            st.write(question["question"])
            if selected:
                st.write(f"**Your answer:** {selected}. {question['options'][selected]}")
            else:
                st.write("**Your answer:** Not answered")
            st.write(f"**Correct answer:** {correct}. {question['options'][correct]}")

    if st.button("Return to home", use_container_width=True):
        reset_quiz()
        st.rerun()


def show_question():
    questions = st.session_state.questions
    index = st.session_state.current_index
    question = questions[index]
    answer_mode = st.session_state.answer_mode
    checked = index in st.session_state.checked_questions

    heading_col, exit_col = st.columns([4, 1])
    with heading_col:
        st.caption(f"Question {index + 1} of {len(questions)}")
    with exit_col:
        if st.button("Exit quiz", use_container_width=True):
            st.session_state.exit_quiz_requested = True
            st.rerun()

    if st.session_state.get("exit_quiz_requested"):
        show_exit_confirmation()
        return

    st.progress((index + 1) / len(questions))
    st.subheader(f"Question {question['number']}")
    st.write(question["question"])

    selected = st.radio(
        "Choose your answer:",
        options=list(question["options"]),
        format_func=lambda letter: f"{letter}. {question['options'][letter]}",
        index=None,
        key=f"answer_{index}",
        disabled=checked and answer_mode == "Show answers after each question",
    )

    if selected is not None:
        st.session_state.user_answers[index] = selected

    if answer_mode == "Show answers after each question":
        if not checked:
            if st.button("Check answer", type="primary", disabled=selected is None):
                st.session_state.checked_questions.add(index)
                st.rerun()
        else:
            selected = st.session_state.user_answers.get(index)
            correct = question["answer"]
            if selected == correct:
                st.success(f"Correct. The answer is {correct}. {question['options'][correct]}")
            else:
                st.error(f"Incorrect. The correct answer is {correct}. {question['options'][correct]}")

    st.divider()
    previous_col, status_col, next_col = st.columns([1, 2, 1])

    with previous_col:
        if st.button("Previous", disabled=index == 0, use_container_width=True):
            st.session_state.current_index -= 1
            st.rerun()

    with status_col:
        answered = len(st.session_state.user_answers)
        st.markdown(
            f"<p style='text-align:center'>{answered} of {len(questions)} answered</p>",
            unsafe_allow_html=True,
        )

    can_continue = (
        answer_mode == "Show all answers at the end"
        or index in st.session_state.checked_questions
    )

    with next_col:
        if index < len(questions) - 1:
            if st.button("Next", disabled=not can_continue, use_container_width=True):
                st.session_state.current_index += 1
                st.rerun()
        elif st.button(
            "Submit quiz",
            type="primary",
            disabled=not can_continue,
            use_container_width=True,
        ):
            submit_quiz()
            st.rerun()

    if answer_mode == "Show all answers at the end":
        if st.button("Submit quiz now", use_container_width=True):
            submit_quiz()
            st.rerun()


st.set_page_config(page_title="PDF Quiz Maker", page_icon="Q", layout="centered")
apply_styles()

if st.session_state.get("submitted"):
    show_results()
elif st.session_state.get("quiz_started"):
    show_question()
else:
    st.markdown(
        """
        <section class="quiz-hero">
            <div class="quiz-eyebrow">A simpler way to revise</div>
            <h1>Quiz Maker</h1>
            <p>Turn a multiple-choice PDF into a focused, interactive quiz.
            Choose when to reveal answers and work through it one question at a time.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    step_one, step_two, step_three = st.columns(3)
    steps = [
        ("01", "Upload your PDF", "Use a text-based PDF with numbered questions and A-D answers."),
        ("02", "Choose your mode", "Learn with instant feedback or keep every answer hidden until the end."),
        ("03", "Start revising", "Move one question at a time and review your final result."),
    ]
    for column, (number, title, copy) in zip(
        [step_one, step_two, step_three], steps
    ):
        with column:
            st.markdown(
                f"""
                <div class="step-number">{number}</div>
                <div class="step-title">{title}</div>
                <div class="step-copy">{copy}</div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("Create a quiz")
    st.caption("Your PDF is processed for this quiz session and is not saved by the app.")

    uploaded_pdf = st.file_uploader("Upload your quiz PDF", type=["pdf"])

    if uploaded_pdf is not None:
        with st.spinner("Reading PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_pdf)
            questions = parse_quiz_text(extracted_text)

        if not questions:
            st.error(
                "No questions were detected. The PDF format may be different, "
                "or the PDF may be scanned."
            )
        else:
            st.success(f"Detected {len(questions)} questions.")
            answer_mode = st.radio(
                "When would you like to see the correct answers?",
                [
                    "Show answers after each question",
                    "Show all answers at the end",
                ],
                help=(
                    "Immediate mode checks and locks each answer before you continue. "
                    "End mode lets you move between questions and review everything after submission."
                ),
            )

            if st.button("Start quiz", type="primary", use_container_width=True):
                start_quiz(questions, answer_mode, uploaded_pdf.name)
                st.rerun()

            with st.expander("Preview extracted text"):
                st.text_area("Extracted PDF text", extracted_text, height=250)
