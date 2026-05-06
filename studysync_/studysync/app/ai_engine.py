from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from typing import Iterable

from .models import Course, Event, Exam, GroupMember, ProjectTask, Reminder, RevisionTopic, User


@dataclass
class AIContext:
    user: User
    exams: list[Exam]
    events: list[Event]
    reminders: list[Reminder]
    courses: list[Course]
    group_member: GroupMember | None
    group_tasks: list[ProjectTask]


SYSTEM_PROMPT = """You are StudySync AI, a helpful study assistant inside a UWA student web app.
Use the user's timetable, courses, exams, weak topics, reminders and group project tasks.
Be practical, concise, friendly and structured. Never invent exact official UWA handbook facts.
If you do not know official content, say that the plan is based on the app's stored data.
"""


def build_ai_context(user: User) -> AIContext:
    now = datetime.utcnow()
    exams = (
        Exam.query.filter_by(owner_id=user.id)
        .order_by(Exam.starts_at.asc())
        .limit(8)
        .all()
    )
    events = (
        Event.query.filter(Event.owner_id == user.id, Event.ends_at >= now - timedelta(days=1))
        .order_by(Event.starts_at.asc())
        .limit(30)
        .all()
    )
    reminders = (
        Reminder.query.filter_by(owner_id=user.id, is_done=False)
        .order_by(Reminder.due_at.asc())
        .limit(12)
        .all()
    )
    courses = Course.query.filter((Course.owner_id == user.id) | (Course.owner_id.is_(None))).order_by(Course.code.asc()).limit(20).all()
    group_member = GroupMember.query.filter_by(user_id=user.id).first()
    group_tasks: list[ProjectTask] = []
    if group_member:
        group_tasks = (
            ProjectTask.query.filter_by(group_id=group_member.group_id)
            .order_by(ProjectTask.due_date.asc().nullslast(), ProjectTask.id.asc())
            .limit(20)
            .all()
        )
    return AIContext(user=user, exams=exams, events=events, reminders=reminders, courses=courses, group_member=group_member, group_tasks=group_tasks)


def build_study_reply(context: AIContext, message: str) -> str:
    """Return a useful AI-style response.

    The project now supports three modes:
    1. AI_PROVIDER=ollama for a local Ollama model.
    2. AI_PROVIDER=openai_compatible for LM Studio/OpenAI-compatible local server.
    3. Built-in contextual rule engine fallback so the feature works without API keys.
    """
    provider = os.getenv("AI_PROVIDER", "local").strip().lower()
    if provider == "ollama":
        external = try_ollama_reply(context, message)
        if external:
            return external
    if provider in {"openai_compatible", "lmstudio", "lm_studio"}:
        external = try_openai_compatible_reply(context, message)
        if external:
            return external
    return local_contextual_reply(context, message)


def local_contextual_reply(context: AIContext, message: str) -> str:
    msg = normalise(message)

    if any(word in msg for word in ["hello", "hi", "hey", "help"]):
        return intro_reply(context)
    if contains_any(msg, ["likely exam", "exam topic", "topics", "what are my topics", "what to study"]):
        return likely_topics_reply(context)
    if contains_any(msg, ["practice", "question", "quiz", "test me", "mcq"]):
        return practice_question_reply(context, message)
    if contains_any(msg, ["sqlalchemy", "relationship", "foreign key", "database", "model"]):
        return sqlalchemy_reply(context)
    if contains_any(msg, ["reschedule", "study plan", "revision plan", "plan", "timetable", "free slot", "schedule"]):
        return study_plan_reply(context)
    if contains_any(msg, ["today", "now", "tonight", "next", "urgent"]):
        return today_reply(context)
    if contains_any(msg, ["progress", "weak", "behind", "done", "complete"]):
        return progress_reply(context)
    if contains_any(msg, ["group", "project", "task", "team", "member"]):
        return group_reply(context)
    if contains_any(msg, ["resource", "slide", "lecture", "notes", "read"]):
        return resources_reply(context)
    if contains_any(msg, ["full marks", "demo", "presentation", "rubric"]):
        return demo_reply(context)

    return smart_fallback_reply(context, message)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_any(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def upcoming_exam(context: AIContext) -> Exam | None:
    now = datetime.utcnow()
    future = [exam for exam in context.exams if exam.starts_at >= now]
    return future[0] if future else (context.exams[0] if context.exams else None)


def format_due(dt: datetime) -> str:
    now = datetime.utcnow()
    if dt.date() == now.date():
        return f"today at {dt.strftime('%I:%M %p').lstrip('0')}"
    if dt.date() == (now + timedelta(days=1)).date():
        return f"tomorrow at {dt.strftime('%I:%M %p').lstrip('0')}"
    return dt.strftime("%a %d %b, %I:%M %p").replace(" 0", " ")


def exam_countdown(exam: Exam) -> str:
    delta = exam.starts_at - datetime.utcnow()
    total_minutes = max(0, int(delta.total_seconds() // 60))
    days, minutes = divmod(total_minutes, 1440)
    hours, mins = divmod(minutes, 60)
    if days:
        return f"{days} day(s), {hours} hour(s)"
    if hours:
        return f"{hours} hour(s), {mins} minute(s)"
    return f"{mins} minute(s)"


def topic_priority(topic: RevisionTopic) -> int:
    status_score = {"Not Started": 0, "In Progress": 40, "Done": 100}.get(topic.status, 20)
    confidence = topic.confidence or 0
    return status_score + confidence


def sorted_weak_topics(exam: Exam, limit: int = 6) -> list[RevisionTopic]:
    topics = [topic for topic in exam.topics if topic.status != "Done"]
    return sorted(topics, key=topic_priority)[:limit]


def intro_reply(context: AIContext) -> str:
    exam = upcoming_exam(context)
    lines = ["👋 Hi! I am now using your StudySync database instead of giving one fixed/default reply.", ""]
    if exam:
        lines.append(f"Your next exam is **{exam.title}** in {exam_countdown(exam)}. Current topic progress: {exam.progress}%.")
    if context.reminders:
        lines.append(f"You also have {len(context.reminders)} active reminder(s). The next one is: {context.reminders[0].title} — {format_due(context.reminders[0].due_at)}.")
    lines.extend([
        "",
        "Try asking:",
        "• Generate a study plan",
        "• What are my weak topics?",
        "• Give me a practice question",
        "• What group tasks are pending?",
    ])
    return "\n".join(lines)


def likely_topics_reply(context: AIContext) -> str:
    exam = upcoming_exam(context)
    if not exam:
        return "I cannot find an exam in your account yet. Add an exam and revision topics first, then I can rank what to study."

    weak = sorted_weak_topics(exam, 8)
    lines = [
        f"📊 Likely priority topics for **{exam.title}**",
        f"Exam time: {format_due(exam.starts_at)} · Countdown: {exam_countdown(exam)} · Weight: {exam.weight}%",
        "",
    ]
    if not exam.topics:
        lines.append("No revision topics are stored for this exam yet. Add topics on the exam detail page first.")
        return "\n".join(lines)
    if weak:
        lines.append("Highest priority based on your stored status/confidence:")
        for i, topic in enumerate(weak, 1):
            lines.append(f"{i}. {topic.title} — {topic.status}, confidence {topic.confidence or 0}%")
    else:
        lines.append("All stored topics are marked Done. Move to practice questions, timed recall, and checking mistakes.")

    done = [topic for topic in exam.topics if topic.status == "Done"]
    lines.extend([
        "",
        f"Summary: {len(done)}/{len(exam.topics)} topics done ({exam.progress}%).",
        "Recommendation: spend 70% of your next session on the first 2 weak topics and 30% on timed practice.",
    ])
    return "\n".join(lines)


def study_plan_reply(context: AIContext) -> str:
    exam = upcoming_exam(context)
    if not exam:
        return "Add an upcoming exam first, then I can generate a study plan around your timetable."

    weak = sorted_weak_topics(exam, 6)
    if not weak:
        weak = list(exam.topics[:4])

    slots = find_free_slots(context.events, days=3)
    lines = [
        f"🧠 STUDY PLAN — Smart revision plan for **{exam.title}**",
        f"Countdown: {exam_countdown(exam)} · Current progress: {exam.progress}%",
        "",
    ]
    if not weak:
        lines.append("No revision topics are saved yet. Add topics first so the plan can be specific.")
        return "\n".join(lines)

    if slots:
        lines.append("Suggested sessions from your free timetable slots:")
        for i, slot in enumerate(slots[:4], 1):
            topic = weak[(i - 1) % len(weak)]
            start, end = slot
            lines.append(f"{i}. {start.strftime('%a %I:%M %p').lstrip('0')}–{end.strftime('%I:%M %p').lstrip('0')}: {topic.title}")
            lines.append("   Method: 25 min active recall + 15 min examples + 10 min self-test.")
    else:
        lines.append("I could not find a clear free slot from the stored timetable, so use this compact plan:")
        for i, topic in enumerate(weak[:4], 1):
            lines.append(f"{i}. {topic.title}: 40 min focused revision + 10 min questions")

    lines.extend([
        "",
        "Rules for this plan:",
        "• Start with Not Started topics before In Progress topics.",
        "• Do not only reread slides; write answers from memory.",
        "• After each session, update the topic status so the AI plan changes next time.",
    ])
    return "\n".join(lines)


def find_free_slots(events: list[Event], days: int = 3) -> list[tuple[datetime, datetime]]:
    now = datetime.utcnow().replace(second=0, microsecond=0)
    search_start = now + timedelta(minutes=30)
    busy = sorted([event for event in events if event.ends_at > search_start], key=lambda event: event.starts_at)
    slots: list[tuple[datetime, datetime]] = []
    for day_offset in range(days):
        day = (search_start + timedelta(days=day_offset)).date()
        cursor = datetime.combine(day, time(hour=9))
        end_of_day = datetime.combine(day, time(hour=21))
        if day == search_start.date():
            cursor = max(cursor, search_start)
        day_events = [event for event in busy if event.starts_at.date() == day]
        for event in day_events:
            if event.starts_at > cursor and int((event.starts_at - cursor).total_seconds() // 60) >= 45:
                slot_end = min(event.starts_at, cursor + timedelta(minutes=90))
                slots.append((cursor, slot_end))
            cursor = max(cursor, event.ends_at + timedelta(minutes=15))
        if end_of_day > cursor and int((end_of_day - cursor).total_seconds() // 60) >= 45:
            slots.append((cursor, min(end_of_day, cursor + timedelta(minutes=90))))
    return slots[:6]


def practice_question_reply(context: AIContext, original_message: str) -> str:
    exam = upcoming_exam(context)
    topic = None
    if exam:
        weak = sorted_weak_topics(exam, 1)
        topic = weak[0] if weak else (exam.topics[0] if exam.topics else None)

    if topic:
        topic_text = topic.title
    else:
        topic_text = "your current weakest topic"

    lower = original_message.lower()
    wants_mcq = any(word in lower for word in ["mcq", "multiple", "option"])

    if wants_mcq:
        return "\n".join([
            f"📝 Practice MCQ based on **{topic_text}**",
            "",
            "Question: Which approach usually gives the strongest exam answer for this topic?",
            "A. Memorise definitions only",
            "B. Explain the concept, apply it to a small example, and mention one limitation",
            "C. Write only code without explanation",
            "D. Skip it because it is difficult",
            "",
            "Answer: B",
            "Explanation: High-scoring answers usually combine definition + application + justification. Now try writing a 5-line answer for this topic from memory.",
        ])

    return "\n".join([
        f"📝 Practice question for **{topic_text}**",
        "",
        "Question:",
        f"Explain {topic_text} in your own words, then give one small example and one common mistake students make.",
        "",
        "Model answer structure:",
        "1. Definition: what it means.",
        "2. Example: show a tiny realistic case from the project or lecture.",
        "3. Mistake: explain what not to do.",
        "4. Fix: state the correct approach.",
        "",
        "After answering, mark this topic In Progress or Done so your progress dashboard updates.",
    ])


def sqlalchemy_reply(context: AIContext) -> str:
    return "\n".join([
        "🔗 SQLAlchemy relationships — quick explanation for your demo",
        "",
        "In this project, each table is represented by a Python class. A foreign key stores the ID of a related row, and `relationship()` lets Flask access the related object easily.",
        "",
        "Example from StudySync:",
        "• User has many Exams.",
        "• Exam belongs to one User.",
        "• Exam has many RevisionTopics.",
        "",
        "How to explain it:",
        "`owner_id` in the Exam table points to `user.id`. This creates the database link. Then `owner = relationship(...)` lets us write `exam.owner.name` in Python/Jinja instead of manually joining tables every time.",
        "",
        "Why it matters: it keeps user data separated, lets us load each student's own exams/topics, and supports persistent data in SQLite.",
    ])


def today_reply(context: AIContext) -> str:
    now = datetime.utcnow()
    today_events = [event for event in context.events if event.starts_at.date() == now.date()]
    today_reminders = [reminder for reminder in context.reminders if reminder.due_at.date() == now.date()]
    exam = upcoming_exam(context)
    lines = ["📅 Today's StudySync plan", ""]

    if today_events:
        lines.append("Timetable:")
        for event in today_events[:5]:
            lines.append(f"• {event.starts_at.strftime('%I:%M %p').lstrip('0')} — {event.title} ({event.event_type})")
    else:
        lines.append("No classes/events are stored for today.")

    if today_reminders:
        lines.append("\nDue today:")
        for reminder in today_reminders[:5]:
            lines.append(f"• {reminder.title} at {reminder.due_at.strftime('%I:%M %p').lstrip('0')}")

    if exam:
        weak = sorted_weak_topics(exam, 2)
        lines.append("\nBest use of free time:")
        if weak:
            for topic in weak:
                lines.append(f"• Revise {topic.title} for 35–45 minutes.")
        else:
            lines.append(f"• Do one timed practice question for {exam.title}.")
    return "\n".join(lines)


def progress_reply(context: AIContext) -> str:
    if not context.exams:
        return "No exams are stored yet, so I cannot calculate revision progress. Add an exam and topics first."
    lines = ["📈 Revision progress summary", ""]
    for exam in context.exams[:5]:
        weak = sorted_weak_topics(exam, 3)
        lines.append(f"**{exam.title}** — {exam.progress}% complete")
        if weak:
            lines.append("Weakest topics: " + ", ".join(f"{topic.title} ({topic.status})" for topic in weak))
        else:
            lines.append("All saved topics are marked Done.")
        lines.append("")
    lines.append("Next action: pick the weakest topic above, study it, then update its status on the exam page.")
    return "\n".join(lines)


def group_reply(context: AIContext) -> str:
    if not context.group_member:
        return "You are not currently linked to a project group in the demo data. Join/create a group first to use group project planning."
    lines = [f"👥 Group project summary — {context.group_member.group.name}", ""]
    if context.group_tasks:
        pending = [task for task in context.group_tasks if task.status != "Done"]
        lines.append(f"Pending tasks: {len(pending)}/{len(context.group_tasks)}")
        for task in pending[:6]:
            assignee = task.assigned_to.name if task.assigned_to else "Unassigned"
            due = task.due_date.strftime("%d %b") if task.due_date else "No due date"
            lines.append(f"• {task.title} — {task.status}, assigned to {assignee}, due {due}")
    else:
        lines.append("No group tasks are saved yet.")
    lines.extend([
        "",
        "Suggestion: use Group Chat for decisions, Messenger for one-to-one messages, and update task status after each merge/commit.",
    ])
    return "\n".join(lines)


def resources_reply(context: AIContext) -> str:
    exam = upcoming_exam(context)
    if not exam:
        return "Add an exam first, then attach resources to that exam. I can then suggest what to read first."
    lines = [f"📚 Resources for **{exam.title}**", ""]
    if exam.resources:
        for resource in exam.resources[:8]:
            lines.append(f"• {resource.title} ({resource.kind}) — {resource.url}")
        lines.append("\nUse resources only after trying active recall first. Read to fix gaps, not as the whole revision method.")
    else:
        lines.append("No resources are attached yet. Add lecture slides, lab links, or notes on the exam detail page.")
    return "\n".join(lines)


def demo_reply(context: AIContext) -> str:
    return "\n".join([
        "🎤 Demo answer for the AI feature",
        "",
        "You can say:",
        "Our AI Planner is connected to the Flask backend. When a user sends a message, JavaScript Fetch/AJAX posts it to `/api/ai/message`. The backend reads the logged-in student's exams, timetable, revision topics, reminders and group tasks from SQLite using SQLAlchemy. It then returns a contextual study response as JSON, and the frontend updates the chat without reloading the page.",
        "",
        "Full-mark points:",
        "• AJAX request/response is working.",
        "• Messages are persisted in ChatMessage table.",
        "• Responses change based on real database data.",
        "• It still works without paid API keys, with optional Ollama/LM Studio support.",
    ])


def smart_fallback_reply(context: AIContext, message: str) -> str:
    exam = upcoming_exam(context)
    lines = ["I understood your question, but I do not have a special template for that exact wording yet.", ""]
    if exam:
        weak = sorted_weak_topics(exam, 3)
        lines.append(f"Based on your stored data, the most useful next step is for **{exam.title}**.")
        if weak:
            lines.append("Focus topics: " + ", ".join(topic.title for topic in weak))
        lines.append(f"Progress: {exam.progress}% · Exam in {exam_countdown(exam)}")
    if context.reminders:
        lines.append(f"Next reminder: {context.reminders[0].title} — {format_due(context.reminders[0].due_at)}")
    lines.extend([
        "",
        "You can ask me in these formats:",
        "• Generate my study plan",
        "• Give me a practice question",
        "• Show my weak topics",
        "• Summarise group tasks",
    ])
    return "\n".join(lines)


def context_as_text(context: AIContext) -> str:
    exams = []
    for exam in context.exams[:5]:
        exams.append({
            "title": exam.title,
            "starts_at": exam.starts_at.isoformat(),
            "weight": exam.weight,
            "progress": exam.progress,
            "topics": [
                {"title": topic.title, "status": topic.status, "confidence": topic.confidence}
                for topic in exam.topics[:10]
            ],
        })
    events = [
        {"title": event.title, "type": event.event_type, "starts_at": event.starts_at.isoformat(), "ends_at": event.ends_at.isoformat()}
        for event in context.events[:12]
    ]
    reminders = [{"title": reminder.title, "due_at": reminder.due_at.isoformat()} for reminder in context.reminders[:8]]
    tasks = [
        {"title": task.title, "status": task.status, "assignee": task.assigned_to.name if task.assigned_to else "Unassigned"}
        for task in context.group_tasks[:10]
    ]
    return json.dumps({"exams": exams, "events": events, "reminders": reminders, "group_tasks": tasks}, indent=2)


def try_ollama_reply(context: AIContext, message: str) -> str | None:
    url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    prompt = f"{SYSTEM_PROMPT}\n\nSTUDYSYNC DATABASE CONTEXT:\n{context_as_text(context)}\n\nUSER QUESTION:\n{message}\n\nAnswer:"
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            text = (data.get("response") or "").strip()
            return text or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def try_openai_compatible_reply(context: AIContext, message: str) -> str | None:
    base_url = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "http://127.0.0.1:1234/v1")
    model = os.getenv("OPENAI_COMPATIBLE_MODEL", "local-model")
    api_key = os.getenv("OPENAI_COMPATIBLE_API_KEY", "not-needed")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"STUDYSYNC DATABASE CONTEXT:\n{context_as_text(context)}\n\nUSER QUESTION:\n{message}"},
        ],
        "temperature": 0.3,
        "max_tokens": 600,
    }).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return text or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, IndexError):
        return None
