from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    uwa_id = db.Column(db.String(30), nullable=True)
    program = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(250), nullable=True)
    availability = db.Column(db.String(250), nullable=True)
    avatar_colour = db.Column(db.String(30), default="purple")
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
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
    name = db.Column(db.String(120), nullable=False)
    group_code = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)


class GroupMember(db.Model):
    __tablename__ = "group_members"

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(80), default="Member")
    status = db.Column(db.String(40), default="Online")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False)

    user = db.relationship("User", backref="group_memberships")
    group = db.relationship("StudyGroup", backref="members")


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
