from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import EventForm, ExamForm, ResourceForm, TaskForm, TopicForm
from ..models import ChatMessage, Course, DirectMessage, Event, Exam, GroupMember, GroupMessage, HandbookSubject, ProjectTask, Reminder, Resource, RevisionTopic, User
from ..ai_engine import build_ai_context, build_study_reply

api_bp = Blueprint("api", __name__)




PROFILE_TEXT_LIMITS = {
    "name": 80,
    "uwa_id": 20,
    "program": 120,
    "year_level": 40,
    "bio": 500,
    "skills": 255,
    "study_goal": 255,
    "availability": 255,
    "preferred_contact": 120,
    "avatar_color": 30,
}


def profile_to_json(user: User) -> dict:
    membership = GroupMember.query.filter_by(user_id=user.id).first()
    return {
        "id": user.id,
        "name": user.name,
        "initials": user.initials,
        "uwa_id": user.uwa_id,
        "email": user.public_email,
        "program": user.program or "",
        "year_level": user.year_level or "",
        "bio": user.bio or "",
        "skills": user.skill_list,
        "study_goal": user.study_goal or "",
        "availability": user.availability or "",
        "preferred_contact": user.preferred_contact or "StudySync Messenger",
        "avatar_color": user.avatar_color or "primary",
        "show_email": bool(user.show_email),
        "group_role": membership.role if membership else "",
        "group_progress": membership.progress if membership else 0,
        "last_seen": membership.last_seen if membership else "",
    }


@api_bp.get("/profile")
@login_required
def current_profile_json():
    return jsonify(profile_to_json(current_user))


@api_bp.post("/profile")
@login_required
def update_profile_json():
    data = request.get_json(silent=True) or request.form
    errors = {}

    for field_name, limit in PROFILE_TEXT_LIMITS.items():
        if field_name not in data:
            continue
        value = str(data.get(field_name) or "").strip()
        if len(value) > limit:
            errors[field_name] = f"{field_name.replace('_', ' ').title()} must be {limit} characters or fewer."

    if not (data.get("name") or current_user.name).strip():
        errors["name"] = "Name is required."
    if not (data.get("uwa_id") or current_user.uwa_id).strip():
        errors["uwa_id"] = "UWA ID is required."

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    def incoming(field_name: str, fallback: str = "") -> str:
        return str(data.get(field_name) if field_name in data else fallback).strip()

    current_user.name = incoming("name", current_user.name)
    current_user.uwa_id = incoming("uwa_id", current_user.uwa_id)
    current_user.program = incoming("program", current_user.program or "")
    current_user.year_level = incoming("year_level", current_user.year_level or "Postgraduate")
    current_user.bio = incoming("bio", current_user.bio or "")
    current_user.skills = incoming("skills", current_user.skills or "")
    current_user.study_goal = incoming("study_goal", current_user.study_goal or "")
    current_user.availability = incoming("availability", current_user.availability or "")
    current_user.preferred_contact = incoming("preferred_contact", current_user.preferred_contact or "StudySync Messenger")
    current_user.avatar_color = incoming("avatar_color", current_user.avatar_color or "primary")
    if "show_email" in data:
        current_user.show_email = bool(data.get("show_email") in [True, "true", "True", "1", "on", "yes"])
    db.session.commit()
    return jsonify({"ok": True, "profile": profile_to_json(current_user)})


@api_bp.get("/students/<int:user_id>/profile")
@login_required
def student_profile_json(user_id: int):
    membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    student_membership = GroupMember.query.filter_by(group_id=membership.group_id, user_id=user_id).first_or_404()
    return jsonify(profile_to_json(student_membership.user))

def event_to_json(event: Event) -> dict:
    return {
        "id": event.id,
        "title": event.title,
        "type": event.event_type,
        "location": event.location,
        "starts_at": event.starts_at.isoformat(),
        "ends_at": event.ends_at.isoformat(),
        "duration_minutes": event.duration_minutes,
        "course_id": event.course_id,
        "course": event.course.label() if event.course else "",
    }



def get_accessible_course_id(raw_course_id) -> int | None:
    """Validate an optional course_id from a form/API request."""
    if raw_course_id in (None, "", "None"):
        return None
    try:
        course_id = int(raw_course_id)
    except (TypeError, ValueError):
        abort(400)
    course = Course.query.filter(
        Course.id == course_id,
        Course.owner_id == current_user.id,
    ).first_or_404()
    return course.id


def get_or_create_course_from_handbook_subject(raw_subject_id) -> int | None:
    if raw_subject_id in (None, "", "None"):
        return None
    try:
        subject_id = int(raw_subject_id)
    except (TypeError, ValueError):
        abort(400)
    subject = db.session.get(HandbookSubject, subject_id)
    if not subject:
        abort(404)
    course = Course.query.filter_by(owner_id=current_user.id, code=subject.code).first()
    if not course:
        course = Course(code=subject.code, title=subject.title, colour="blue", owner_id=current_user.id)
        db.session.add(course)
        db.session.flush()
    return course.id


@api_bp.get("/events")
@login_required
def events_json():
    events = Event.query.filter_by(owner_id=current_user.id).order_by(Event.starts_at.asc()).all()
    return jsonify([event_to_json(event) for event in events])


def message_to_json(message: DirectMessage) -> dict:
    return {
        "id": message.id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "body": message.body,
        "is_read": message.is_read,
        "created_at": message.created_at.isoformat(),
        "created_time": message.created_at.strftime("%I:%M %p").lstrip("0"),
        "sender_name": message.sender.name,
        "sender_initials": message.sender.initials,
        "is_mine": message.sender_id == current_user.id,
    }


def require_group_contact(contact_id: int) -> User:
    if contact_id == current_user.id:
        abort(400)
    membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    contact_membership = GroupMember.query.filter_by(group_id=membership.group_id, user_id=contact_id).first_or_404()
    return contact_membership.user


@api_bp.get("/messages/conversations")
@login_required
def message_conversations():
    membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    group_members = GroupMember.query.filter_by(group_id=membership.group_id).order_by(GroupMember.id.asc()).all()
    conversations = []
    for group_member in group_members:
        contact = group_member.user
        if contact.id == current_user.id:
            continue
        latest = DirectMessage.query.filter(
            ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == contact.id))
            | ((DirectMessage.sender_id == contact.id) & (DirectMessage.receiver_id == current_user.id))
        ).order_by(DirectMessage.created_at.desc()).first()
        unread = DirectMessage.query.filter_by(sender_id=contact.id, receiver_id=current_user.id, is_read=False).count()
        conversations.append({
            "id": contact.id,
            "name": contact.name,
            "initials": contact.initials,
            "last_seen": group_member.last_seen,
            "latest": latest.body if latest else "No messages yet",
            "latest_time": latest.created_at.strftime("%b %d, %I:%M %p").replace(" 0", " ") if latest else "",
            "unread": unread,
        })
    return jsonify(conversations)


@api_bp.get("/messages/<int:contact_id>")
@login_required
def messages_json(contact_id: int):
    contact = require_group_contact(contact_id)
    messages = DirectMessage.query.filter(
        ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == contact.id))
        | ((DirectMessage.sender_id == contact.id) & (DirectMessage.receiver_id == current_user.id))
    ).order_by(DirectMessage.created_at.asc()).all()

    DirectMessage.query.filter_by(sender_id=contact.id, receiver_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"contact": {"id": contact.id, "name": contact.name, "initials": contact.initials}, "messages": [message_to_json(message) for message in messages]})


@api_bp.post("/messages/<int:contact_id>")
@login_required
def send_message(contact_id: int):
    contact = require_group_contact(contact_id)
    data = request.get_json(silent=True) or request.form
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(body) > 1000:
        return jsonify({"error": "Message must be 1000 characters or fewer."}), 400

    message = DirectMessage(sender_id=current_user.id, receiver_id=contact.id, body=body)
    db.session.add(message)
    db.session.commit()
    return jsonify({"ok": True, "message": message_to_json(message)}), 201


def group_message_to_json(message: GroupMessage) -> dict:
    return {
        "id": message.id,
        "group_id": message.group_id,
        "sender_id": message.sender_id,
        "sender_name": message.sender.name,
        "sender_initials": message.sender.initials,
        "body": message.body,
        "created_at": message.created_at.isoformat(),
        "created_time": message.created_at.strftime("%I:%M %p").lstrip("0"),
        "created_date": message.created_at.strftime("%b %d"),
        "is_mine": message.sender_id == current_user.id,
    }


def require_current_group() -> GroupMember:
    return GroupMember.query.filter_by(user_id=current_user.id).first_or_404()


@api_bp.get("/group-chat/messages")
@login_required
def group_chat_messages_json():
    membership = require_current_group()
    messages = (
        GroupMessage.query.filter_by(group_id=membership.group_id)
        .order_by(GroupMessage.created_at.asc())
        .limit(120)
        .all()
    )
    members = GroupMember.query.filter_by(group_id=membership.group_id).join(GroupMember.user).order_by(GroupMember.id.asc()).all()
    return jsonify({
        "group_id": membership.group_id,
        "members": [
            {
                "id": member.user.id,
                "name": member.user.name,
                "initials": member.user.initials,
                "role": member.role,
                "last_seen": member.last_seen,
                "is_me": member.user_id == current_user.id,
            }
            for member in members
        ],
        "messages": [group_message_to_json(message) for message in messages],
    })


@api_bp.post("/group-chat/messages")
@login_required
def send_group_chat_message():
    membership = require_current_group()
    data = request.get_json(silent=True) or request.form
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify({"error": "Group message cannot be empty."}), 400
    if len(body) > 1500:
        return jsonify({"error": "Group message must be 1500 characters or fewer."}), 400

    message = GroupMessage(group_id=membership.group_id, sender_id=current_user.id, body=body)
    db.session.add(message)
    db.session.commit()
    return jsonify({"ok": True, "message": group_message_to_json(message)}), 201


@api_bp.post("/events")
@login_required
def create_event():
    form = EventForm()
    wants_json = "application/json" in (request.headers.get("Accept") or "") or request.is_json
    if form.validate_on_submit():
        if form.ends_at.data <= form.starts_at.data:
            message = "End time must be after the start time."
            if wants_json:
                return jsonify({"error": message, "errors": {"ends_at": [message]}}), 400
            flash(message, "danger")
            return redirect(url_for("main.timetable", week=form.starts_at.data.date().isoformat()))

        incoming_data = request.get_json(silent=True) or request.form
        course_id = get_accessible_course_id(incoming_data.get("course_id"))

        event = Event(
            owner_id=current_user.id,
            course_id=course_id,
            title=form.title.data,
            event_type=form.event_type.data,
            location=form.location.data or "",
            starts_at=form.starts_at.data,
            ends_at=form.ends_at.data,
            group_visible=form.group_visible.data,
        )
        db.session.add(event)
        db.session.commit()

        if wants_json:
            return jsonify(event_to_json(event)), 201

        flash(f"Event '{event.title}' was added to your timetable.", "success")
        return redirect(url_for("main.timetable", week=event.starts_at.date().isoformat()))

    if wants_json:
        return jsonify({"errors": form.errors}), 400
    flash("Please check the event form and try again.", "danger")
    return redirect(url_for("main.timetable"))


@api_bp.delete("/events/<int:event_id>")
@login_required
def delete_event(event_id: int):
    event = Event.query.filter_by(id=event_id, owner_id=current_user.id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    return jsonify({"ok": True})


@api_bp.post("/exams")
@login_required
def create_exam():
    form = ExamForm()
    wants_json = "application/json" in (request.headers.get("Accept") or "") or request.is_json
    incoming_data = request.get_json(silent=True) or request.form
    handbook_subject_id = incoming_data.get("handbook_subject_id")
    if not (incoming_data.get("title") or "").strip() and handbook_subject_id not in (None, "", "None"):
        subject = HandbookSubject.query.filter_by(id=int(handbook_subject_id)).first()
        if subject:
            form.title.data = f"{subject.code} Exam"
    if form.validate_on_submit():
        if form.ends_at.data <= form.starts_at.data:
            message = "End time must be after the start time."
            if wants_json:
                return jsonify({"error": message, "errors": {"ends_at": [message]}}), 400
            flash(message, "danger")
            return redirect(url_for("main.exams"))

        course_id = get_accessible_course_id(incoming_data.get("course_id"))
        if not course_id:
            course_id = get_or_create_course_from_handbook_subject(handbook_subject_id)

        exam = Exam(
            owner_id=current_user.id,
            course_id=course_id,
            title=form.title.data,
            room=form.room.data or "",
            weight=form.weight.data or 0,
            starts_at=form.starts_at.data,
            ends_at=form.ends_at.data,
            notes=form.notes.data or "",
        )
        db.session.add(exam)
        db.session.commit()
        if wants_json:
            return jsonify({
                "ok": True,
                "id": exam.id,
                "title": exam.title,
                "url": url_for("main.exam_detail", exam_id=exam.id),
                "starts_at": exam.starts_at.isoformat(),
            }), 201
        flash("Exam saved successfully.", "success")
        return redirect(url_for("main.exam_detail", exam_id=exam.id))
    if wants_json:
        return jsonify({"errors": form.errors}), 400
    flash("Please check the exam form and try again.", "danger")
    return redirect(url_for("main.exams"))


@api_bp.post("/exams/<int:exam_id>/notes")
@login_required
def update_exam_notes(exam_id: int):
    exam = Exam.query.filter_by(id=exam_id, owner_id=current_user.id).first_or_404()
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        notes = payload.get("notes", "")
    else:
        notes = request.form.get("notes", "")
    exam.notes = (notes or "").strip()[:2000]
    db.session.commit()
    if request.is_json or "application/json" in (request.headers.get("Accept") or ""):
        return jsonify({"ok": True, "notes": exam.notes})
    flash("Exam notes updated.", "success")
    return redirect(url_for("main.exam_detail", exam_id=exam.id))


@api_bp.get("/exams/<int:exam_id>/share")
@login_required
def share_exam(exam_id: int):
    """Build a shareable exam summary for the Share button."""
    exam = Exam.query.filter_by(id=exam_id, owner_id=current_user.id).first_or_404()
    share_url = request.host_url.rstrip("/") + url_for("main.exam_detail", exam_id=exam.id)
    course = exam.course.code if exam.course else "Course"
    text = (
        f"{course} — {exam.title}\n"
        f"Date: {exam.starts_at.strftime('%A, %d %B %Y')}\n"
        f"Time: {exam.starts_at.strftime('%I:%M %p')}–{exam.ends_at.strftime('%I:%M %p')}\n"
        f"Room: {exam.room or 'TBC'}\n"
        f"Weight: {exam.weight}%\n"
        f"Revision progress: {exam.progress}%\n"
        f"Link: {share_url}"
    )
    return jsonify({"ok": True, "text": text, "url": share_url})



@api_bp.post("/exams/<int:exam_id>/topics")
@login_required
def add_topic(exam_id: int):
    exam = Exam.query.filter_by(id=exam_id, owner_id=current_user.id).first_or_404()
    form = TopicForm()
    if form.validate_on_submit():
        topic = RevisionTopic(
            exam_id=exam.id,
            title=form.title.data,
            area=form.area.data or "General",
            status=form.status.data,
            confidence=form.confidence.data or 0,
        )
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for("main.exam_detail", exam_id=exam.id))
    return jsonify({"errors": form.errors}), 400


@api_bp.post("/exams/<int:exam_id>/resources")
@login_required
def add_resource(exam_id: int):
    exam = Exam.query.filter_by(id=exam_id, owner_id=current_user.id).first_or_404()
    form = ResourceForm()
    if form.validate_on_submit():
        resource = Resource(exam_id=exam.id, title=form.title.data, kind=form.kind.data, url=form.url.data or "#")
        db.session.add(resource)
        db.session.commit()
        return redirect(url_for("main.exam_detail", exam_id=exam.id))
    return jsonify({"errors": form.errors}), 400


@api_bp.post("/topics/<int:topic_id>/status")
@login_required
def update_topic_status(topic_id: int):
    topic = RevisionTopic.query.join(Exam).filter(RevisionTopic.id == topic_id, Exam.owner_id == current_user.id).first_or_404()
    data = request.get_json(silent=True) or request.form
    requested_status = data.get("status")
    if requested_status not in {"Not Started", "In Progress", "Done"}:
        requested_status = "Done" if topic.status != "Done" else "In Progress"
    topic.status = requested_status
    if topic.status == "Done":
        topic.confidence = max(topic.confidence or 0, 100)
    elif topic.status == "In Progress":
        topic.confidence = max(topic.confidence or 0, 60)
    db.session.commit()
    return jsonify({"ok": True, "status": topic.status, "progress": topic.exam.progress})


@api_bp.post("/ai/message")
@login_required
def ai_message():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    db.session.add(ChatMessage(owner_id=current_user.id, role="user", content=user_message))
    context = build_ai_context(current_user)
    answer = build_study_reply(context, user_message)
    db.session.add(ChatMessage(owner_id=current_user.id, role="assistant", content=answer))
    db.session.commit()
    return jsonify({"reply": answer})


@api_bp.get("/ai/history")
@login_required
def ai_history():
    """Return the latest AI planner messages for the History button."""
    history = (
        ChatMessage.query.filter_by(owner_id=current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "created_label": message.created_at.strftime("%b %d, %I:%M %p").replace(" 0", " "),
        }
        for message in history
    ])


@api_bp.delete("/ai/history")
@login_required
def clear_ai_history():
    """Delete saved AI planner messages for the Clear button."""
    removed = ChatMessage.query.filter_by(owner_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"ok": True, "removed": removed})



@api_bp.post("/group/invite")
@login_required
def invite_group_member():
    """Prepare a safe group invite.

    Existing users are added directly to the current group.
    New users are given a shareable group code instead of an insecure default password.
    """
    membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").strip().lower()
    role = (data.get("role") or "Member").strip()[:40] or "Member"

    if not email or "@" not in email:
        return jsonify({"error": "Enter a valid email address."}), 400

    user = User.query.filter_by(email=email).first()
    created_account = False
    added_to_group = False

    if user:
        existing_member = GroupMember.query.filter_by(group_id=membership.group_id, user_id=user.id).first()
        if not existing_member:
            existing_member = GroupMember(
                group_id=membership.group_id,
                user_id=user.id,
                role=role,
                progress=0,
                last_seen="Invited",
            )
            db.session.add(existing_member)
            added_to_group = True
        else:
            existing_member.role = role or existing_member.role
        invite_text = (
            f"Hi {user.name}! You have been added to the StudySync group '{membership.group.name}'. "
            f"Open StudySync and head to My Group to start collaborating."
        )
        audit_text = f"{current_user.name} added {user.name} ({email}) to the group as {existing_member.role}."
        member_payload = {
            "id": user.id,
            "name": user.name,
            "initials": user.initials,
            "role": existing_member.role,
            "last_seen": existing_member.last_seen,
            "is_me": existing_member.user_id == current_user.id,
        }
    else:
        invite_text = (
            f"Hi! Join our StudySync project group '{membership.group.name}' using group code {membership.group.code}. "
            f"Create your StudySync account first, then open My Group and enter the code to join."
        )
        audit_text = f"{current_user.name} prepared an invite for {email} using group code {membership.group.code}."
        member_payload = None

    db.session.add(
        GroupMessage(
            group_id=membership.group_id,
            sender_id=current_user.id,
            body=audit_text,
        )
    )
    db.session.commit()

    return jsonify({
        "ok": True,
        "created_account": created_account,
        "added_to_group": added_to_group,
        "message": "Invite prepared successfully.",
        "invite_text": invite_text,
        "group_code": membership.group.code,
        "member": member_payload,
    })


@api_bp.post("/group/study-session")
@login_required
def book_group_study_session():
    """Book one of the common free slots for available group members."""
    membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or request.form
    title = (data.get("title") or "Group Study Session").strip()[:120]
    location = (data.get("location") or "StudySync group room").strip()[:100]
    try:
        starts_at = datetime.fromisoformat(str(data.get("starts_at")))
        ends_at = datetime.fromisoformat(str(data.get("ends_at")))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid start or end time."}), 400
    if ends_at <= starts_at:
        return jsonify({"error": "End time must be after start time."}), 400

    members = GroupMember.query.filter_by(group_id=membership.group_id).all()
    created = 0
    skipped = 0
    for member in members:
        exists = Event.query.filter_by(owner_id=member.user_id, title=title, starts_at=starts_at).first()
        conflict = Event.query.filter(
            Event.owner_id == member.user_id,
            Event.starts_at < ends_at,
            Event.ends_at > starts_at,
        ).first()
        exam_conflict = Exam.query.filter(
            Exam.owner_id == member.user_id,
            Exam.starts_at < ends_at,
            Exam.ends_at > starts_at,
        ).first()
        if exists or conflict or exam_conflict:
            skipped += 1
            continue
        db.session.add(
            Event(
                owner_id=member.user_id,
                title=title,
                event_type="Workshop",
                location=location,
                starts_at=starts_at,
                ends_at=ends_at,
                group_visible=True,
            )
        )
        created += 1

    db.session.add(
        GroupMessage(
            group_id=membership.group_id,
            sender_id=current_user.id,
            body=f"Booked {title} for {starts_at.strftime('%a %d %b, %I:%M %p')} at {location}. {created} member(s) added, {skipped} skipped due to clashes.",
        )
    )
    db.session.commit()
    return jsonify({"ok": True, "created": created, "skipped": skipped, "message": f"Booked for {created} group member(s). {skipped} skipped due to clashes."})


@api_bp.post("/group/tasks")
@login_required
def add_group_task():
    membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    form = TaskForm()
    if form.validate_on_submit():
        task = ProjectTask(group_id=membership.group_id, assigned_to_id=current_user.id, title=form.title.data, due_date=form.due_date.data, status="Not Started")
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("main.group"))
    return jsonify({"errors": form.errors}), 400


@api_bp.post("/group/tasks/<int:task_id>/status")
@login_required
def update_task_status(task_id: int):
    membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    task = ProjectTask.query.filter_by(id=task_id, group_id=membership.group_id).first_or_404()
    data = request.get_json(silent=True) or request.form
    requested_status = data.get("status", "In Progress")
    if requested_status in {"Not Started", "In Progress", "Done"}:
        task.status = requested_status
        db.session.commit()
    return jsonify({"ok": True, "status": task.status})


@api_bp.post("/reminders")
@login_required
def create_reminder():
    data = request.get_json(silent=True) or request.form
    title = (data.get("title") or "").strip()
    due_raw = (data.get("due_at") or "").strip()
    if not title:
        flash("Reminder title is required.", "danger")
        return redirect(url_for("main.reminders"))
    try:
        due_at = datetime.fromisoformat(due_raw)
    except ValueError:
        flash("Reminder due date is invalid.", "danger")
        return redirect(url_for("main.reminders"))
    reminder = Reminder(owner_id=current_user.id, title=title[:160], due_at=due_at)
    db.session.add(reminder)
    db.session.commit()
    flash("Reminder created.", "success")
    return redirect(url_for("main.reminders"))


@api_bp.post("/reminders/<int:reminder_id>/update")
@login_required
def update_reminder(reminder_id: int):
    reminder = Reminder.query.filter_by(id=reminder_id, owner_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or request.form
    title = (data.get("title") or "").strip()
    due_raw = (data.get("due_at") or "").strip()
    if not title:
        flash("Reminder title is required.", "danger")
        return redirect(url_for("main.reminders"))
    try:
        due_at = datetime.fromisoformat(due_raw)
    except ValueError:
        flash("Reminder due date is invalid.", "danger")
        return redirect(url_for("main.reminders"))
    reminder.title = title[:160]
    reminder.due_at = due_at
    db.session.commit()
    flash("Reminder updated.", "success")
    return redirect(url_for("main.reminders"))


@api_bp.post("/reminders/<int:reminder_id>/delete")
@login_required
def delete_reminder(reminder_id: int):
    reminder = Reminder.query.filter_by(id=reminder_id, owner_id=current_user.id).first_or_404()
    db.session.delete(reminder)
    db.session.commit()
    flash("Reminder deleted.", "success")
    return redirect(url_for("main.reminders"))


@api_bp.post("/reminders/<int:reminder_id>/toggle")
@login_required
def toggle_reminder(reminder_id: int):
    reminder = Reminder.query.filter_by(id=reminder_id, owner_id=current_user.id).first_or_404()
    reminder.is_done = not reminder.is_done
    db.session.commit()
    return jsonify({"ok": True, "is_done": reminder.is_done})


@api_bp.post("/handbook/subjects/<int:subject_id>/add-course")
@login_required
def add_handbook_subject_to_courses(subject_id: int):
    subject = db.session.get(HandbookSubject, subject_id)
    if not subject:
        abort(404)
    existing = Course.query.filter_by(owner_id=current_user.id, code=subject.code).first()
    if existing:
        return jsonify({"ok": True, "created": False, "course_id": existing.id, "message": "Already in your courses"})

    course = Course(code=subject.code, title=subject.title, colour="blue", owner_id=current_user.id)
    db.session.add(course)
    db.session.commit()
    return jsonify({"ok": True, "created": True, "course_id": course.id, "message": f"{subject.code} added to your courses"}), 201


@api_bp.get("/handbook/subjects")
@login_required
def handbook_subjects_json():
    query_text = (request.args.get("q") or "").strip()
    subjects_query = HandbookSubject.query
    if query_text:
        like = f"%{query_text}%"
        subjects_query = subjects_query.filter(HandbookSubject.code.ilike(like) | HandbookSubject.title.ilike(like))
    subjects = subjects_query.order_by(HandbookSubject.code.asc()).limit(50).all()
    return jsonify([
        {
            "id": subject.id,
            "code": subject.code,
            "title": subject.title,
            "credit_points": subject.credit_points,
            "availability": subject.availability,
            "school": subject.school,
            "handbook_url": subject.handbook_url,
        }
        for subject in subjects
    ])
