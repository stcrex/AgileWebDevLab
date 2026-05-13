from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from secrets import token_hex

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import (
    CreateGroupForm,
    EventForm,
    ExamForm,
    JoinGroupForm,
    ProfileForm,
    ReminderForm,
    ResourceForm,
    TaskForm,
    TopicForm,
)
from ..models import (
    Course,
    DirectMessage,
    Event,
    Exam,
    Group,
    GroupMember,
    GroupMessage,
    HandbookSubject,
    ProjectTask,
    Reminder,
    User,
)

main_bp = Blueprint("main", __name__)


WORKDAY_START_HOUR = 8
WORKDAY_END_HOUR = 18


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def week_bounds(reference: datetime | None = None):
    reference = reference or utcnow()
    start = reference - timedelta(days=reference.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=5)


def parse_week_reference() -> datetime:
    raw_week = (request.args.get("week") or "").strip()
    if not raw_week:
        return utcnow()
    try:
        return datetime.fromisoformat(raw_week)
    except ValueError:
        flash("Invalid week selected, showing the current week instead.", "warning")
        return utcnow()


def datetime_local_value(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%dT%H:%M") if value else ""


def default_datetime_pair(start_hour: int = 9, duration_minutes: int = 60) -> tuple[str, str]:
    now = utcnow().replace(second=0, microsecond=0)
    start = now.replace(hour=start_hour, minute=0)
    if start <= now:
        start = (now + timedelta(days=1)).replace(hour=start_hour, minute=0)
    end = start + timedelta(minutes=duration_minutes)
    return datetime_local_value(start), datetime_local_value(end)


def create_group_code() -> str:
    while True:
        code = f"GRP-{token_hex(3).upper()}"
        if not Group.query.filter_by(code=code).first():
            return code


def accessible_course_or_404(course_id: int) -> Course:
    return Course.query.filter(
        Course.id == course_id,
        Course.owner_id == current_user.id,
    ).first_or_404()


def same_group_member_or_404(user_id: int) -> GroupMember:
    my_membership = GroupMember.query.filter_by(user_id=current_user.id).first_or_404()
    requested = GroupMember.query.filter_by(group_id=my_membership.group_id, user_id=user_id).first_or_404()
    return requested


def student_profile_stats(user: User) -> dict:
    completed_tasks = ProjectTask.query.filter_by(assigned_to_id=user.id, status="Done").count()
    total_tasks = ProjectTask.query.filter_by(assigned_to_id=user.id).count()
    upcoming_events = Event.query.filter_by(owner_id=user.id).count()
    courses_count = Course.query.filter_by(owner_id=user.id).count()
    direct_messages_sent = DirectMessage.query.filter_by(sender_id=user.id).count()
    group_messages_sent = GroupMessage.query.filter_by(sender_id=user.id).count()
    return {
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "task_progress": round(completed_tasks / total_tasks * 100) if total_tasks else 0,
        "upcoming_events": upcoming_events,
        "courses_count": courses_count,
        "messages_sent": direct_messages_sent + group_messages_sent,
    }


def group_member_stats(member: GroupMember) -> dict:
    return {
        "tasks": ProjectTask.query.filter_by(assigned_to_id=member.user_id).count(),
        "events": Event.query.filter_by(owner_id=member.user_id).count(),
        "messages": DirectMessage.query.filter_by(sender_id=member.user_id).count()
        + GroupMessage.query.filter_by(sender_id=member.user_id).count(),
    }


def overlaps(starts_at: datetime, ends_at: datetime, other_start: datetime, other_end: datetime) -> bool:
    return starts_at < other_end and ends_at > other_start


def compute_common_free_slots(group: Group, week_start: datetime, duration_minutes: int = 120) -> list[dict]:
    member_ids = [member.user_id for member in group.memberships]
    slots: list[dict] = []
    for day_index in range(5):
        day = week_start + timedelta(days=day_index)
        for hour in (9, 11, 13, 15):
            starts_at = day.replace(hour=hour, minute=0)
            ends_at = starts_at + timedelta(minutes=duration_minutes)
            available_count = 0
            for user_id in member_ids:
                event_conflict = Event.query.filter(
                    Event.owner_id == user_id,
                    Event.starts_at < ends_at,
                    Event.ends_at > starts_at,
                ).first()
                exam_conflict = Exam.query.filter(
                    Exam.owner_id == user_id,
                    Exam.starts_at < ends_at,
                    Exam.ends_at > starts_at,
                ).first()
                if not event_conflict and not exam_conflict:
                    available_count += 1
            if available_count >= max(2, len(member_ids) - 1):
                slots.append(
                    {
                        "label": f"{day.strftime('%a')} {starts_at.strftime('%I:%M %p').lstrip('0')}–{ends_at.strftime('%I:%M %p').lstrip('0')}",
                        "starts_at": starts_at,
                        "ends_at": ends_at,
                        "available_count": available_count,
                        "member_count": len(member_ids),
                    }
                )
    slots.sort(key=lambda item: (item["starts_at"], -item["available_count"]))
    return slots[:4]


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if request.method == "GET":
        form.show_email.data = current_user.show_email

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.uwa_id = form.uwa_id.data
        current_user.program = form.program.data or ""
        current_user.year_level = form.year_level.data
        current_user.bio = form.bio.data or ""
        current_user.skills = form.skills.data or ""
        current_user.study_goal = form.study_goal.data or ""
        current_user.availability = form.availability.data or ""
        current_user.preferred_contact = form.preferred_contact.data or "StudySync Messenger"
        current_user.avatar_color = form.avatar_color.data
        current_user.show_email = bool(form.show_email.data)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("main.profile"))

    membership = GroupMember.query.filter_by(user_id=current_user.id).first()
    stats = student_profile_stats(current_user)
    assigned_tasks = ProjectTask.query.filter_by(assigned_to_id=current_user.id).order_by(ProjectTask.due_date.asc()).all()
    courses = Course.query.filter_by(owner_id=current_user.id).order_by(Course.code.asc()).limit(8).all()
    return render_template("pages/profile.html", form=form, membership=membership, stats=stats, assigned_tasks=assigned_tasks, courses=courses)


@main_bp.route("/students")
@login_required
def students():
    membership = GroupMember.query.filter_by(user_id=current_user.id).first()
    if not membership:
        return render_template("pages/students.html", group=None, members=[])

    group = db.session.get(Group, membership.group_id)
    if not group:
        abort(404)
    members = GroupMember.query.filter_by(group_id=group.id).join(GroupMember.user).order_by(GroupMember.id.asc()).all()
    member_stats = {member.user_id: student_profile_stats(member.user) for member in members}
    return render_template("pages/students.html", group=group, members=members, member_stats=member_stats)


@main_bp.route("/students/<int:user_id>")
@login_required
def student_profile(user_id: int):
    member = same_group_member_or_404(user_id)
    student = member.user
    stats = student_profile_stats(student)
    tasks = ProjectTask.query.filter_by(assigned_to_id=student.id).order_by(ProjectTask.due_date.asc()).all()
    courses = Course.query.filter_by(owner_id=student.id).order_by(Course.code.asc()).limit(8).all()
    return render_template("pages/student_profile.html", student=student, member=member, stats=stats, tasks=tasks, courses=courses)


@main_bp.route("/timetable")
@login_required
def timetable():
    week_reference = parse_week_reference()
    start, end = week_bounds(week_reference)
    events = Event.query.filter(
        Event.owner_id == current_user.id,
        Event.starts_at >= start,
        Event.starts_at < end,
    ).order_by(Event.starts_at.asc()).all()
    days = [start + timedelta(days=i) for i in range(5)]

    visible_start_hour = WORKDAY_START_HOUR
    visible_end_hour = WORKDAY_END_HOUR
    slot_minutes = 15
    slots_per_hour = 60 // slot_minutes
    hours = list(range(visible_start_hour, visible_end_hour))
    total_slots = (visible_end_hour - visible_start_hour) * slots_per_hour
    default_start = start.replace(hour=9, minute=0)
    if default_start < utcnow():
        default_start = (utcnow() + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    default_end = default_start + timedelta(hours=1)
    week_label = f"{start.day} – {(end - timedelta(days=1)).day} {start.strftime('%B %Y')}"

    return render_template(
        "pages/timetable.html",
        events=events,
        days=days,
        hours=hours,
        form=EventForm(),
        visible_start_hour=visible_start_hour,
        visible_end_hour=visible_end_hour,
        slot_minutes=slot_minutes,
        slots_per_hour=slots_per_hour,
        total_slots=total_slots,
        week_label=week_label,
        prev_week=(start - timedelta(days=7)).date().isoformat(),
        next_week=(start + timedelta(days=7)).date().isoformat(),
        today=utcnow().date(),
        default_start_value=datetime_local_value(default_start),
        default_end_value=datetime_local_value(default_end),
    )


@main_bp.route("/exams")
@login_required
def exams():
    exams = Exam.query.filter_by(owner_id=current_user.id).order_by(Exam.starts_at.asc()).all()
    handbook_subjects = HandbookSubject.query.order_by(HandbookSubject.code.asc()).limit(200).all()
    return render_template("pages/exams.html", exams=exams, form=ExamForm(), handbook_subjects=handbook_subjects)


@main_bp.route("/exams/<int:exam_id>")
@login_required
def exam_detail(exam_id: int):
    exam = Exam.query.filter_by(id=exam_id, owner_id=current_user.id).first_or_404()
    progress_by_area = defaultdict(list)
    for topic in exam.topics:
        progress_by_area[topic.area].append(topic)
    return render_template(
        "pages/exam_detail.html",
        exam=exam,
        progress_by_area=progress_by_area,
        topic_form=TopicForm(),
        resource_form=ResourceForm(),
    )


@main_bp.route("/ai-planner")
@login_required
def ai_planner():
    exam = Exam.query.filter_by(owner_id=current_user.id).order_by(Exam.starts_at.asc()).first()
    messages = current_user.chat_messages[-8:]
    return render_template("pages/ai_planner.html", exam=exam, messages=messages)


@main_bp.route("/group", methods=["GET"])
@login_required
def group():
    membership = GroupMember.query.filter_by(user_id=current_user.id).first()
    if not membership:
        return render_template(
            "pages/group_setup.html",
            create_group_form=CreateGroupForm(),
            join_group_form=JoinGroupForm(),
        )

    group = db.session.get(Group, membership.group_id)
    if not group:
        abort(404)
    week_reference = parse_week_reference()
    week_start, week_end = week_bounds(week_reference)
    selected_raw = (request.args.get("day") or "").strip()
    try:
        selected_day = datetime.fromisoformat(selected_raw) if selected_raw else week_start
    except ValueError:
        selected_day = week_start

    if selected_day < week_start or selected_day >= week_end:
        selected_day = week_start

    day_start = selected_day.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    member_ids = [member.user_id for member in group.memberships]
    group_events = (
        Event.query.filter(
            Event.owner_id.in_(member_ids),
            Event.group_visible.is_(True),
            Event.starts_at >= day_start,
            Event.starts_at < day_end,
        )
        .order_by(Event.starts_at.asc())
        .all()
    )
    days = [week_start + timedelta(days=i) for i in range(5)]
    common_free_slots = compute_common_free_slots(group, week_start)
    member_stats = {member.user_id: group_member_stats(member) for member in group.memberships}

    return render_template(
        "pages/group.html",
        group=group,
        task_form=TaskForm(),
        days=days,
        selected_day=selected_day,
        group_events=group_events,
        week_start=week_start,
        week_label=f"{week_start.day} – {(week_end - timedelta(days=1)).day} {week_start.strftime('%B %Y')}",
        prev_week=(week_start - timedelta(days=7)).date().isoformat(),
        next_week=(week_start + timedelta(days=7)).date().isoformat(),
        common_free_slots=common_free_slots,
        member_stats=member_stats,
    )


@main_bp.route("/group/create", methods=["POST"])
@login_required
def create_group():
    if GroupMember.query.filter_by(user_id=current_user.id).first():
        flash("You are already in a group.", "info")
        return redirect(url_for("main.group"))

    form = CreateGroupForm()
    join_form = JoinGroupForm()
    if not form.validate_on_submit():
        return render_template("pages/group_setup.html", create_group_form=form, join_group_form=join_form), 400

    group = Group(name=form.name.data.strip(), code=create_group_code())
    db.session.add(group)
    db.session.flush()
    db.session.add(GroupMember(group_id=group.id, user_id=current_user.id, role="Lead", progress=0, last_seen="Online"))
    db.session.commit()
    flash(f"Group '{group.name}' created. Share code {group.code} with your teammates.", "success")
    return redirect(url_for("main.group"))


@main_bp.route("/group/join", methods=["POST"])
@login_required
def join_group():
    if GroupMember.query.filter_by(user_id=current_user.id).first():
        flash("You are already in a group.", "info")
        return redirect(url_for("main.group"))

    create_form = CreateGroupForm()
    form = JoinGroupForm()
    if not form.validate_on_submit():
        return render_template("pages/group_setup.html", create_group_form=create_form, join_group_form=form), 400

    group = Group.query.filter_by(code=form.code.data.strip().upper()).first()
    if not group:
        form.code.errors.append("That group code was not found.")
        return render_template("pages/group_setup.html", create_group_form=create_form, join_group_form=form), 404

    existing_membership = GroupMember.query.filter_by(group_id=group.id, user_id=current_user.id).first()
    if existing_membership:
        flash("You are already in that group.", "info")
        return redirect(url_for("main.group"))

    membership = GroupMember(group_id=group.id, user_id=current_user.id, role="Member", progress=0, last_seen="Online")
    db.session.add(membership)
    db.session.add(
        GroupMessage(
            group_id=group.id,
            sender_id=current_user.id,
            body=f"{current_user.name} joined the group using the shared invite code.",
        )
    )
    db.session.commit()
    flash(f"You joined {group.name}.", "success")
    return redirect(url_for("main.group"))


@main_bp.route("/messages")
@login_required
def messages():
    membership = GroupMember.query.filter_by(user_id=current_user.id).first()
    if not membership:
        return render_template("pages/messages.html", contacts=[], selected_contact=None, messages=[], unread_counts={}, latest_messages={})

    contacts = [
        group_member.user
        for group_member in GroupMember.query.filter_by(group_id=membership.group_id).join(GroupMember.user).order_by(GroupMember.id.asc()).all()
        if group_member.user_id != current_user.id
    ]

    requested_id = request.args.get("contact", type=int)
    selected_contact = next((contact for contact in contacts if contact.id == requested_id), None)
    if selected_contact is None and contacts:
        selected_contact = contacts[0]

    conversation_messages = []
    if selected_contact:
        conversation_messages = DirectMessage.query.filter(
            ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == selected_contact.id))
            | ((DirectMessage.sender_id == selected_contact.id) & (DirectMessage.receiver_id == current_user.id))
        ).order_by(DirectMessage.created_at.asc()).all()

        DirectMessage.query.filter_by(sender_id=selected_contact.id, receiver_id=current_user.id, is_read=False).update({"is_read": True})
        db.session.commit()

    unread_counts = dict(
        db.session.query(DirectMessage.sender_id, db.func.count(DirectMessage.id))
        .filter(DirectMessage.receiver_id == current_user.id, DirectMessage.is_read.is_(False))
        .group_by(DirectMessage.sender_id)
        .all()
    )

    latest_messages = {}
    for contact in contacts:
        latest_messages[contact.id] = DirectMessage.query.filter(
            ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == contact.id))
            | ((DirectMessage.sender_id == contact.id) & (DirectMessage.receiver_id == current_user.id))
        ).order_by(DirectMessage.created_at.desc()).first()

    return render_template(
        "pages/messages.html",
        contacts=contacts,
        selected_contact=selected_contact,
        messages=conversation_messages,
        unread_counts=unread_counts,
        latest_messages=latest_messages,
    )


@main_bp.route("/group-chat")
@login_required
def group_chat():
    membership = GroupMember.query.filter_by(user_id=current_user.id).first()
    if not membership:
        return render_template("pages/group_chat.html", group=None, members=[], messages=[])

    group = db.session.get(Group, membership.group_id)
    if not group:
        abort(404)
    members = GroupMember.query.filter_by(group_id=group.id).join(GroupMember.user).order_by(GroupMember.id.asc()).all()
    messages = GroupMessage.query.filter_by(group_id=group.id).order_by(GroupMessage.created_at.asc()).limit(120).all()
    return render_template("pages/group_chat.html", group=group, members=members, messages=messages)


@main_bp.route("/courses")
@login_required
def courses():
    courses = Course.query.filter_by(owner_id=current_user.id).order_by(Course.code.asc()).all()
    course_stats = {}
    for course in courses:
        course_stats[course.id] = {
            "events": Event.query.filter_by(owner_id=current_user.id, course_id=course.id).count(),
            "exams": Exam.query.filter_by(owner_id=current_user.id, course_id=course.id).count(),
        }
    event_start, event_end = default_datetime_pair(9, 60)
    exam_start, exam_end = default_datetime_pair(10, 60)
    return render_template(
        "pages/courses.html",
        courses=courses,
        course_stats=course_stats,
        event_form=EventForm(),
        exam_form=ExamForm(),
        handbook_subjects=HandbookSubject.query.order_by(HandbookSubject.code.asc()).limit(200).all(),
        default_start_value=event_start,
        default_end_value=event_end,
        default_exam_start_value=exam_start,
        default_exam_end_value=exam_end,
    )


@main_bp.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id: int):
    course = accessible_course_or_404(course_id)
    upcoming_events = Event.query.filter_by(owner_id=current_user.id, course_id=course.id).order_by(Event.starts_at.asc()).all()
    course_exams = Exam.query.filter_by(owner_id=current_user.id, course_id=course.id).order_by(Exam.starts_at.asc()).all()
    week_value = upcoming_events[0].starts_at.date().isoformat() if upcoming_events else utcnow().date().isoformat()
    event_start, event_end = default_datetime_pair(9, 60)
    exam_start, exam_end = default_datetime_pair(10, 60)
    return render_template(
        "pages/course_detail.html",
        course=course,
        events=upcoming_events,
        exams=course_exams,
        event_form=EventForm(),
        exam_form=ExamForm(),
        handbook_subjects=HandbookSubject.query.order_by(HandbookSubject.code.asc()).limit(200).all(),
        week_value=week_value,
        default_start_value=event_start,
        default_end_value=event_end,
        default_exam_start_value=exam_start,
        default_exam_end_value=exam_end,
    )


@main_bp.route("/reminders")
@login_required
def reminders():
    reminders = Reminder.query.filter_by(owner_id=current_user.id).order_by(Reminder.due_at.asc()).all()
    default_due = datetime_local_value((utcnow() + timedelta(days=1)).replace(second=0, microsecond=0, hour=9, minute=0))
    return render_template("pages/reminders.html", reminders=reminders, form=ReminderForm(), default_due_value=default_due)


@main_bp.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    form = ProfileForm(obj=current_user)
    if request.method == "GET":
        form.show_email.data = current_user.show_email

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.uwa_id = form.uwa_id.data
        current_user.program = form.program.data or ""
        current_user.year_level = form.year_level.data
        current_user.bio = form.bio.data or ""
        current_user.skills = form.skills.data or ""
        current_user.study_goal = form.study_goal.data or ""
        current_user.availability = form.availability.data or ""
        current_user.preferred_contact = form.preferred_contact.data or "StudySync Messenger"
        current_user.avatar_color = form.avatar_color.data
        current_user.show_email = bool(form.show_email.data)
        db.session.commit()
        flash("Preferences saved successfully.", "success")
        return redirect(url_for("main.preferences"))

    stats = student_profile_stats(current_user)
    return render_template("pages/preferences.html", form=form, stats=stats)


@main_bp.route("/handbook")
@login_required
def handbook():
    query_text = (request.args.get("q") or "").strip()
    semester = (request.args.get("semester") or "").strip()
    level = (request.args.get("level") or "").strip()
    school = (request.args.get("school") or "").strip()

    subjects_query = HandbookSubject.query
    if query_text:
        like = f"%{query_text}%"
        subjects_query = subjects_query.filter(
            HandbookSubject.code.ilike(like)
            | HandbookSubject.title.ilike(like)
            | HandbookSubject.coordinator.ilike(like)
            | HandbookSubject.school.ilike(like)
            | HandbookSubject.field_of_education.ilike(like)
        )
    if semester:
        subjects_query = subjects_query.filter(HandbookSubject.availability.ilike(f"%{semester}%"))
    if level:
        subjects_query = subjects_query.filter(HandbookSubject.level_of_study.ilike(f"%{level}%"))
    if school:
        subjects_query = subjects_query.filter(HandbookSubject.school == school)

    subjects = subjects_query.order_by(HandbookSubject.code.asc()).limit(120).all()
    schools = [row[0] for row in db.session.query(HandbookSubject.school).filter(HandbookSubject.school != "").distinct().order_by(HandbookSubject.school.asc()).all()]
    my_course_codes = {course.code for course in Course.query.filter_by(owner_id=current_user.id).all()}
    return render_template(
        "pages/handbook.html",
        subjects=subjects,
        schools=schools,
        query_text=query_text,
        semester=semester,
        level=level,
        school=school,
        my_course_codes=my_course_codes,
    )
