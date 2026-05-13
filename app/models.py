from __future__ import annotations

from datetime import UTC, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    uwa_id = db.Column(db.String(20), nullable=False, default="")
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_color = db.Column(db.String(30), default="primary")
    program = db.Column(db.String(120), default="Master of Information Technology")
    year_level = db.Column(db.String(40), default="Postgraduate")
    bio = db.Column(db.Text, default="")
    skills = db.Column(db.String(255), default="")
    study_goal = db.Column(db.String(255), default="")
    availability = db.Column(db.String(255), default="")
    preferred_contact = db.Column(db.String(120), default="StudySync Messenger")
    show_email = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    events = db.relationship("Event", back_populates="owner", cascade="all, delete-orphan")
    exams = db.relationship("Exam", back_populates="owner", cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", back_populates="owner", cascade="all, delete-orphan")
    chat_messages = db.relationship("ChatMessage", back_populates="owner", cascade="all, delete-orphan")
    sent_messages = db.relationship("DirectMessage", foreign_keys="DirectMessage.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = db.relationship("DirectMessage", foreign_keys="DirectMessage.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    group_messages = db.relationship("GroupMessage", back_populates="sender", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self) -> str:
        parts = [p[0].upper() for p in self.name.split() if p]
        return "".join(parts[:2]) or "U"

    @property
    def skill_list(self) -> list[str]:
        return [skill.strip() for skill in (self.skills or "").split(",") if skill.strip()]

    @property
    def public_email(self) -> str:
        return self.email if self.show_email else "Hidden"


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id)) if user_id.isdigit() else None


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    colour = db.Column(db.String(30), default="blue")
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    events = db.relationship("Event", back_populates="course")
    exams = db.relationship("Exam", back_populates="course")

    def label(self) -> str:
        return f"{self.code} — {self.title}"


class HandbookSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True, index=True)
    title = db.Column(db.String(180), nullable=False, index=True)
    credit_points = db.Column(db.Integer, default=6)
    coordinator = db.Column(db.String(180), default="")
    level_of_study = db.Column(db.String(80), default="")
    school = db.Column(db.String(140), default="")
    field_of_education = db.Column(db.String(140), default="")
    availability = db.Column(db.String(120), default="")
    location = db.Column(db.String(120), default="")
    description = db.Column(db.Text, default="")
    handbook_url = db.Column(db.String(255), default="")
    source_year = db.Column(db.Integer, default=2026)
    imported_at = db.Column(db.DateTime, default=utcnow)

    @property
    def short_label(self) -> str:
        return f"{self.code} — {self.title}"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=True)
    title = db.Column(db.String(120), nullable=False)
    event_type = db.Column(db.String(30), nullable=False, default="Lecture")
    location = db.Column(db.String(100), default="")
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    group_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    owner = db.relationship("User", back_populates="events")
    course = db.relationship("Course", back_populates="events")

    @property
    def duration_minutes(self) -> int:
        return int((self.ends_at - self.starts_at).total_seconds() // 60)


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=True)
    title = db.Column(db.String(120), nullable=False)
    room = db.Column(db.String(80), default="")
    weight = db.Column(db.Integer, default=0)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, default="")

    owner = db.relationship("User", back_populates="exams")
    course = db.relationship("Course", back_populates="exams")
    topics = db.relationship("RevisionTopic", back_populates="exam", cascade="all, delete-orphan")
    resources = db.relationship("Resource", back_populates="exam", cascade="all, delete-orphan")

    @property
    def progress(self) -> int:
        if not self.topics:
            return 0
        done_count = sum(1 for topic in self.topics if topic.status == "Done")
        return round(done_count / len(self.topics) * 100)

    @property
    def weak_topics(self):
        return [topic for topic in self.topics if topic.status != "Done"]


class RevisionTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    area = db.Column(db.String(80), default="General")
    status = db.Column(db.String(30), nullable=False, default="Not Started")
    confidence = db.Column(db.Integer, default=0)

    exam = db.relationship("Exam", back_populates="topics")


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(30), default="Link")
    url = db.Column(db.String(255), default="")

    exam = db.relationship("Exam", back_populates="resources")


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    due_at = db.Column(db.DateTime, nullable=False)
    is_done = db.Column(db.Boolean, default=False)

    owner = db.relationship("User", back_populates="reminders")


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(40), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    memberships = db.relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    tasks = db.relationship("ProjectTask", back_populates="group", cascade="all, delete-orphan")
    messages = db.relationship("GroupMessage", back_populates="group", cascade="all, delete-orphan")


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role = db.Column(db.String(40), default="Member")
    progress = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.String(40), default="Online")

    group = db.relationship("Group", back_populates="memberships")
    user = db.relationship("User")


class ProjectTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    title = db.Column(db.String(160), nullable=False)
    status = db.Column(db.String(30), default="Not Started")
    due_date = db.Column(db.Date, nullable=True)

    group = db.relationship("Group", back_populates="tasks")
    assigned_to = db.relationship("User")


class GroupMessage(db.Model):
    """Message posted into a project group chat room."""

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)

    group = db.relationship("Group", back_populates="messages")
    sender = db.relationship("User", back_populates="group_messages")

    def preview(self, limit: int = 80) -> str:
        clean = " ".join(self.body.split())
        return clean if len(clean) <= limit else clean[: limit - 1] + "…"


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user / assistant
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    owner = db.relationship("User", back_populates="chat_messages")


class DirectMessage(db.Model):
    """One-to-one messenger message between two students in the same StudySync group."""

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)

    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

    def belongs_to_conversation(self, first_user_id: int, second_user_id: int) -> bool:
        return {self.sender_id, self.receiver_id} == {first_user_id, second_user_id}
