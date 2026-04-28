from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    uwa_id = db.Column(db.String(30), nullable=True)
    program = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(250), nullable=True)
    availability = db.Column(db.String(250), nullable=True)
    avatar_colour = db.Column(db.String(30), default="purple")
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    calendar_events = db.relationship(
        "CalendarEvent",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    group_memberships = db.relationship(
        "GroupMember",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    exam_sessions = db.relationship(
        "ExamSession",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", backref="courses")


class TimetableEvent(db.Model):
    __tablename__ = "timetable_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    event_type = db.Column(db.String(40), nullable=False)
    location = db.Column(db.String(120), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_group_event = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=True)

    owner = db.relationship("User", backref="timetable_events")
    course = db.relationship("Course", backref="events")


class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(32), nullable=False, default="other", index=True)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    end_at = db.Column(db.DateTime, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "event_type": self.event_type,
            "start_at": self.start_at.isoformat(timespec="minutes"),
            "end_at": self.end_at.isoformat(timespec="minutes"),
            "notes": self.notes or "",
        }


class Exam(db.Model):
    __tablename__ = "exams"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(120), nullable=True)
    weight_percent = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=True)

    owner = db.relationship("User", backref="exams")
    course = db.relationship("Course", backref="exams")


class RevisionTopic(db.Model):
    __tablename__ = "revision_topics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    progress = db.Column(db.Integer, default=0)
    status = db.Column(db.String(40), default="Not Started")
    exam_id = db.Column(db.Integer, db.ForeignKey("exams.id"), nullable=False)

    exam = db.relationship("Exam", backref="topics")


class StudyGroup(db.Model):
    __tablename__ = "study_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    # Old main branch field
    group_code = db.Column(db.String(40), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)

    # PR branch fields
    join_code = db.Column(db.String(16), unique=True, nullable=True, index=True)
    created_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    members = db.relationship(
        "GroupMember",
        back_populates="group",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self, *, include_join_code: bool = True) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "created_by_user_id": self.created_by_user_id,
            "member_count": self.members.count(),
        }

        if include_join_code:
            data["join_code"] = self.join_code

        return data


class GroupMember(db.Model):
    __tablename__ = "group_members"
    __table_args__ = (
        db.UniqueConstraint("group_id", "user_id", name="uq_group_member_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(80), default="member")
    status = db.Column(db.String(40), default="Online")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False, index=True)

    user = db.relationship("User", back_populates="group_memberships")
    group = db.relationship("StudyGroup", back_populates="members")


class GroupTask(db.Model):
    __tablename__ = "group_tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    status = db.Column(db.String(40), default="Not Started")
    due_date = db.Column(db.DateTime, nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)

    assigned_to = db.relationship("User", backref="assigned_tasks")
    group = db.relationship("StudyGroup", backref="tasks")


class GroupMessage(db.Model):
    __tablename__ = "group_messages"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)

    sender = db.relationship("User", backref="group_messages")
    group = db.relationship("StudyGroup", backref="messages")


class DirectMessage(db.Model):
    __tablename__ = "direct_messages"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    due_at = db.Column(db.DateTime, nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", backref="reminders")


class HandbookSubject(db.Model):
    __tablename__ = "handbook_subjects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(160), nullable=False)
    school = db.Column(db.String(160), nullable=True)
    level = db.Column(db.String(40), nullable=True)
    semester = db.Column(db.String(80), nullable=True)
    credit_points = db.Column(db.Integer, default=6)


class ExamSession(db.Model):
    __tablename__ = "exam_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    course_code = db.Column(db.String(32), nullable=True)
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    ends_at = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    share_token = db.Column(db.String(64), nullable=True, unique=True, index=True)

    resources = db.relationship(
        "ExamResource",
        backref="exam",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ExamResource.sort_order",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "course_code": self.course_code or "",
            "starts_at": self.starts_at.isoformat(timespec="minutes"),
            "ends_at": self.ends_at.isoformat(timespec="minutes"),
            "notes": self.notes or "",
        }


class ExamResource(db.Model):
    __tablename__ = "exam_resources"

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam_sessions.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "title": self.title,
            "url": self.url,
            "sort_order": self.sort_order,
        }


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if not user_id:
        return None

    return db.session.get(User, int(user_id))