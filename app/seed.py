from datetime import datetime

from app.extensions import db
from app.models import User, Course, TimetableEvent, Exam, RevisionTopic, StudyGroup, GroupMember, GroupTask, GroupMessage, DirectMessage, Reminder, HandbookSubject


def seed_demo_data():
    existing_user = User.query.filter_by(email="you@student.uwa.edu.au").first()

    if existing_user:
        print("Demo data already exists. Skipping seed.")
        return

    jane = User(
        full_name="Jane Smith",
        email="you@student.uwa.edu.au",
        uwa_id="23456789",
        program="Master of Information Technology",
        bio="StudySync demo user.",
        skills="Flask, HTML, CSS, JavaScript, SQLAlchemy",
        availability="Weekdays after 2 PM",
        avatar_colour="purple"
    )
    jane.set_password("password123")

    tom = User(full_name="Tom Liu", email="tom@student.uwa.edu.au", uwa_id="23112233", program="Bachelor of Computer Science", skills="Frontend, JavaScript", availability="Monday afternoon", avatar_colour="orange")
    tom.set_password("password123")

    amy = User(full_name="Amy Kim", email="amy@student.uwa.edu.au", uwa_id="23884455", program="Master of Data Science", skills="Planning, testing", availability="Tuesday evening", avatar_colour="violet")
    amy.set_password("password123")

    ryan = User(full_name="Ryan Zhang", email="ryan@student.uwa.edu.au", uwa_id="23990011", program="Master of Information Technology", skills="AI UI, testing", availability="Friday afternoon", avatar_colour="blue")
    ryan.set_password("password123")

    db.session.add_all([jane, tom, amy, ryan])
    db.session.flush()

    cits3403 = Course(code="CITS3403", title="Agile Web Development", description="Client-server web application development using Flask.", owner_id=jane.id)
    cits4009 = Course(code="CITS4009", title="Fundamentals of Data Science", description="Data analysis and modelling.", owner_id=jane.id)
    math2004 = Course(code="MATH2004", title="Linear Algebra", description="Matrices and vectors.", owner_id=jane.id)

    db.session.add_all([cits3403, cits4009, math2004])
    db.session.flush()

    events = [
        TimetableEvent(title="CITS3403 Laboratory", event_type="Laboratory", location="Lab 106", start_time=datetime(2026, 4, 14, 9, 0), end_time=datetime(2026, 4, 14, 10, 0), owner_id=jane.id, course_id=cits3403.id, is_group_event=True),
        TimetableEvent(title="CITS3403 Lecture", event_type="Lecture", location="LT 225", start_time=datetime(2026, 4, 15, 9, 0), end_time=datetime(2026, 4, 15, 10, 0), owner_id=jane.id, course_id=cits3403.id),
        TimetableEvent(title="MATH2004 Lecture", event_type="Lecture", location="LT 120", start_time=datetime(2026, 4, 16, 9, 0), end_time=datetime(2026, 4, 16, 10, 0), owner_id=jane.id, course_id=math2004.id)
    ]
    db.session.add_all(events)

    exam = Exam(title="CITS3403 Mid-semester Test", exam_date=datetime(2026, 4, 15, 10, 0), location="Room 106", weight_percent=20, owner_id=jane.id, course_id=cits3403.id)
    db.session.add(exam)
    db.session.flush()

    topics = [
        RevisionTopic(name="HTML semantic elements and forms", progress=100, status="Done", exam_id=exam.id),
        RevisionTopic(name="CSS flexbox and grid layout", progress=100, status="Done", exam_id=exam.id),
        RevisionTopic(name="JavaScript event listeners and DOM manipulation", progress=65, status="In Progress", exam_id=exam.id),
        RevisionTopic(name="Flask routes and Jinja templates", progress=30, status="Not Started", exam_id=exam.id),
        RevisionTopic(name="SQLAlchemy models and relationships", progress=10, status="Not Started", exam_id=exam.id)
    ]
    db.session.add_all(topics)

    group = StudyGroup(name="CITS3403 Group 7", group_code="GRP-3403-07", description="Group project team for StudySync.")
    db.session.add(group)
    db.session.flush()

    members = [
        GroupMember(user_id=jane.id, group_id=group.id, role="Lead", status="Online"),
        GroupMember(user_id=tom.id, group_id=group.id, role="Frontend", status="Online"),
        GroupMember(user_id=amy.id, group_id=group.id, role="Planner", status="Last seen 1h ago"),
        GroupMember(user_id=ryan.id, group_id=group.id, role="AI UI", status="Online")
    ]
    db.session.add_all(members)

    tasks = [
        GroupTask(title="Login and register pages", status="Done", assigned_to_id=jane.id, group_id=group.id),
        GroupTask(title="Timetable grid component", status="In Progress", assigned_to_id=tom.id, group_id=group.id),
        GroupTask(title="User stories and page list document", status="Done", assigned_to_id=amy.id, group_id=group.id),
        GroupTask(title="AI planner chat UI", status="Not Started", assigned_to_id=ryan.id, group_id=group.id)
    ]
    db.session.add_all(tasks)

    messages = [
        GroupMessage(body="Morning team! I uploaded the user stories for Checkpoint 2.", sender_id=amy.id, group_id=group.id),
        GroupMessage(body="Great. I am working on the timetable UI.", sender_id=tom.id, group_id=group.id),
        GroupMessage(body="I will connect the Flask routes and database models.", sender_id=jane.id, group_id=group.id)
    ]
    db.session.add_all(messages)

    db.session.add(DirectMessage(body="Can you review the timetable branch later?", sender_id=tom.id, receiver_id=jane.id))

    reminders = [
        Reminder(title="Review Flask routes before demo", due_at=datetime(2026, 4, 15, 8, 30), owner_id=jane.id),
        Reminder(title="Finish group PR review", due_at=datetime(2026, 4, 16, 17, 0), owner_id=jane.id)
    ]
    db.session.add_all(reminders)

    subjects = [
        HandbookSubject(code="CITS3403", title="Agile Web Development", school="Computer Science", level="Level 3", semester="Semester 1"),
        HandbookSubject(code="CITS4009", title="Fundamentals of Data Science", school="Computer Science", level="Level 4", semester="Semester 2"),
        HandbookSubject(code="CITS1401", title="Computational Thinking with Python", school="Computer Science", level="Level 1", semester="Semester 1"),
        HandbookSubject(code="MATH2004", title="Linear Algebra", school="Mathematics", level="Level 2", semester="Semester 1")
    ]
    db.session.add_all(subjects)

    db.session.commit()

    print("Demo data created successfully.")
