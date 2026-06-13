# Quiz Maker

Quiz Maker is a small Streamlit app that turns a PDF containing multiple-choice questions into an interactive quiz.

I originally built this because I had a long revision PDF containing 100 questions. Constantly scrolling through the PDF while trying not to accidentally look at the answers was not a great way to revise. I wanted something that felt more like an actual quiz, where I could answer one question at a time and receive a score at the end.

**Live app:** https://ck-quiz-maker.streamlit.app

## What It Does

Upload a supported quiz PDF and the app will:

* Extract the questions, answer choices, and correct answers
* Display one question at a time
* Keep track of your selected answers
* Show your progress throughout the quiz
* Allow you to move between questions
* Calculate your final score and percentage
* Show a complete answer review after submission

## Answer Review Modes

Before starting the quiz, you can choose when you want to see the answers.

### Show Answers After Each Question

Your answer is checked immediately. Once checked, the answer is locked before you continue to the next question.

This mode is useful when learning or revising a topic.

### Show All Answers at the End

You can freely move between questions and change your answers. The correct answers are only shown after submitting the quiz.

This mode is better when testing yourself under exam-style conditions.

## Supported PDF Format

The app currently works best with text-based PDFs formatted like this:

```text
1. What is the capital of Malaysia?
A. Bangkok
B. Kuala Lumpur
C. Jakarta
D. Singapore
Answer: B
```

Questions may span multiple lines, but each question should contain:

* A question number
* Four options labelled `A.` to `D.`
* An answer line formatted as `Answer: A`

Scanned or image-based PDFs are not currently supported.

## Running the App Locally

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

If the `streamlit` command is not recognised, use:

```bash
python -m streamlit run app.py
```

## Built With

* Python
* Streamlit
* PyMuPDF

## Current Limitations

Quiz Maker is still an early version. Its PDF parser expects a fairly specific question format, so PDFs with differently labelled options or missing answer keys may not work correctly.

The app also does not currently support scanned PDFs, user accounts, saved quiz history, or custom question editing.

## Ideas for Future Improvements

* Select how many questions to attempt
* Shuffle questions and answer choices
* Flag questions for review
* Retry only incorrectly answered questions
* Add a question preview and editing screen
* Support scanned PDFs using OCR
* Support more quiz formats

## About This Project

This project started as a simple tool to make revising from large quiz PDFs less frustrating. It is also an opportunity for me to practise building useful applications with Python and gradually improve them based on real use.
