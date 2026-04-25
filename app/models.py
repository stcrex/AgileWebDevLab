from __future__ import annotations

from flask_login import UserMixin

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)

    calendar_events = db.relationship(
        "CalendarEvent",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    group_memberships = db.relationship(
        "GroupMember",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        from werkzeug.security import generate_password_hash

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        from werkzeug.security import check_password_hash

        return check_password_hash(self.password_hash, password)


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


class StudyGroup(db.Model):
    __tablename__ = "study_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    join_code = db.Column(db.String(16), unique=True, nullable=False, index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    members = db.relationship(
        "GroupMember",
        back_populates="group",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self, *, include_join_code: bool = True) -> dict:
        d = {
            "id": self.id,
            "name": self.name,
            "created_by_user_id": self.created_by_user_id,
            "member_count": self.members.count(),
        }
        if include_join_code:
            d["join_code"] = self.join_code
        return d


class GroupMember(db.Model):
    __tablename__ = "group_members"
    __table_args__ = (db.UniqueConstraint("group_id", "user_id", name="uq_group_member_user"),)

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("study_groups.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default="member")

    group = db.relationship("StudyGroup", back_populates="members")


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if not user_id:
        return None
    return db.session.get(User, int(user_id))
