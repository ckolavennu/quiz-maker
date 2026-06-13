import re
import fitz  # PyMuPDF
import streamlit as st


def extract_text_from_pdf(uploaded_file):
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text("text", sort=True) + "\n"

    return text

def parse_quiz_text(text):
    questions = []

    # Normalize PDF text
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove common header/footer noise
    text = re.sub(r"(?m)^\s*Asia Pacific University.*?Database Security.*?\d+\s*$", "", text)
    text = re.sub(r"(?m)^\s*COMPREHENSIVE DATABASE SECURITY QUIZ\s*$", "", text)
    text = re.sub(r"(?m)^\s*Official Revision Bank.*$", "", text)
    text = re.sub(r"(?m)^\s*Module:.*$", "", text)
    text = re.sub(r"(?m)^\s*Scope:.*$", "", text)

    # Find each question block up to its Answer line
    question_pattern = re.compile(
        r"(?ms)^\s*(\d{1,3})\.\s*(.*?)^\s*Answer\s*:\s*([A-D])\s*$"
    )

    for match in question_pattern.finditer(text):
        question_number = int(match.group(1))
        body = match.group(2).strip()
        correct_answer = match.group(3).upper()

        # Split into question text and options.
        # This allows spaces before A. B. C. D.
        parts = re.split(r"(?m)^\s*([A-D])\.\s+", body)

        if len(parts) < 9:
            continue

        question_text = " ".join(parts[0].split())

        options = {}

        for i in range(1, len(parts), 2):
            letter = parts[i].upper()
            option_text = parts[i + 1] if i + 1 < len(parts) else ""
            options[letter] = " ".join(option_text.split())

        if all(letter in options for letter in ["A", "B", "C", "D"]):
            questions.append({
                "number": question_number,
                "question": question_text,
                "options": {
                    "A": options["A"],
                    "B": options["B"],
                    "C": options["C"],
                    "D": options["D"],
                },
                "answer": correct_answer
            })

    return questions

st.set_page_config(
    page_title="PDF Quiz Interface",
    page_icon="📝",
    layout="centered"
)

st.title("📝 PDF Quiz Generator")
st.write("Upload a quiz PDF and turn it into an interactive quiz interface.")

uploaded_pdf = st.file_uploader("Upload your quiz PDF", type=["pdf"])

if uploaded_pdf is not None:
    with st.spinner("Reading PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_pdf)

    st.success("PDF text extracted successfully.")

    with st.expander("Preview extracted text"):
        st.text_area("Extracted PDF Text", extracted_text, height=250)

    questions = parse_quiz_text(extracted_text)

    if not questions:
        st.error(
            "No questions detected. The PDF format may be different, "
            "or the PDF may be scanned/image-based."
        )
    else:
        st.subheader(f"Quiz Generated: {len(questions)} questions")

        user_answers = {}

        with st.form("quiz_form"):
            for i, q in enumerate(questions, start=1):
                st.markdown(f"### Question {i}")
                st.write(q["question"])

                option_labels = [
                    f"{letter}. {text}"
                    for letter, text in q["options"].items()
                ]

                selected = st.radio(
                    label="Choose your answer:",
                    options=option_labels,
                    key=f"q_{i}"
                )

                selected_letter = selected.split(".")[0]
                user_answers[i] = selected_letter

            submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            score = 0
            total_gradable = 0

            st.subheader("Results")

            for i, q in enumerate(questions, start=1):
                correct = q["answer"]
                selected = user_answers[i]

                if correct is None:
                    st.info(f"Question {i}: Answer key not found in PDF.")
                    continue

                total_gradable += 1

                if selected == correct:
                    score += 1
                    st.success(f"Question {i}: Correct")
                else:
                    st.error(f"Question {i}: Wrong. Correct answer: {correct}")

            if total_gradable > 0:
                st.markdown(f"## Final Score: {score}/{total_gradable}")
            else:
                st.warning("No answer key found, so the quiz could not be auto-graded.")