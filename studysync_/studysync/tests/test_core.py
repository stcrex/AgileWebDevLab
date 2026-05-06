from datetime import datetime

from app.extensions import db
from app.models import ChatMessage, DirectMessage, Event, Exam, GroupMessage, ProjectTask, RevisionTopic, User
from .conftest import login


def test_seed_user_password_is_hashed(app):
    with app.app_context():
        user = User.query.filter_by(email="you@student.uwa.edu.au").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert user.check_password("password123")


def test_login_and_logout_flow(client):
    response = login(client)
    assert b"Timetable" in response.data

    logout_page = client.get("/logout")
    assert logout_page.status_code == 200
    assert b"Log out of StudySync" in logout_page.data

    response = client.post("/logout", follow_redirects=True)
    assert b"Welcome back" in response.data
    assert b"logged out safely" in response.data


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create account" in response.data
    assert b"student workspace" in response.data


def test_timetable_requires_login(client):
    response = client.get("/timetable")
    assert response.status_code == 302
    assert "/login" in response.location


def test_events_json_returns_current_user_events(client):
    login(client)
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert data[0]["title"]


def test_create_event_persists_to_database(client, app):
    login(client)
    response = client.post(
        "/api/events",
        data={
            "title": "Revision Workshop",
            "event_type": "Workshop",
            "location": "Library",
            "starts_at": "2026-04-18T09:00",
            "ends_at": "2026-04-18T10:00",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert Event.query.filter_by(title="Revision Workshop").first() is not None


def test_ai_planner_generates_reply_from_weak_topics(client):
    login(client)
    response = client.post("/api/ai/message", json={"message": "Make me a 2 hour study plan"})
    assert response.status_code == 200
    data = response.get_json()
    assert "STUDY PLAN" in data["reply"]
    assert "Flask" in data["reply"] or "SQLAlchemy" in data["reply"]


def test_topic_status_update_changes_exam_progress(client, app):
    login(client)
    with app.app_context():
        topic = RevisionTopic.query.filter(RevisionTopic.status != "Done").first()
        topic_id = topic.id
    response = client.post(f"/api/topics/{topic_id}/status", json={"status": "Done"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "Done"


def test_group_task_status_update(client, app):
    login(client)
    with app.app_context():
        task = ProjectTask.query.first()
        task_id = task.id
    response = client.post(f"/api/group/tasks/{task_id}/status", json={"status": "Done"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "Done"


def test_register_user_persists(client, app):
    response = client.post(
        "/login",
        data={
            "form-name": "register",
            "register-name": "New Student",
            "register-uwa_id": "24000001",
            "register-email": "new@student.uwa.edu.au",
            "register-password": "password123",
            "register-confirm_password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="new@student.uwa.edu.au").first() is not None


def test_handbook_seed_contains_uwa_subjects(app):
    from app.models import HandbookSubject
    with app.app_context():
        subject = HandbookSubject.query.filter_by(code="CITS1401").first()
        assert subject is not None
        assert subject.credit_points == 6
        assert "Python" in subject.title


def test_handbook_page_searches_subjects(client):
    login(client)
    response = client.get("/handbook?q=CITS")
    assert response.status_code == 200
    assert b"UWA Handbook Subjects" in response.data
    assert b"CITS1401" in response.data


def test_add_handbook_subject_to_my_courses(client, app):
    from app.models import Course, HandbookSubject
    login(client)
    with app.app_context():
        subject = HandbookSubject.query.filter_by(code="CITS4012").first()
        subject_id = subject.id
    response = client.post(f"/api/handbook/subjects/{subject_id}/add-course")
    assert response.status_code in {200, 201}
    assert response.get_json()["ok"] is True
    with app.app_context():
        assert Course.query.filter_by(code="CITS4012", title="Natural Language Processing").first() is not None


def test_messages_page_loads_for_group_members(client):
    login(client)
    response = client.get("/messages")
    assert response.status_code == 200
    assert b"Messenger" in response.data
    assert b"Tom Liu" in response.data


def test_send_message_between_group_students(client, app):
    login(client)
    with app.app_context():
        receiver = User.query.filter_by(email="tom@student.uwa.edu.au").first()
        receiver_id = receiver.id
    response = client.post(f"/api/messages/{receiver_id}", json={"body": "Can you check the timetable PR?"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["ok"] is True
    assert data["message"]["body"] == "Can you check the timetable PR?"
    with app.app_context():
        assert DirectMessage.query.filter_by(receiver_id=receiver_id, body="Can you check the timetable PR?").first() is not None


def test_message_api_rejects_non_group_student(client, app):
    login(client)
    with app.app_context():
        outsider = User(name="Outside Student", uwa_id="24009999", email="outsider@student.uwa.edu.au")
        outsider.set_password("password123")
        db.session.add(outsider)
        db.session.commit()
        outsider_id = outsider.id
    response = client.post(f"/api/messages/{outsider_id}", json={"body": "Hello"})
    assert response.status_code == 404



def test_group_chat_page_loads(client):
    login(client)
    response = client.get("/group-chat")
    assert response.status_code == 200
    assert b"Group Chat" in response.data
    assert b"CITS3403 Group 7" in response.data
    assert b"Tom Liu" in response.data


def test_send_group_chat_message_persists(client, app):
    login(client)
    response = client.post("/api/group-chat/messages", json={"body": "Team update: backend group chat is working."})
    assert response.status_code == 201
    data = response.get_json()
    assert data["ok"] is True
    assert data["message"]["body"] == "Team update: backend group chat is working."
    assert data["message"]["is_mine"] is True
    with app.app_context():
        assert GroupMessage.query.filter_by(body="Team update: backend group chat is working.").first() is not None


def test_group_chat_rejects_empty_message(client):
    login(client)
    response = client.post("/api/group-chat/messages", json={"body": "   "})
    assert response.status_code == 400
    assert "empty" in response.get_json()["error"]



def test_profile_page_loads_with_seeded_student_data(client):
    login(client)
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"My Student Profile" in response.data
    assert b"Master of Information Technology" in response.data
    assert b"Backend-focused student" in response.data


def test_profile_ajax_update_persists(client, app):
    login(client)
    response = client.post(
        "/api/profile",
        json={
            "name": "Jane Demo",
            "uwa_id": "23456789",
            "program": "Master of Information Technology",
            "year_level": "Postgraduate",
            "bio": "Updated profile through AJAX.",
            "skills": "Python, Flask, AJAX",
            "study_goal": "Ace the demo",
            "availability": "Sunday afternoon",
            "preferred_contact": "StudySync Messenger",
            "avatar_color": "success",
            "show_email": True,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["profile"]["name"] == "Jane Demo"
    assert "AJAX" in data["profile"]["skills"]
    with app.app_context():
        user = User.query.filter_by(email="you@student.uwa.edu.au").first()
        assert user.name == "Jane Demo"
        assert user.avatar_color == "success"


def test_students_directory_shows_group_member_profiles(client):
    login(client)
    response = client.get("/students")
    assert response.status_code == 200
    assert b"Student Profiles" in response.data
    assert b"Tom Liu" in response.data
    assert b"Frontend developer" in response.data


def test_student_profile_page_restricts_to_same_group(client, app):
    login(client)
    with app.app_context():
        tom = User.query.filter_by(email="tom@student.uwa.edu.au").first()
        outsider = User(name="Outside Student", uwa_id="24009991", email="outside2@student.uwa.edu.au")
        outsider.set_password("password123")
        db.session.add(outsider)
        db.session.commit()
        tom_id = tom.id
        outsider_id = outsider.id

    allowed = client.get(f"/students/{tom_id}")
    assert allowed.status_code == 200
    assert b"Tom Liu" in allowed.data
    denied = client.get(f"/students/{outsider_id}")
    assert denied.status_code == 404


def test_student_profile_json_api(client, app):
    login(client)
    with app.app_context():
        amy = User.query.filter_by(email="amy@student.uwa.edu.au").first()
        amy_id = amy.id
    response = client.get(f"/api/students/{amy_id}/profile")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Amy Kim"
    assert data["email"] == "Hidden"
    assert "Documentation" in data["skills"]


def test_ai_history_buttons_have_backend_endpoints(client, app):
    login(client)
    client.post("/api/ai/message", json={"message": "Make a study plan"})
    response = client.get("/api/ai/history")
    assert response.status_code == 200
    assert len(response.get_json()) >= 2

    clear = client.delete("/api/ai/history", json={})
    assert clear.status_code == 200
    assert clear.get_json()["removed"] >= 2
    with app.app_context():
        user = User.query.filter_by(email="you@student.uwa.edu.au").first()
        assert ChatMessage.query.filter_by(owner_id=user.id).count() == 0


def test_exam_share_button_endpoint_returns_copy_text(client, app):
    login(client)
    with app.app_context():
        exam = Exam.query.first()
        exam_id = exam.id
    response = client.get(f"/api/exams/{exam_id}/share")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert "Revision progress" in data["text"]
    assert f"/exams/{exam_id}" in data["url"]


def test_invite_member_button_endpoint_posts_group_message(client, app):
    login(client)
    response = client.post("/api/group/invite", json={"email": "newmate@student.uwa.edu.au"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert "newmate@student.uwa.edu.au" in data["message"]
    with app.app_context():
        assert GroupMessage.query.filter(GroupMessage.body.contains("newmate@student.uwa.edu.au")).first() is not None


def test_book_common_slot_button_creates_group_events(client, app):
    login(client)
    response = client.post(
        "/api/group/study-session",
        json={
            "title": "Group Study Session — Test Slot",
            "starts_at": "2026-04-20T12:00",
            "ends_at": "2026-04-20T13:00",
            "location": "UWA Library / Online",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["ok"] is True
    with app.app_context():
        assert Event.query.filter_by(title="Group Study Session — Test Slot").count() >= 1
        assert GroupMessage.query.filter(GroupMessage.body.contains("Group Study Session")).first() is not None


def test_ai_planner_returns_contextual_replies(client, login):
    login()
    response = client.post("/api/ai/message", json={"message": "What are my weak exam topics?"})
    assert response.status_code == 200
    data = response.get_json()
    assert "default" not in data["reply"].lower()
    assert "priority" in data["reply"].lower() or "topic" in data["reply"].lower()


def test_ai_practice_question_is_different_from_study_plan(client, login):
    login()
    plan_response = client.post("/api/ai/message", json={"message": "Generate my study plan"})
    quiz_response = client.post("/api/ai/message", json={"message": "Give me one MCQ practice question"})
    assert plan_response.status_code == 200
    assert quiz_response.status_code == 200
    plan = plan_response.get_json()["reply"]
    quiz = quiz_response.get_json()["reply"]
    assert plan != quiz
    assert "practice" in quiz.lower() or "question" in quiz.lower()


def test_courses_page_cards_have_working_actions(client):
    login(client)
    response = client.get("/courses")
    assert response.status_code == 200
    assert b"data-course-card" in response.data
    assert b"Details" in response.data
    assert b"Create Course Event" in response.data
    assert b"Create Course Exam" in response.data


def test_course_detail_page_loads_and_links_course_events(client, app):
    from app.models import Course
    login(client)
    with app.app_context():
        course = Course.query.filter_by(code="CITS3403").first()
        course_id = course.id
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    assert b"Linked Timetable Events" in response.data
    assert b"Linked Exams" in response.data


def test_create_event_from_course_attaches_course_id(client, app):
    from app.models import Course, Event
    login(client)
    with app.app_context():
        course = Course.query.filter_by(code="CITS3403").first()
        course_id = course.id
    response = client.post(
        "/api/events",
        data={
            "course_id": str(course_id),
            "title": "CITS3403 Extra Workshop",
            "event_type": "Workshop",
            "location": "Lab 106",
            "starts_at": "2026-04-21T14:00",
            "ends_at": "2026-04-21T15:00",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        event = Event.query.filter_by(title="CITS3403 Extra Workshop").first()
        assert event is not None
        assert event.course_id == course_id
