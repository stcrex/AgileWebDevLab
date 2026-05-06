from datetime import date, datetime
import json
from pathlib import Path

from .extensions import db
from .models import ChatMessage, Course, DirectMessage, Event, Exam, Group, GroupMember, GroupMessage, HandbookSubject, ProjectTask, Reminder, Resource, RevisionTopic, User


def seed_handbook_subjects() -> int:
    """Load a curated 2026 UWA Handbook unit catalogue into the database."""
    data_path = Path(__file__).parent / "data" / "uwa_handbook_units_2026_seed.json"
    units = json.loads(data_path.read_text(encoding="utf-8"))
    inserted = 0
    for item in units:
        subject = HandbookSubject.query.filter_by(code=item["code"]).first()
        if subject is None:
            subject = HandbookSubject(code=item["code"], title=item["title"])
            db.session.add(subject)
            inserted += 1
        subject.title = item.get("title", subject.title)
        subject.credit_points = item.get("credit_points", 6)
        subject.coordinator = item.get("coordinator", "")
        subject.level_of_study = item.get("level_of_study", "")
        subject.school = item.get("school", "")
        subject.field_of_education = item.get("field_of_education", "")
        subject.availability = item.get("availability", "")
        subject.location = item.get("location", "")
        subject.description = item.get("description", "")
        subject.handbook_url = item.get("handbook_url", f"https://handbooks.uwa.edu.au/unitdetails?code={subject.code}")
        subject.source_year = item.get("source_year", 2026)
    return inserted


def seed_database() -> None:
    """Insert realistic demo data used in the screenshots and tests."""
    seed_handbook_subjects()
    if User.query.filter_by(email="you@student.uwa.edu.au").first():
        db.session.commit()
        return

    jane = User(
        name="Jane Smith",
        uwa_id="23456789",
        email="you@student.uwa.edu.au",
        avatar_color="primary",
        program="Master of Information Technology",
        year_level="Postgraduate",
        bio="Backend-focused student working on Flask routes, SQLAlchemy models, testing and project coordination.",
        skills="Python, Flask, SQLAlchemy, GitHub, Testing",
        study_goal="Finish the group project early and polish the demo for full marks.",
        availability="Weekdays after 5pm, Sunday afternoon",
        preferred_contact="StudySync Messenger",
        show_email=True,
    )
    jane.set_password("password123")
    tom = User(
        name="Tom Liu",
        uwa_id="23112233",
        email="tom@student.uwa.edu.au",
        avatar_color="warning",
        program="Bachelor of Computer Science",
        year_level="Undergraduate Year 3",
        bio="Frontend developer who enjoys building clean Bootstrap layouts and responsive interfaces.",
        skills="HTML, CSS, Bootstrap, JavaScript, UI Design",
        study_goal="Make the timetable and dashboard pages look professional.",
        availability="Monday and Wednesday evenings",
        preferred_contact="Messenger or group chat",
        show_email=True,
    )
    tom.set_password("password123")
    amy = User(
        name="Amy Kim",
        uwa_id="23888881",
        email="amy@student.uwa.edu.au",
        avatar_color="purple",
        program="Master of Data Science",
        year_level="Postgraduate",
        bio="Planning and documentation lead. Keeps the README, user stories and project checklist organised.",
        skills="Documentation, User Stories, Testing, Agile, Research",
        study_goal="Keep the group organised and ready for each checkpoint.",
        availability="Tuesday afternoon, Friday morning",
        preferred_contact="Group chat",
        show_email=False,
    )
    amy.set_password("password123")
    ryan = User(
        name="Ryan Zhang",
        uwa_id="23777774",
        email="ryan@student.uwa.edu.au",
        avatar_color="success",
        program="Master of Information Technology",
        year_level="Postgraduate",
        bio="Works on AI planner screens, AJAX interactions and demo testing.",
        skills="JavaScript, AJAX, Flask, Selenium, AI UI",
        study_goal="Make the planner and messaging features smooth in the final demo.",
        availability="Most evenings after 6pm",
        preferred_contact="StudySync Messenger",
        show_email=True,
    )
    ryan.set_password("password123")
    db.session.add_all([jane, tom, amy, ryan])
    db.session.flush()

    cits = Course(code="CITS3403", title="Agile Web Development", colour="blue", owner_id=jane.id)
    math = Course(code="MATH2004", title="Linear Algebra", colour="indigo", owner_id=jane.id)
    data_science = Course(code="CITS4009", title="Fundamentals of Data Science", colour="green", owner_id=jane.id)
    db.session.add_all([cits, math, data_science])
    db.session.flush()

    events = [
        Event(owner_id=jane.id, course_id=cits.id, title="CITS3403 Laboratory", event_type="Laboratory", location="Lab 106", starts_at=datetime(2026, 4, 14, 9, 0), ends_at=datetime(2026, 4, 14, 10, 0)),
        Event(owner_id=jane.id, course_id=cits.id, title="CITS3403 Lecture — Web Dev", event_type="Lecture", location="LT 225", starts_at=datetime(2026, 4, 15, 9, 0), ends_at=datetime(2026, 4, 15, 10, 0)),
        Event(owner_id=jane.id, course_id=cits.id, title="Mid-sem Test", event_type="Exam", location="Room 106", starts_at=datetime(2026, 4, 15, 10, 0), ends_at=datetime(2026, 4, 15, 11, 0)),
        Event(owner_id=jane.id, course_id=math.id, title="MATH2004 Lecture — Linear Alg", event_type="Lecture", location="LT 120", starts_at=datetime(2026, 4, 16, 9, 0), ends_at=datetime(2026, 4, 16, 10, 0)),
        Event(owner_id=jane.id, course_id=math.id, title="MATH2004 Tutorial", event_type="Tutorial", location="Big 205", starts_at=datetime(2026, 4, 16, 11, 0), ends_at=datetime(2026, 4, 16, 12, 0)),
        Event(owner_id=jane.id, course_id=cits.id, title="CITS3403 Tutorial — Group 02", event_type="Tutorial", location="Reid 115", starts_at=datetime(2026, 4, 17, 10, 0), ends_at=datetime(2026, 4, 17, 11, 0)),
    ]
    db.session.add_all(events)

    exam = Exam(owner_id=jane.id, course_id=cits.id, title="CITS3403 — Mid-semester Test", room="Room 106, CS Building", weight=20, starts_at=datetime(2026, 4, 15, 10, 0), ends_at=datetime(2026, 4, 15, 11, 0), notes="- Flask app factory pattern: create_app() function\n- SQLAlchemy session vs query interface\n- Remember CSRF tokens for all forms!")
    db.session.add(exam)
    db.session.flush()
    topics = [
        RevisionTopic(exam_id=exam.id, title="HTML semantic elements & forms", area="HTML & CSS Fundamentals", status="Done", confidence=100),
        RevisionTopic(exam_id=exam.id, title="CSS flexbox & grid layout", area="HTML & CSS Fundamentals", status="Done", confidence=100),
        RevisionTopic(exam_id=exam.id, title="Bootstrap 5 components", area="HTML & CSS Fundamentals", status="Done", confidence=100),
        RevisionTopic(exam_id=exam.id, title="JavaScript event listeners & DOM manipulation", area="JavaScript & DOM", status="In Progress", confidence=65),
        RevisionTopic(exam_id=exam.id, title="AJAX & fetch API", area="JavaScript & DOM", status="In Progress", confidence=65),
        RevisionTopic(exam_id=exam.id, title="Flask routes & Jinja2 templates", area="Flask Basics", status="Not Started", confidence=30),
        RevisionTopic(exam_id=exam.id, title="SQLAlchemy models & relationships", area="SQLAlchemy & Models", status="Not Started", confidence=10),
    ]
    db.session.add_all(topics)
    db.session.add_all([
        Resource(exam_id=exam.id, title="Week 1–4 Lecture Slides", kind="PDF", url="#"),
        Resource(exam_id=exam.id, title="Flask Tutorial (CS50)", kind="Video", url="https://www.youtube.com/"),
        Resource(exam_id=exam.id, title="SQLAlchemy Docs", kind="Docs", url="https://docs.sqlalchemy.org/"),
    ])

    group = Group(name="CITS3403 Group 7", code="GRP-3403-07")
    db.session.add(group)
    db.session.flush()
    db.session.add_all([
        GroupMember(group_id=group.id, user_id=jane.id, role="Lead", progress=75, last_seen="Online"),
        GroupMember(group_id=group.id, user_id=tom.id, role="Frontend", progress=80, last_seen="Online"),
        GroupMember(group_id=group.id, user_id=amy.id, role="Planner", progress=45, last_seen="Last seen 1h ago"),
        GroupMember(group_id=group.id, user_id=ryan.id, role="AI UI", progress=60, last_seen="Online"),
    ])
    db.session.add_all([
        ProjectTask(group_id=group.id, assigned_to_id=jane.id, title="Login / Register pages (HTML)", due_date=date(2026, 4, 18), status="Done"),
        ProjectTask(group_id=group.id, assigned_to_id=tom.id, title="Timetable grid component", due_date=date(2026, 4, 18), status="In Progress"),
        ProjectTask(group_id=group.id, assigned_to_id=amy.id, title="User stories & page list document", due_date=date(2026, 4, 16), status="Done"),
        ProjectTask(group_id=group.id, assigned_to_id=ryan.id, title="AI Planner chat UI", due_date=date(2026, 4, 20), status="Not Started"),
    ])

    db.session.add_all([
        Reminder(owner_id=jane.id, title="Revise Flask routes before the test", due_at=datetime(2026, 4, 15, 7, 25)),
        Reminder(owner_id=jane.id, title="Group checkpoint meeting", due_at=datetime(2026, 4, 17, 14, 0)),
    ])
    db.session.add_all([
        ChatMessage(owner_id=jane.id, role="assistant", content="👋 Hi Jane! I can see you have a CITS3403 Mid-semester Test soon. I have checked your progress and timetable. How can I help right now?"),
    ])
    db.session.add_all([
        DirectMessage(sender_id=tom.id, receiver_id=jane.id, body="Hey Jane, I finished the timetable CSS. Can you check the pull request?", is_read=False, created_at=datetime(2026, 4, 14, 18, 15)),
        DirectMessage(sender_id=jane.id, receiver_id=tom.id, body="Nice work! I will review it after updating the backend routes.", is_read=True, created_at=datetime(2026, 4, 14, 18, 22)),
        DirectMessage(sender_id=amy.id, receiver_id=jane.id, body="I added the user stories document. We still need screenshots for the README.", is_read=False, created_at=datetime(2026, 4, 15, 9, 10)),
        DirectMessage(sender_id=ryan.id, receiver_id=jane.id, body="I can start the AI planner chat UI tonight.", is_read=False, created_at=datetime(2026, 4, 15, 10, 40)),
    ])
    db.session.add_all([
        GroupMessage(group_id=group.id, sender_id=amy.id, body="Morning team! I uploaded the 10 user stories and page list for Checkpoint 2.", created_at=datetime(2026, 4, 15, 8, 45)),
        GroupMessage(group_id=group.id, sender_id=tom.id, body="Great. I am working on the timetable UI and will open a PR before tonight.", created_at=datetime(2026, 4, 15, 9, 5)),
        GroupMessage(group_id=group.id, sender_id=jane.id, body="I will connect the Flask routes and database models. Please keep task statuses updated here.", created_at=datetime(2026, 4, 15, 9, 20)),
        GroupMessage(group_id=group.id, sender_id=ryan.id, body="I can test the AI planner page and add screenshots to the README.", created_at=datetime(2026, 4, 15, 10, 15)),
    ])
    db.session.commit()
