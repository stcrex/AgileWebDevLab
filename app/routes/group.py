from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import GroupMember, GroupMessage, StudyGroup, User

group_bp = Blueprint("group", __name__)


def first_available_column(model, options):
    """Return the first column name that exists on a model."""
    columns = model.__table__.columns.keys()

    for option in options:
        if option in columns:
            return option

    return None


def get_first_group():
    """For this demo project, we use the first study group in the database."""
    return StudyGroup.query.first()


def message_to_dict(message):
    """Convert a GroupMessage object into safe data for the template."""
    text_column = first_available_column(GroupMessage, ["body", "content", "message", "text"])
    sender_column = first_available_column(GroupMessage, ["sender_id", "user_id", "author_id"])
    created_column = first_available_column(GroupMessage, ["created_at", "timestamp", "sent_at"])

    sender = None

    if sender_column:
        sender_id = getattr(message, sender_column)
        sender = User.query.get(sender_id)

    return {
        "id": message.id,
        "text": getattr(message, text_column) if text_column else "",
        "sender_name": sender.full_name if sender else "StudySync User",
        "sender_email": sender.email if sender else "",
        "is_mine": sender.id == current_user.id if sender else False,
        "created_at": getattr(message, created_column) if created_column else None,
    }


def create_group_message(group_id, user_id, text):
    """Create a message while supporting slightly different model column names."""
    message_data = {}

    group_column = first_available_column(GroupMessage, ["group_id", "study_group_id"])
    sender_column = first_available_column(GroupMessage, ["sender_id", "user_id", "author_id"])
    text_column = first_available_column(GroupMessage, ["body", "content", "message", "text"])
    created_column = first_available_column(GroupMessage, ["created_at", "timestamp", "sent_at"])

    if group_column:
        message_data[group_column] = group_id

    if sender_column:
        message_data[sender_column] = user_id

    if text_column:
        message_data[text_column] = text

    if created_column:
        message_data[created_column] = datetime.now()

    message = GroupMessage(**message_data)
    db.session.add(message)
    db.session.commit()


@group_bp.route("/group-chat", methods=["GET", "POST"])
@login_required
def group_chat():
    group = get_first_group()

    if group is None:
        flash("No study group exists yet. Please seed the database first.")
        return redirect(url_for("main.dashboard"))

    group_id = group.id

    if request.method == "POST":
        message_text = request.form.get("message", "").strip()

        if message_text:
            create_group_message(group_id, current_user.id, message_text)
            flash("Message sent.")
        else:
            flash("Message cannot be empty.")

        return redirect(url_for("group.group_chat"))

    group_column = first_available_column(GroupMessage, ["group_id", "study_group_id"])

    if group_column:
        messages = (
            GroupMessage.query
            .filter(getattr(GroupMessage, group_column) == group_id)
            .all()
        )
    else:
        messages = GroupMessage.query.all()

    message_cards = [message_to_dict(message) for message in messages]

    members = User.query.limit(8).all()

    return render_template(
        "pages/group_chat.html",
        group=group,
        messages=message_cards,
        members=members,
    )


@group_bp.route("/group-chat/invite", methods=["POST"])
@login_required
def invite_member():
    group = get_first_group()

    if group is None:
        flash("No group found.")
        return redirect(url_for("main.dashboard"))

    email = request.form.get("email", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()

    if not email:
        flash("Please enter the student email.")
        return redirect(url_for("group.group_chat"))

    user = User.query.filter_by(email=email).first()

    if user is None:
        user_data = {}

        for column in User.__table__.columns.keys():
            if column == "full_name":
                user_data[column] = full_name or "Invited Student"
            elif column == "email":
                user_data[column] = email
            elif column == "uwa_id":
                user_data[column] = "pending"
            elif column == "program":
                user_data[column] = "Pending invite"
            elif column == "avatar_colour":
                user_data[column] = "blue"

        user = User(**user_data)

        if hasattr(user, "set_password"):
            user.set_password("password123")

        db.session.add(user)
        db.session.commit()

    group_column = first_available_column(GroupMember, ["group_id", "study_group_id"])
    user_column = first_available_column(GroupMember, ["user_id", "member_id"])

    if group_column and user_column:
        existing_member = (
            GroupMember.query
            .filter(getattr(GroupMember, group_column) == group.id)
            .filter(getattr(GroupMember, user_column) == user.id)
            .first()
        )

        if existing_member is None:
            member_data = {
                group_column: group.id,
                user_column: user.id,
            }

            if "role" in GroupMember.__table__.columns.keys():
                member_data["role"] = "Member"

            new_member = GroupMember(**member_data)
            db.session.add(new_member)
            db.session.commit()

    create_group_message(
        group.id,
        current_user.id,
        f"Invited {user.full_name} ({user.email}) to the group."
    )

    flash("Member invited successfully.")
    return redirect(url_for("group.group_chat"))
