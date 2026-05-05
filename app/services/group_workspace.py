"""Group workspace: messages and invites for a study group (used by group_book blueprint)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db
from app.models import GroupMember, GroupMessage, User


def message_cards_for_group(group_id: int, viewer_user_id: int) -> list[dict]:
    rows = (
        GroupMessage.query.filter_by(group_id=group_id)
        .order_by(GroupMessage.created_at.asc(), GroupMessage.id.asc())
        .all()
    )
    return [_message_to_dict(m, viewer_user_id) for m in rows]


def _message_to_dict(message: GroupMessage, viewer_user_id: int) -> dict:
    sender = db.session.get(User, message.sender_id)
    return {
        "id": message.id,
        "text": message.body,
        "sender_name": sender.full_name if sender else "Member",
        "sender_email": sender.email if sender else "",
        "is_mine": bool(sender and sender.id == viewer_user_id),
        "created_at": message.created_at,
    }


def create_group_message(*, group_id: int, user_id: int, body: str) -> GroupMessage:
    msg = GroupMessage(
        body=body, sender_id=user_id, group_id=group_id, created_at=datetime.now(timezone.utc)
    )
    db.session.add(msg)
    db.session.commit()
    return msg


def group_member_users(group_id: int) -> list[User]:
    return (
        db.session.query(User)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .order_by(User.full_name.asc())
        .all()
    )


def add_group_member_if_missing(*, group_id: int, user_id: int) -> bool:
    """Return True if a new GroupMember row was added."""
    exists = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if exists is not None:
        return False
    db.session.add(GroupMember(group_id=group_id, user_id=user_id, role="member"))
    db.session.commit()
    return True


def ensure_user_for_invite(*, email: str, full_name: str) -> User:
    """Find or create a user record for an invited email."""
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()
    if user is not None:
        return user
    u = User(
        email=email,
        full_name=full_name or "Invited Student",
        uwa_id="pending",
        program="Pending invite",
        avatar_colour="blue",
        password_hash="",
    )
    u.set_password("password123")
    db.session.add(u)
    db.session.commit()
    return u
