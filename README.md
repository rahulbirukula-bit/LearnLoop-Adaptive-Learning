# LearnLoop — Teacher-Centered Adaptive Learning

## Features
- Teacher dashboard and class roster
- Topic-level mastery and learning gaps
- Suggested flexible groups: Needs Support, Developing, Ready for Challenge
- Student quiz with explanations and follow-up recommendations
- Teacher-created group activities
- Blended learning plan using digital quizzes and printable worksheets
- CSV class report and SQLite persistence

## Run on Windows
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```
Then open http://localhost:8501.

## Demo flow
1. Teacher Dashboard: show class overview and topic averages.
2. Student Learning: select a fictional student and take a quiz.
3. Teacher Dashboard: show updated mastery and group suggestion.
4. Group Activities: assign a worksheet to a group.
5. Class Insights: explain the blended lesson plan.

## Limitations
- The demo roster is fictional.
- Group thresholds are illustrative rules, not a validated assessment.
- Teachers should review group suggestions; groups must remain flexible.
- Authentication and production privacy controls are not implemented.
