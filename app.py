import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="LearnLoop", page_icon="🎯", layout="wide")
DB = sqlite3.connect("learnloop_classroom.db", check_same_thread=False)
DB.execute("""CREATE TABLE IF NOT EXISTS attempts(
 id INTEGER PRIMARY KEY AUTOINCREMENT, student TEXT, topic TEXT,
 correct INTEGER, total INTEGER, created TEXT)""")
DB.execute("""CREATE TABLE IF NOT EXISTS assignments(
 id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT, topic TEXT,
 activity TEXT, created TEXT)""")
DB.commit()

TOPICS = ["Fractions", "Algebra", "Geometry"]
QUIZ = {
"Fractions":[
("What is 1/2 + 1/4?",["2/6","3/4","1/6","2/4"],"3/4","Use a common denominator: 2/4 + 1/4 = 3/4."),
("Which fraction equals 2/3?",["4/6","2/6","3/4","4/9"],"4/6","Multiply numerator and denominator by 2."),
("What is 3/5 of 20?",["8","10","12","15"],"12","20 ÷ 5 × 3 = 12."),
("Simplify 6/8.",["2/3","3/4","4/6","1/2"],"3/4","Divide numerator and denominator by 2."),
],
"Algebra":[
("Solve x + 5 = 12.",["5","7","12","17"],"7","Subtract 5 from both sides."),
("Simplify 3x + 2x.",["5","5x","6x","x"],"5x","Combine like terms."),
("If x = 4, what is 2x + 3?",["8","10","11","14"],"11","Substitute 4: 2 × 4 + 3 = 11."),
("Solve 2x = 18.",["6","8","9","16"],"9","Divide both sides by 2."),
],
"Geometry":[
("A triangle's interior angles total…",["90°","180°","270°","360°"],"180°","The interior angles of a triangle total 180°."),
("Area of a rectangle 6 by 4?",["10","20","24","28"],"24","Area = length × width."),
("How many sides does a hexagon have?",["5","6","7","8"],"6","A hexagon has six sides."),
("Perimeter of a square with side 5 cm?",["10 cm","15 cm","20 cm","25 cm"],"20 cm","Perimeter = 4 × side."),
]}

DEMO = ["Aarav","Diya","Kabir","Meera","Ishaan","Anaya","Rohan","Sara","Arjun"]
def attempts():
    return pd.read_sql_query("SELECT * FROM attempts ORDER BY id DESC", DB)
def scores():
    rows=[]
    hist=attempts()
    for name in DEMO:
        topic_scores={}
        for topic in TOPICS:
            d=hist[(hist.student==name)&(hist.topic==topic)].head(5)
            topic_scores[topic]=round(d.correct.sum()/d.total.sum()*100) if len(d) else None
        seen=[v for v in topic_scores.values() if v is not None]
        avg=round(sum(seen)/len(seen)) if seen else None
        weak=min((t for t in TOPICS if topic_scores[t] is not None),key=lambda t:topic_scores[t],default="Not assessed")
        if avg is None: group="Not assessed"
        elif avg < 50: group="Needs Support"
        elif avg < 80: group="Developing"
        else: group="Ready for Challenge"
        unseen=[t for t in TOPICS if topic_scores[t] is None]
        next_topic=unseen[0] if unseen else weak
        rows.append({"Student":name,**topic_scores,"Average mastery":avg,"Priority topic":next_topic,"Suggested group":group})
    return pd.DataFrame(rows)

st.sidebar.title("🎯 LearnLoop")
page=st.sidebar.radio("Workspace",["Teacher Dashboard","Student Learning","Group Activities","Class Insights"])
st.sidebar.caption("Teacher-led adaptive learning prototype")

if page=="Teacher Dashboard":
    st.title("Teacher Dashboard")
    st.write("A classroom overview for mixed-pace learning—not just individual quizzes.")
    df=scores()
    a,b,c,d=st.columns(4)
    a.metric("Students",len(df))
    b.metric("Assessed",int(df["Average mastery"].notna().sum()))
    c.metric("Needs support",int((df["Suggested group"]=="Needs Support").sum()))
    d.metric("Ready for challenge",int((df["Suggested group"]=="Ready for Challenge").sum()))
    avgs={t:round(df[t].dropna().mean()) if df[t].notna().any() else 0 for t in TOPICS}
    st.subheader("Average mastery by topic")
    st.bar_chart(pd.DataFrame({"Mastery (%)":avgs}))
    st.subheader("Class roster and flexible groups")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download class report CSV",df.to_csv(index=False),"learnloop_class_report.csv","text/csv")
    weakest=min(avgs,key=avgs.get)
    st.info(f"Teacher suggestion: consider a whole-class mini-lesson on {weakest}, then split practice by group.")

elif page=="Student Learning":
    st.title("Student Learning")
    st.write("Select a demo student and complete a topic check. Results update the teacher dashboard.")
    student=st.selectbox("Student",DEMO)
    row=scores().set_index("Student").loc[student]
    st.write(f"**Suggested group:** {row['Suggested group']}  ·  **Priority topic:** {row['Priority topic']}")
    group=row["Suggested group"]
    if group=="Needs Support": st.info("Suggested support: teacher-guided example and foundation worksheet.")
    elif group=="Developing": st.info("Suggested support: paired practice, hint card, then independent work.")
    elif group=="Ready for Challenge": st.info("Suggested activity: extension problem or explain-your-reasoning task.")
    topic=st.selectbox("Quiz topic",TOPICS,index=TOPICS.index(row["Priority topic"]) if row["Priority topic"] in TOPICS else 0)
    with st.form("quiz"):
        answers=[]
        for i,(q,opts,correct,why) in enumerate(QUIZ[topic]):
            answers.append(st.radio(f"{i+1}. {q}",opts,key=f"{student}-{topic}-{i}"))
        submit=st.form_submit_button("Submit quiz")
    if submit:
        correct_count=sum(a==item[2] for a,item in zip(answers,QUIZ[topic]))
        total=len(QUIZ[topic])
        DB.execute("INSERT INTO attempts(student,topic,correct,total,created) VALUES(?,?,?,?,?)",
                   (student,topic,correct_count,total,datetime.now().isoformat(timespec="seconds")))
        DB.commit()
        pct=round(correct_count/total*100)
        st.success(f"Score: {correct_count}/{total} ({pct}%).")
        for i,(answer,item) in enumerate(zip(answers,QUIZ[topic]),1):
            if answer!=item[2]: st.write(f"Question {i}: {item[2]}. {item[3]}")
        if pct<50: st.warning("Next step: reteach the concept, then use easier guided practice.")
        elif pct<80: st.info("Next step: targeted practice and a short retry.")
        else: st.success("Next step: challenge activity or peer explanation.")

elif page=="Group Activities":
    st.title("Flexible Learning Groups")
    st.write("Groups are suggestions based on recorded quiz mastery. Teachers can review and adjust them.")
    df=scores()
    for group in ["Needs Support","Developing","Ready for Challenge","Not assessed"]:
        subset=df[df["Suggested group"]==group]
        with st.expander(f"{group} ({len(subset)} students)",expanded=True):
            if subset.empty: st.write("No students currently in this group.")
            else:
                for _,r in subset.iterrows():
                    st.write(f"• {r['Student']} — next focus: {r['Priority topic']}")
    st.subheader("Assign a group activity")
    with st.form("assignment"):
        group=st.selectbox("Group",["Needs Support","Developing","Ready for Challenge","Not assessed"])
        topic=st.selectbox("Topic",TOPICS)
        activity=st.text_input("Activity",value="10-minute guided practice worksheet")
        save=st.form_submit_button("Save activity")
    if save:
        DB.execute("INSERT INTO assignments(group_name,topic,activity,created) VALUES(?,?,?,?)",
                   (group,topic,activity,datetime.now().isoformat(timespec="seconds")))
        DB.commit()
        st.success("Activity saved.")
    assigned=pd.read_sql_query('SELECT group_name AS "Group", topic AS "Topic", activity AS "Activity", created AS "Created" FROM assignments ORDER BY id DESC',DB)
    if not assigned.empty: st.dataframe(assigned,use_container_width=True,hide_index=True)

else:
    st.title("Class Insights & Blended Learning")
    df=scores()
    st.write("Use digital quiz evidence alongside teacher observation, discussion, and paper worksheets.")
    for topic in TOPICS:
        vals=df[topic].dropna()
        avg=round(vals.mean()) if len(vals) else 0
        st.write(f"**{topic}:** class mastery {avg}%")
        st.progress(avg/100)
    st.subheader("Suggested lesson flow")
    st.markdown("""
    1. **Whole-class mini-lesson:** address the most common misconception.
    2. **Needs Support:** teacher-guided worked example and printed step-by-step worksheet.
    3. **Developing:** pair practice with hints, followed by independent questions.
    4. **Ready for Challenge:** extension task and peer explanation.
    5. **Exit ticket:** one short question to update mastery and regroup flexibly.
    """)
    st.subheader("How grouping works")
    st.write("Prototype heuristic: average recorded topic mastery below 50% → Needs Support; 50–79% → Developing; 80% or higher → Ready for Challenge; no attempts → Not assessed.")
    st.warning("Groups are provisional suggestions, not fixed labels or validated measures of ability. Teachers should review them and regroup students as they progress. Demo student names are fictional.")
